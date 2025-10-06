from common import calculate_mean, calculate_standard_deviation, get_current_timestamp

frequency_history = []
pressure_history = []
oxygen_history = []


def frequency_analyzer(frequency_value):
    frequency_history.append(frequency_value)
    if len(frequency_history) > 30:
        frequency_history.pop(0)
    
    return {
        "type": "frequency",
        "timestamp": get_current_timestamp(),
        "mean": calculate_mean(frequency_history),
        "std_dev": calculate_standard_deviation(frequency_history)
    }


def pressure_analyzer(pressure_list):
    systolic, diastolic = pressure_list
    pressure_history.append([systolic, diastolic])
    if len(pressure_history) > 30:
        pressure_history.pop(0)
    
    systolic_values = [p[0] for p in pressure_history]
    diastolic_values = [p[1] for p in pressure_history]
    
    return {
        "type": "pressure",
        "timestamp": get_current_timestamp(),
        "mean": [calculate_mean(systolic_values), calculate_mean(diastolic_values)],
        "std_dev": [calculate_standard_deviation(systolic_values), calculate_standard_deviation(diastolic_values)]
    }


def oxygen_analyzer(oxygen_value):
    oxygen_history.append(oxygen_value)
    if len(oxygen_history) > 30:
        oxygen_history.pop(0)
    
    return {
        "type": "oxygen",
        "timestamp": get_current_timestamp(),
        "mean": calculate_mean(oxygen_history),
        "std_dev": calculate_standard_deviation(oxygen_history)
    }