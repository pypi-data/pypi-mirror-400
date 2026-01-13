def compare(a, b, tolerance_percent=5, precision=2):
    diff = a - b

    if b == 0:
        pct_diff = None
    else:
        pct_diff = (diff / abs(b)) * 100

    close = (
        abs(pct_diff) <= tolerance_percent
        if pct_diff is not None
        else False
    )

    return {
        "difference": diff,
        "percent_diff": round(pct_diff, precision) if pct_diff is not None else None,
        "close": close
    }
