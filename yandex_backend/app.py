from yandex_backend.json_schemas import post_schema, courier_post_schema, courier_patch_schema, order_post_schema

import os
import json
from http import HTTPStatus

from flask import Flask, request, abort, make_response
from flask_restful import Api, Resource
import jsonschema


app = Flask(__name__)
app.config.from_pyfile(os.path.join(os.path.dirname(app.instance_path), os.environ['APP_CONFIG_FILE']))
api = Api(app)

DATABASE = {'couriers': {}, 'orders': {}}


def add_courier(courier):
    courier_id = courier['courier_id']
    DATABASE['couriers'][courier_id] = courier


def get_courier(courier_id):
    return DATABASE['couriers'][courier_id] if courier_id in DATABASE['couriers'] else None


def patch_courier(courier_id, patch_info):
    for parameter in ['courier_type', 'regions', 'working_hours']:
        if parameter in patch_info:
            DATABASE['couriers'][courier_id][parameter] = patch_info[parameter]


def add_order(order):
    order_id = order['order_id']
    DATABASE['orders'][order_id] = order


def get_order(order_id):
    return DATABASE['orders'][order_id] if order_id in DATABASE['orders'] else None


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


api.add_resource(CouriersPost, '/couriers')
api.add_resource(CouriersPatch, '/couriers/<int:courier_id>')
api.add_resource(OrdersPost, '/orders')
