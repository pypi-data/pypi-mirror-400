def percent(part, whole, precision=2, on_zero=None):
    """
    on_zero:
        None -> return None
        0    -> return 0.0
        'error' -> raise ZeroDivisionError
    """
    if whole == 0:
        if on_zero == "error":
            raise ZeroDivisionError("Whole cannot be zero")
        return on_zero

    return round((part / whole) * 100, precision)
