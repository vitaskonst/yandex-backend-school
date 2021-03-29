from src.json_schemas import post_schema, courier_post_schema, courier_patch_schema, order_post_schema
from src.models import db, Courier, Order, time_intervals_to_minutes_array

import os
import json
from http import HTTPStatus

from flask import Flask, request, abort, make_response
from flask_restful import Api, Resource
import jsonschema


app = Flask(__name__)

app.config.from_pyfile(os.path.join(os.path.dirname(app.instance_path), 'config.py'))
db.init_app(app)
api = Api(app)


def add_courier(courier):
    already_exists = True if Courier.query.filter_by(courier_id=courier['courier_id']).first() else False

    if already_exists:
        Courier.query.filter_by(courier_id=courier['courier_id']).delete()

    courier = Courier(
        courier_id=courier['courier_id'],
        courier_type=courier['courier_type'],
        regions=courier['regions'],
        working_hours=time_intervals_to_minutes_array(courier['working_hours']),
    )
    db.session.add(courier)
    db.session.commit()


def get_courier(courier_id):
    courier = Courier.query.filter_by(courier_id=courier_id).first()
    return courier.serialize() if courier else None


def patch_courier(courier_id, patch_info):
    if patch_info:
        if 'working_hours' in patch_info:
            patch_info['working_hours'] = time_intervals_to_minutes_array(patch_info['working_hours'])

        Courier.query.filter_by(courier_id=courier_id).update(patch_info)
        db.session.commit()


def update_assigned_orders(courier_id):
    # TODO:
    #   for all non-delivered orders assigned to this courier
    #       if doesn't fit anymore
    #           reset to NULL assigned_time, courier_id, price_coefficient
    pass


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
    order = Order.query.filter_by(order_id=order_id).first()
    return order.serialize() if order else None


def validate_post_request():
    try:
        jsonschema.validate(request.json, schema=post_schema)
    except jsonschema.exceptions.ValidationError:
        abort(HTTPStatus.BAD_REQUEST)


class CouriersPost(Resource):
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
            except jsonschema.exceptions.ValidationError:
                if 'courier_id' in courier:
                    invalid_ids.append({'id': courier['courier_id']})
                else:
                    invalid_ids.append({'id': None})

        if invalid_ids:
            response_dict = {'validation_error': {'couriers': invalid_ids}}
            abort(make_response(json.dumps(response_dict), HTTPStatus.BAD_REQUEST))

        return {'couriers': valid_ids}, HTTPStatus.CREATED


class CouriersPatch(Resource):
    @staticmethod
    def patch(courier_id):
        if get_courier(courier_id) is None:
            abort(HTTPStatus.NOT_FOUND)

        try:
            jsonschema.validate(request.json, schema=courier_patch_schema)
        except jsonschema.exceptions.ValidationError:
            abort(HTTPStatus.BAD_REQUEST)

        patch_courier(courier_id, patch_info=request.json)
        update_assigned_orders(courier_id)

        return get_courier(courier_id), HTTPStatus.OK


class OrdersPost(Resource):
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
            except jsonschema.exceptions.ValidationError:
                if 'order_id' in order:
                    invalid_ids.append({'id': order['order_id']})
                else:
                    invalid_ids.append({'id': None})

        if invalid_ids:
            response_dict = {'validation_error': {'orders': invalid_ids}}
            abort(make_response(json.dumps(response_dict), HTTPStatus.BAD_REQUEST))

        return {'orders': valid_ids}, HTTPStatus.CREATED


class OrdersAssignPost(Resource):
    @staticmethod
    def post():
        # TODO:
        #   Check if there are assigned but not delivered orders for this courier
        #   if any
        #       return their assign time and list of their ids
        #   else
        #       search all orders which are:
        #           non-assigned
        #           in courier region
        #           intersect delivery time and courier's working hours
        #           <= weight than his load capacity
        #       if no orders found
        #           return empty list
        #       else
        #           set to them assigned_time, courier_id, price_coefficient

        return {}, HTTPStatus.OK


api.add_resource(CouriersPost, '/couriers')
api.add_resource(CouriersPatch, '/couriers/<int:courier_id>')
api.add_resource(OrdersPost, '/orders')
api.add_resource(OrdersAssignPost, '/orders/assign')
