from src.business_data import COURIER_TYPES, MIN_WEIGHT, MAX_WEIGHT

HH_MM_REGEX = '([0-1][0-9]|2[0-3]):[0-5][0-9]'
TIME_INTERVAL_REGEX = f'^{HH_MM_REGEX}-{HH_MM_REGEX}$'

HH_MM_SS_REGEX = f'{HH_MM_REGEX}:[0-5][0-9]'
YYYY_MM_DD_REGEX = '[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])'
TIMESTAMP_REGEX = f'^{YYYY_MM_DD_REGEX}T{HH_MM_SS_REGEX}.[0-9]{{2,6}}Z$'


positive_integer = {
    'type': 'integer',
    'exclusiveMinimum': 0
}

post_schema = {
    'type': 'object',
    'properties': {
        'data': {'type': 'array'}
    },
    'required': ['data'],
    'additionalProperties': False
}

courier_post_schema = {
    'type': 'object',
    'properties': {
        'courier_id': positive_integer,
        'courier_type': {
            'type': 'string',
            'enum': COURIER_TYPES
        },
        'regions': {
            'type': 'array',
            'items': positive_integer
        },
        'working_hours': {
            'type': 'array',
            'items': {
                'type': 'string',
                'pattern': TIME_INTERVAL_REGEX
            }
        }
    },
    'required': ['courier_id', 'courier_type', 'regions', 'working_hours'],
    'additionalProperties': False
}

courier_patch_schema = {
    'type': 'object',
    'properties': {
        'courier_type': {
            'type': 'string',
            'enum': COURIER_TYPES
        },
        'regions': {
            'type': 'array',
            'items': positive_integer
        },
        'working_hours': {
            'type': 'array',
            'items': {
                'type': 'string',
                'pattern': TIME_INTERVAL_REGEX
            }
        }
    },
    'additionalProperties': False,
}

order_post_schema = {
    'type': 'object',
    'properties': {
        'order_id': positive_integer,
        'weight': {
            'type': 'number',
            'multipleOf': 0.01,
            'minimum': MIN_WEIGHT,
            'maximum': MAX_WEIGHT
        },
        'region': positive_integer,
        'delivery_hours': {
            'type': 'array',
            'items': {
                'type': 'string',
                'pattern': TIME_INTERVAL_REGEX
            }
        }
    },
    'required': ['order_id', 'weight', 'region', 'delivery_hours'],
    'additionalProperties': False
}

order_complete_schema = {
    'type': 'object',
    'properties': {
        'courier_id': positive_integer,
        'order_id': positive_integer,
        'complete_time': {
            'type': 'string',
            'pattern': TIMESTAMP_REGEX
        }
    },
    'required': ['courier_id', 'order_id', 'complete_time'],
    'additionalProperties': False
}
