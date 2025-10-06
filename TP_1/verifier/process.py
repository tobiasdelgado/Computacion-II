from multiprocessing import Queue
from verifier import data_block_verifier
from common import add_block_to_chain


def verifier_process(queue: Queue):
    pending_blocks = {}
    blockchain = []

    while True:
        data = queue.get()
        if data is None:
            break

        timestamp = data["timestamp"]
        block_type = data["type"]

        if timestamp not in pending_blocks:
            pending_blocks[timestamp] = {}

        pending_blocks[timestamp][block_type] = data

        if len(pending_blocks[timestamp]) == 3:
            required_types = {"frequency", "pressure", "oxygen"}
            if set(pending_blocks[timestamp].keys()) == required_types:
                complete_data = pending_blocks[timestamp]

                block = data_block_verifier(complete_data)

                current_index = add_block_to_chain(blockchain, block)

                # Info
                alert_text = "⚠️ ALERT" if block["alert"] else "✓ OK"
                print(
                    f"\033[93mBlock #{current_index} - Hash: {block['hash'][:16]}... - {alert_text}\033[0m"
                )

                del pending_blocks[timestamp]
