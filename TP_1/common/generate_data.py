import random
from datetime import datetime


def generate_random_number(min_val, max_val):
    return random.randint(min_val, max_val)


def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")