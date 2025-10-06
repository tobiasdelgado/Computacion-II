import hashlib


def calculate_block_hash(previous_hash, data, timestamp):
    hash_input = previous_hash + str(data) + timestamp
    return hashlib.sha256(hash_input.encode()).hexdigest()
