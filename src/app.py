from src.models import db
from src.url_handlers import Couriers, CouriersId, Orders, OrdersAssign, OrdersComplete

import os

from flask import Flask
from flask_restful import Api


app = Flask(__name__)

app.config.from_pyfile(os.path.join(os.path.dirname(app.instance_path), 'config.py'))
db.init_app(app)
api = Api(app)


api.add_resource(Couriers, '/couriers')
api.add_resource(CouriersId, '/couriers/<int:courier_id>')
api.add_resource(Orders, '/orders')
api.add_resource(OrdersAssign, '/orders/assign')
api.add_resource(OrdersComplete, '/orders/complete')
