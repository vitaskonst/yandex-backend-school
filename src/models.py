from src.business import COURIER_TYPES

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ENUM, ARRAY


db = SQLAlchemy()

courier_type_enum = ENUM(*COURIER_TYPES, name='courier_type')


def time_intervals_to_minutes_array(time_intervals):
    minutes_array = []
    for time_interval in time_intervals:
        start_time, end_time = (time_interval.split('-'))
        start_minutes = int(start_time.split(':')[0]) * 60 + int(start_time.split(':')[1])
        end_minutes = int(end_time.split(':')[0]) * 60 + int(end_time.split(':')[1])
        minutes_array.append([start_minutes, end_minutes])
    return minutes_array


def minutes_array_to_time_intervals(minutes_array):
    time_intervals = []
    for period in minutes_array:
        start_time = str(period[0] // 60).zfill(2) + ':' + str(period[0] % 60).zfill(2)
        end_time = str(period[1] // 60).zfill(2) + ':' + str(period[1] % 60).zfill(2)
        time_intervals.append(f'{start_time}-{end_time}')
    return time_intervals


def datetime_to_rfc_3339(datetime):
    return datetime


class Courier(db.Model):
    __tablename__ = 'couriers'

    courier_id = db.Column(db.Integer, primary_key=True)
    courier_type = db.Column(courier_type_enum)
    regions = db.Column(ARRAY(db.Integer))
    working_hours = db.Column(ARRAY(db.Integer))
    assigned_orders = db.relationship('Order', backref='courier', lazy='dynamic')

    def __init__(self, courier_id, courier_type, regions, working_hours):
        self.courier_id = courier_id
        self.courier_type = courier_type
        self.regions = regions
        self.working_hours = working_hours

    def __repr__(self):
        return '<id {}>'.format(self.courier_id)

    def serialize(self):
        return {
            'courier_id': self.courier_id,
            'courier_type': self.courier_type,
            'regions': self.regions,
            'working_hours': minutes_array_to_time_intervals(self.working_hours)
        }


class Order(db.Model):
    __tablename__ = 'orders'

    order_id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float)
    region = db.Column(db.Integer)
    delivery_hours = db.Column(ARRAY(db.Integer))

    courier_id = db.Column(db.Integer, db.ForeignKey('couriers.courier_id'))
    courier_type = db.Column(courier_type_enum)
    assigned_time = db.Column(db.DateTime(timezone=True))
    delivery_time = db.Column(db.Integer)

    def __init__(self, order_id, weight, region, delivery_hours):
        self.order_id = order_id
        self.weight = weight
        self.region = region
        self.delivery_hours = delivery_hours

    def __repr__(self):
        return '<id {}>'.format(self.order_id)

    def get_full_info(self):
        return {
            'order_id': self.order_id,
            'weight': self.weight,
            'region': self.region,
            'delivery_hours': minutes_array_to_time_intervals(self.delivery_hours),
            'courier_id': self.courier_id,
            'courier_type': self.courier_type,
            'assigned_time': datetime_to_rfc_3339(self.assigned_time),
            'delivery_time': self.delivery_time
        }

    def serialize(self):
        return {
            'order_id': self.order_id,
            'weight': self.weight,
            'region': self.region,
            'delivery_hours': minutes_array_to_time_intervals(self.delivery_hours)
        }
