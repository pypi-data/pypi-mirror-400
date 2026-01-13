from hmcalc import change

def test_increase():
    r = change(100, 125)
    assert r["direction"] == "increase"
    assert r["percent"] == 25.0

def test_zero_old():
    r = change(0, 50)
    assert r["percent"] is None
