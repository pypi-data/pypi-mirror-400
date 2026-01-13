import math

def round_human(value, sig=3):
    if value == 0:
        return 0

    return round(
        value,
        sig - int(math.floor(math.log10(abs(value)))) - 1
    )
