import requests
import traceback
from http import HTTPStatus

DOMAIN = 'http://0.0.0.0:8080'


# def test_request(request_type, url, request_data, http_code_expected, response_expected):
#     if request_type == 'POST':
#         request = requests.post
#     elif request_type == 'PATCH':
#         request = requests.patch
#     else:
#         raise ValueError('Invalid request type')
#
#     url = DOMAIN + url if url.startswith('/') else url
#
#     response = request(url, json=request_data)
#     assert response.status_code == http_code_expected
#     assert response.json() == response_expected

class Tester:
    def __init__(self):
        self.test_results = []
        self.exceptions = []
        self.connection_failed = False

    def test_couriers_post(self):
        couriers_empty = []
        couriers_all_valid = [
            {'courier_id': 1, 'courier_type': 'foot', 'regions': [1, 12], 'working_hours': ['11:35-14:05', '09:00-11:00']},
            {'courier_id': 2, 'courier_type': 'bike', 'regions': [22], 'working_hours': ['09:00-18:00']},
            {'courier_id': 3, 'courier_type': 'car', 'regions': [12, 22, 23, 33], 'working_hours': []}
        ]
        couriers_some_invalid = [
            # Valid
            {'courier_id': 100, 'courier_type': 'car', 'regions': [6, 15], 'working_hours': ['09:00-18:00']},

            # Missing 1 field
            {'courier_id': 101, 'regions': [6, 15], 'working_hours': ['09:00-18:00']},
            {'courier_id': 102, 'courier_type': 'car', 'working_hours': ['09:00-18:00']},
            {'courier_id': 103, 'courier_type': 'car', 'regions': [6, 15]},
            # Missing 2 fields
            {'courier_id': 104, 'courier_type': 'car'},
            {'courier_id': 105, 'regions': [6]},
            {'courier_id': 106, 'working_hours': ['09:00-18:00']},
            # Missing 3 fields
            {'courier_id': 107},

            # Undocumented field
            {'courier_id': 108, 'courier_type': 'car', 'regions': [6, 15], 'working_hours': ['09:00-18:00'], 'name': 'Bob'},

            # Invalid courier_type
            {'courier_id': 109, 'courier_type': 'scooter', 'regions': [6, 15], 'working_hours': ['09:00-18:00']},
            # Invalid regions
            {'courier_id': 110, 'courier_type': 'car', 'regions': ['6', 15], 'working_hours': ['09:00-18:00']},
            # Invalid working_hours
            {'courier_id': 111, 'courier_type': 'car', 'regions': [6, 15], 'working_hours': 'full day'},
            {'courier_id': 112, 'courier_type': 'car', 'regions': [6, 15], 'working_hours': ['20:00-25:30']},

            # Missing id
            {'courier_type': 'car', 'regions': [6, 15], 'working_hours': ['09:00-18:00']},
        ]

        url = DOMAIN + '/couriers'

        response = requests.post(url, json={'data': couriers_empty})
        assert response.status_code == HTTPStatus.CREATED
        assert response.json() == {'couriers': []}

        response = requests.post(url, json={'data': couriers_all_valid})
        assert response.status_code == HTTPStatus.CREATED
        assert response.json() == {'couriers': [{'id': 1}, {'id': 2}, {'id': 3}]}

        response = requests.post(url, json={'data': couriers_some_invalid})
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json() == {'validation_error': {
            'couriers': [
                {'id': 101}, {'id': 102}, {'id': 103}, {'id': 104}, {'id': 105}, {'id': 106},
                {'id': 107}, {'id': 108}, {'id': 109}, {'id': 110}, {'id': 111}, {'id': 112},
                {'id': None}
            ]
        }}

        # invalid post format
        response = requests.post(url, json={'couriers': couriers_all_valid})
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_couriers_patch(self):
        patch_empty = {}
        patch_courier_type = {'courier_type': 'foot'}
        patch_regions = {'regions': [11, 33, 2]}
        patch_working_hours = {'working_hours': ['00:00-11:59', '12:00-23:59']}
        patch_2_fields = {'regions': [1, 2, 3], 'working_hours': ['00:00-12:34']}
        patch_3_fields = {'courier_type': 'bike', 'regions': [22], 'working_hours': ['09:00-18:00']}
        patch_id = {'id': 546}
        patch_undocumented = {'name': 'Bob'}

        url = DOMAIN + '/couriers/2'

        response = requests.patch(url, json=patch_empty)
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            'courier_id': 2, 'courier_type': 'bike', 'regions': [22], 'working_hours': ['09:00-18:00']
        }

        response = requests.patch(url, json=patch_courier_type)
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            'courier_id': 2, 'courier_type': 'foot', 'regions': [22], 'working_hours': ['09:00-18:00']
        }

        response = requests.patch(url, json=patch_regions)
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            'courier_id': 2, 'courier_type': 'foot', 'regions': [11, 33, 2], 'working_hours': ['09:00-18:00']
        }

        response = requests.patch(url, json=patch_working_hours)
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            'courier_id': 2, 'courier_type': 'foot', 'regions': [11, 33, 2], 'working_hours': ['00:00-11:59', '12:00-23:59']
        }

        response = requests.patch(url, json=patch_2_fields)
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            'courier_id': 2, 'courier_type': 'foot', 'regions': [1, 2, 3], 'working_hours': ['00:00-12:34']
        }

        response = requests.patch(url, json=patch_3_fields)
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            'courier_id': 2, 'courier_type': 'bike', 'regions': [22], 'working_hours': ['09:00-18:00']
        }

        response = requests.patch(url, json=patch_id)
        assert response.status_code == HTTPStatus.BAD_REQUEST

        response = requests.patch(url, json=patch_undocumented)
        assert response.status_code == HTTPStatus.BAD_REQUEST

        invalid_url = DOMAIN + '/couriers/1000'

        response = requests.patch(invalid_url, json=patch_3_fields)
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_orders_post(self):
        orders_empty = []
        orders_all_valid = [
            {'order_id': 1, 'weight': 0.23, 'region': 12, 'delivery_hours': ['09:00-18:00']},
            {'order_id': 2, 'weight': 15, 'region': 1, 'delivery_hours': ['09:00-18:00']},
            {'order_id': 3, 'weight': 0.01, 'region': 22, 'delivery_hours': ['09:00-12:00', '16:00-21:30']},
            {'order_id': 4, 'weight': 50, 'region': 2, 'delivery_hours': ['17:30-19:25']}
        ]
        orders_some_invalid = [
            # Valid
            {'order_id': 100, 'weight': 1.23, 'region': 7, 'delivery_hours': ['09:00-18:00']},

            # Missing 1 field
            {'order_id': 101, 'region': 7, 'delivery_hours': ['09:00-18:00']},
            {'order_id': 102, 'weight': 1.23, 'delivery_hours': ['09:00-18:00']},
            {'order_id': 103, 'weight': 1.23, 'region': 7},
            # Missing 2 fields
            {'order_id': 104, 'weight': 1.23},
            {'order_id': 105, 'region': 7},
            {'order_id': 106, 'delivery_hours': ['09:00-18:00']},
            # Missing 3 fields
            {'order_id': 107},

            # Undocumented field
            {'order_id': 108, 'weight': 1.23, 'region': 7, 'delivery_hours': ['09:00-18:00'], 'address': 'Lenin st., 8'},

            # Invalid weight
            {'order_id': 109, 'weight': '1.23', 'region': 7, 'delivery_hours': ['09:00-18:00']},
            {'order_id': 110, 'weight': 0.123, 'region': 7, 'delivery_hours': ['09:00-18:00']},
            {'order_id': 111, 'weight': -5, 'region': 7, 'delivery_hours': ['09:00-18:00']},
            {'order_id': 112, 'weight': 0, 'region': 7, 'delivery_hours': ['09:00-18:00']},
            {'order_id': 113, 'weight': 100, 'region': 7, 'delivery_hours': ['09:00-18:00']},
            # Invalid region
            {'order_id': 114, 'weight': 1.23, 'region': '7', 'working_hours': ['09:00-18:00']},
            # Invalid delivery_hours
            {'order_id': 115, 'weight': 1.23, 'region': 7, 'delivery_hours': 'any time'},
            {'order_id': 116, 'weight': 1.23, 'region': 7, 'delivery_hours': ['20:00-25:30']},

            # Missing id
            {'weight': 1.23, 'region': 7, 'delivery_hours': ['09:00-18:00']},
        ]

        url = DOMAIN + '/orders'

        response = requests.post(url, json={'data': orders_empty})
        assert response.status_code == HTTPStatus.CREATED
        assert response.json() == {'orders': []}

        response = requests.post(url, json={'data': orders_all_valid})
        assert response.status_code == HTTPStatus.CREATED
        assert response.json() == {'orders': [{'id': 1}, {'id': 2}, {'id': 3}, {'id': 4}]}

        response = requests.post(url, json={'data': orders_some_invalid})
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json() == {'validation_error': {
            'orders': [
                {'id': 101}, {'id': 102}, {'id': 103}, {'id': 104}, {'id': 105}, {'id': 106}, {'id': 107}, {'id': 108},
                {'id': 109}, {'id': 110}, {'id': 111}, {'id': 112}, {'id': 113}, {'id': 114}, {'id': 115}, {'id': 116},
                {'id': None}
            ]
        }}

        # invalid post format
        response = requests.post(url, json={'orders': orders_all_valid})
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_order_assign(self):
        url = DOMAIN + '/orders/assign'

    def make_test(self, tester):
        test_name = ' '.join(tester.__name__.split('_')[1:]).capitalize()
        print('testing', test_name + '...', end='')
        try:
            tester()
            print('success')
            self.test_results.append(True)
        except AssertionError:
            print('fail\n')
            traceback.print_exc()
            self.test_results.append(False)
        except requests.exceptions.ConnectionError:
            print('fail')
            self.connection_failed = True
            self.test_results.append(False)

    def print_stats(self):
        passed = self.test_results.count(True)
        total = len(self.test_results)

        print(f'\nTests passed: {passed}/{total}')

        if self.connection_failed:
            print('\nConnection error occurred. Maybe you forgot to run the server?')

    def test(self):
        self.make_test(self.test_couriers_post)
        self.make_test(self.test_couriers_patch)
        self.make_test(self.test_orders_post)
        self.make_test(self.test_order_assign)

        self.print_stats()


if __name__ == '__main__':
    t = Tester()
    t.test()
