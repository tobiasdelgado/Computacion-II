from common import calculate_block_hash

previous_hash = "0"


def data_block_verifier(complete_data):
    global previous_hash

    timestamp = complete_data["frequency"]["timestamp"]

    # Data
    frequency_data = {
        "mean": complete_data["frequency"]["mean"],
        "std_dev": complete_data["frequency"]["std_dev"],
    }
    pressure_data = {
        "mean": complete_data["pressure"]["mean"],
        "std_dev": complete_data["pressure"]["std_dev"],
    }
    oxygen_data = {
        "mean": complete_data["oxygen"]["mean"],
        "std_dev": complete_data["oxygen"]["std_dev"],
    }

    data = {
        "frequency": frequency_data,
        "pressure": pressure_data,
        "oxygen": oxygen_data,
    }

    # Alert
    alert = False
    if complete_data["frequency"]["mean"] >= 200:
        alert = True
    if complete_data["oxygen"]["mean"] < 90 or complete_data["oxygen"]["mean"] > 100:
        alert = True
    if complete_data["pressure"]["mean"][0] >= 200:  # Systolic pressure
        alert = True

    current_hash = calculate_block_hash(previous_hash, data, timestamp)

    block = {
        "timestamp": timestamp,
        "data": data,
        "alert": alert,
        "prev_hash": previous_hash,
        "hash": current_hash,
    }

    # Update previous hash
    previous_hash = current_hash

    return block
