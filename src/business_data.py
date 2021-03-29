COURIER_TYPES = ['foot', 'bike', 'car']

MIN_WEIGHT = 0.01
MAX_WEIGHT = 50

MAX_LOAD_CAPACITY = {
    'foot': 10,
    'bike': 15,
    'car': 50
}

EARNINGS_COEFFICIENTS = {
    'foot': 2,
    'bike': 5,
    'car': 9
}


def calculate_rating(delivered_orders):
    delivery_times = {}
    for order in delivered_orders:
        if order['region'] in delivery_times:
            delivery_times[order['region']].append(order['delivery_time'])
        else:
            delivery_times[order['region']] = [order['delivery_time']]

    t = min([sum(times) // len(times) for times in delivery_times.values()])

    return (60 * 60 - min(t, 60 * 60)) / (60 * 60) * 5


def calculate_earnings(delivered_orders):
    return sum([500 * EARNINGS_COEFFICIENTS[order['assigned_courier_type']] for order in delivered_orders])

