def trend(values):
    if len(values) < 2:
        return {
            "trend": "flat",
            "strength": "none",
            "change_percent": 0.0
        }

    start, end = values[0], values[-1]

    if start == 0:
        pct = None
    else:
        pct = ((end - start) / abs(start)) * 100

    direction = (
        "upward" if end > start else
        "downward" if end < start else
        "flat"
    )

    strength = (
        "strong" if pct and abs(pct) > 50 else
        "moderate" if pct and abs(pct) > 20 else
        "weak"
    )

    return {
        "trend": direction,
        "strength": strength,
        "change_percent": round(pct, 2) if pct is not None else None
    }
