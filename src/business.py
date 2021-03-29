max_weight = {
    'foot': 10,
    'bike': 15,
    'car': 50
}

earnings_coefficient = {
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

