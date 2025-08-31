from common import generate_random_number, get_current_timestamp


def generate_raw_data_block():
    return {
        "timestamp": get_current_timestamp(),
        "frequency": generate_random_number(60, 180),
        "pressure": [generate_random_number(110, 180), generate_random_number(70, 110)],
        "oxygen": generate_random_number(90, 100),
    }
