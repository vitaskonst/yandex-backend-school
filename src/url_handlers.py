from src.json_schemas import post_schema, courier_post_schema, courier_patch_schema,\
    order_post_schema, order_complete_schema
from src.models import db, Courier, Order, time_intervals_to_minutes_array
from src.business_data import MAX_LOAD_CAPACITY, calculate_rating, calculate_earnings

import json
import itertools
from http import HTTPStatus

from flask import request, abort, make_response
from flask_restful import Resource
from sqlalchemy import and_
from datetime import datetime
import dateutil.parser
from dateutil.relativedelta import relativedelta
import jsonschema


def abort_json(message, status_code):
    abort(make_response(json.dumps({'details': message}), status_code))


def add_courier(courier):
    already_exists = True if Courier.query.filter_by(courier_id=courier['courier_id']).first() else False

    if already_exists:
        old_courier = Courier.query.filter_by(courier_id=courier['courier_id']).first()
        db.session.delete(old_courier)

    courier = Courier(
        courier_id=courier['courier_id'],
        courier_type=courier['courier_type'],
        regions=courier['regions'],
        working_hours=time_intervals_to_minutes_array(courier['working_hours']),
    )
    db.session.add(courier)
    db.session.commit()


def get_courier(courier_id):
    return Courier.query.filter_by(courier_id=courier_id).first()


def patch_courier(courier_id, patch_info):
    if patch_info:
        if 'working_hours' in patch_info:
            patch_info['working_hours'] = time_intervals_to_minutes_array(patch_info['working_hours'])

        Courier.query.filter_by(courier_id=courier_id).update(patch_info)
        db.session.commit()


def time_ranges_intersect(range1, range2):
    return (
        (range1[1] < range1[0] and range2[1] < range2[0]) or
        (range1[0] <= range2[1] and range2[0] <= range1[1]) or
        (range1[1] < range1[0] <= range2[1]) or
        (range2[0] <= range1[1] < range1[0]) or
        (range1[0] <= range2[1] < range2[0]) or
        (range2[1] < range2[0] <= range1[1])
    )


def intersect(minutes_list1, minutes_list2):
    return any([time_ranges_intersect(period1, period2)
                for period1, period2 in itertools.product(minutes_list1, minutes_list2)])


def fits_assigned_courier(order):
    return order.weight <= MAX_LOAD_CAPACITY[order.courier.courier_type] and \
           order.region in order.courier.regions and \
           intersect(order.delivery_hours, order.courier.working_hours)


def get_remaining_orders(courier_id):
    return [order for order in get_courier(courier_id).assigned_orders if order.delivery_time is None]


def get_suitable_orders(courier):
    return [order for order in Order.query.filter(and_(
        Order.assigned_time.is_(None),
        Order.weight <= MAX_LOAD_CAPACITY[courier.courier_type],
        Order.region.in_(courier.regions)
    )) if intersect(order.delivery_hours, courier.working_hours)]


def assign_orders(courier, orders):
    current_time = current_timestamp()
    for order in orders:
        order.courier = courier
        order.assigned_time = current_time
        order.assigned_courier_type = courier.courier_type

    db.session.commit()


def update_assigned_orders(courier_id):
    remaining_orders = get_remaining_orders(courier_id)

    for order in remaining_orders:
        if not fits_assigned_courier(order):
            order.assigned_time = None
            order.courier = None
            order.assigned_courier_type = None

    db.session.commit()


def add_order(order):
    already_exists = True if Order.query.filter_by(order_id=order['order_id']).first() else False

    if already_exists:
        Order.query.filter_by(order_id=order['order_id']).delete()

    order = Order(
        order_id=order['order_id'],
        weight=order['weight'],
        region=order['region'],
        delivery_hours=time_intervals_to_minutes_array(order['delivery_hours']),
    )
    db.session.add(order)
    db.session.commit()


def get_order(order_id):
    return Order.query.filter_by(order_id=order_id).first()


def validate_post_request():
    try:
        jsonschema.validate(request.json, schema=post_schema)
    except jsonschema.exceptions.ValidationError as e:
        abort_json(e.message, HTTPStatus.BAD_REQUEST)


def validate_patch_request():
    try:
        jsonschema.validate(request.json, schema=courier_patch_schema)
    except jsonschema.exceptions.ValidationError as e:
        abort_json(e.message, HTTPStatus.BAD_REQUEST)


def validate_assign_request():
    if 'courier_id' not in request.json or len(request.json) > 1:
        abort_json('Invalid request structure', HTTPStatus.BAD_REQUEST)


def validate_complete_request():
    try:
        jsonschema.validate(request.json, schema=order_complete_schema)
    except jsonschema.exceptions.ValidationError as e:
        abort_json(e.message, HTTPStatus.BAD_REQUEST)


def current_timestamp():
    return datetime.utcnow().isoformat('T')[:-4] + 'Z'


def count_delivery_time(courier, completed_order, complete_time_str):
    complete_time = dateutil.parser.isoparse(complete_time_str)
    completed_orders_from_the_same_batch = [order for order in courier.assigned_orders
                                            if order.assigned_time == completed_order.assigned_time
                                            and order.delivery_time is not None]

    delivery_start = dateutil.parser.isoparse(completed_order.assigned_time)

    if completed_orders_from_the_same_batch:
        delivery_start += relativedelta(seconds=max([order.delivery_time for order in
                                                     completed_orders_from_the_same_batch]))

    return (complete_time - delivery_start).total_seconds()


class Couriers(Resource):
    @staticmethod
    def post():
        validate_post_request()

        invalid_ids = []
        valid_ids = []

        for courier in request.json['data']:
            try:
                jsonschema.validate(courier, schema=courier_post_schema)
                add_courier(courier)
                valid_ids.append({'id': courier['courier_id']})
            except jsonschema.exceptions.ValidationError as e:
                if 'courier_id' in courier:
                    invalid_ids.append({'id': courier['courier_id'], 'details': e.message})
                else:
                    invalid_ids.append({'id': None})

        if invalid_ids:
            response_dict = {'validation_error': {'couriers': invalid_ids}}
            abort(make_response(json.dumps(response_dict), HTTPStatus.BAD_REQUEST))

        return {'couriers': valid_ids}, HTTPStatus.CREATED


class CouriersId(Resource):
    @staticmethod
    def patch(courier_id):
        if get_courier(courier_id) is None:
            abort_json('No courier with provided id found', HTTPStatus.NOT_FOUND)

        validate_patch_request()

        patch_courier(courier_id, patch_info=request.json)
        update_assigned_orders(courier_id)

        return get_courier(courier_id).serialize(), HTTPStatus.OK

    @staticmethod
    def get(courier_id):
        courier = get_courier(courier_id)

        if courier is None:
            abort_json('No courier with provided id found', HTTPStatus.NOT_FOUND)

        courier_info = courier.serialize()

        delivered_orders = Order.query.filter(and_(Order.courier == courier, Order.delivery_time.isnot(None)))

        courier_info['rating'] = calculate_rating([order.get_full_info() for order in delivered_orders])
        courier_info['earnings'] = calculate_earnings([order.get_full_info() for order in delivered_orders])

        return courier_info, HTTPStatus.OK


class Orders(Resource):
    @staticmethod
    def post():
        validate_post_request()

        invalid_ids = []
        valid_ids = []

        for order in request.json['data']:
            try:
                jsonschema.validate(order, schema=order_post_schema)
                add_order(order)
                valid_ids.append({'id': order['order_id']})
            except jsonschema.exceptions.ValidationError as e:
                if 'order_id' in order:
                    invalid_ids.append({'id': order['order_id'], 'details': e.message})
                else:
                    invalid_ids.append({'id': None, 'details': e.message})

        if invalid_ids:
            response_dict = {'validation_error': {'orders': invalid_ids}}
            abort(make_response(json.dumps(response_dict), HTTPStatus.BAD_REQUEST))

        return {'orders': valid_ids}, HTTPStatus.CREATED


class OrdersAssign(Resource):
    @staticmethod
    def post():
        validate_assign_request()

        courier = get_courier(request.json['courier_id'])
        if courier is None:
            abort_json('No courier with provided id found', HTTPStatus.BAD_REQUEST)

        remaining_orders = get_remaining_orders(courier.courier_id)

        if not remaining_orders:
            suitable_orders = get_suitable_orders(courier)

            if suitable_orders:
                assign_orders(courier, suitable_orders)

            remaining_orders = get_remaining_orders(courier.courier_id)

        if not remaining_orders:
            response = {'orders': []}
        else:
            response = {
                'orders': [{'id': order.order_id} for order in remaining_orders],
                'assigned_time': remaining_orders[0].assigned_time
            }

        return response, HTTPStatus.OK


class OrdersComplete(Resource):
    @staticmethod
    def post():
        validate_complete_request()

        courier = get_courier(request.json['courier_id'])
        order = get_order(request.json['order_id'])

        if courier is None:
            abort_json('No courier with provided id found', HTTPStatus.BAD_REQUEST)

        if order is None:
            abort_json('No order with provided id found', HTTPStatus.BAD_REQUEST)

        if order.courier != courier:
            abort_json('This order is not assigned to given courier', HTTPStatus.BAD_REQUEST)

        if order.delivery_time is None:
            delivery_time = count_delivery_time(courier, order, request.json['complete_time'])

            if delivery_time < 0:
                abort_json('Negative delivery time', HTTPStatus.BAD_REQUEST)

            order.delivery_time = delivery_time
            db.session.commit()

        return {'order_id': order.order_id}, HTTPStatus.OK
