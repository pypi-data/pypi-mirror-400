def change(old, new, precision=2):
    diff = new - old

    if old == 0:
        pct = None
    else:
        pct = (diff / abs(old)) * 100

    return {
        "absolute": diff,
        "percent": round(pct, precision) if pct is not None else None,
        "direction": (
            "increase" if diff > 0 else
            "decrease" if diff < 0 else
            "no change"
        )
    }
