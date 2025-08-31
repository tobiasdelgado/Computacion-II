def calculate_mean(values):
    return sum(values) / len(values)


def calculate_standard_deviation(values):
    mean = calculate_mean(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return variance ** 0.5