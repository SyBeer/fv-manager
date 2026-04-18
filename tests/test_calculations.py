from services.calculations import calc_monthly, calc_roi, roi_sensitivity


def test_calc_monthly_basic():
    r = calc_monthly(production=500, sent_to_grid=300, taken_from_grid=100, price_per_kwh=0.75)
    assert r["auto_consumption"] == 200       # 500 - 300
    assert r["total_consumed"] == 300         # 200 + 100
    assert r["net_metering_pool"] == 240      # 300 * 0.8
    assert r["savings_kwh"] == 300            # 200 auto + min(240, 100) taken
    assert r["savings_pln"] == 225.0          # 300 * 0.75


def test_calc_monthly_no_price():
    r = calc_monthly(500, 300, 100, price_per_kwh=None)
    assert r["savings_pln"] is None


def test_calc_roi_not_achieved():
    readings = [
        {"production_kwh": 500, "sent_to_grid_kwh": 300, "taken_from_grid_kwh": 100, "price_per_kwh": 0.75},
        {"production_kwh": 400, "sent_to_grid_kwh": 200, "taken_from_grid_kwh": 200, "price_per_kwh": 0.75},
    ]
    roi = calc_roi(readings, total_investment_pln=10000)
    assert roi["roi_achieved"] is False
    assert roi["total_savings_pln"] > 0
    assert roi["remaining_to_roi"] > 0


def test_calc_roi_achieved():
    readings = [{"production_kwh": 1000, "sent_to_grid_kwh": 0, "taken_from_grid_kwh": 0, "price_per_kwh": 1.0}] * 5
    roi = calc_roi(readings, total_investment_pln=100)
    assert roi["roi_achieved"] is True
    assert roi["remaining_to_roi"] <= 0


def test_roi_sensitivity():
    readings = [{"production_kwh": 500, "sent_to_grid_kwh": 300, "taken_from_grid_kwh": 100, "price_per_kwh": None}]
    results = roi_sensitivity(readings, 10000, [0.50, 1.00])
    assert len(results) == 2
    assert results[1]["total_savings_pln"] > results[0]["total_savings_pln"]
