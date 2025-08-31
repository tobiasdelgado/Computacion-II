import json
import os


def load_blockchain():
    # Get the path to trabajo-practico-1 directory
    base_path = os.path.dirname(os.path.dirname(__file__))
    blockchain_path = os.path.join(base_path, "blockchain.json")
    if os.path.exists(blockchain_path):
        with open(blockchain_path, "r") as f:
            return json.load(f)
    return []


def save_blockchain(blockchain):
    # Get the path to trabajo-practico-1 directory
    base_path = os.path.dirname(os.path.dirname(__file__))
    blockchain_path = os.path.join(base_path, "blockchain.json")
    with open(blockchain_path, "w") as f:
        json.dump(blockchain, f, indent=2)


def clear_blockchain():
    # Get the path to trabajo-practico-1 directory
    base_path = os.path.dirname(os.path.dirname(__file__))
    blockchain_path = os.path.join(base_path, "blockchain.json")
    with open(blockchain_path, "w") as f:
        json.dump([], f)


def add_block_to_chain(blockchain, block):
    blockchain.append(block)
    save_blockchain(blockchain)
    return len(blockchain) - 1