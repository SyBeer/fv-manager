import logging

import pytest

from services.calculations import (
    calc_monthly, calc_monthly_netbilling, calc_roi, roi_sensitivity, enrich_readings_sequence,
    calc_ev_savings, _get_rce_price, _period_last_day,
)


def _r(period, prod, sent, taken, price=0.75, **extra):
    return {"period": period, "production_kwh": prod, "sent_to_grid_kwh": sent,
            "taken_from_grid_kwh": taken, "price_per_kwh": price, **extra}


def test_calc_monthly_basic():
    r = calc_monthly(production=500, sent_to_grid=300, taken_from_grid=100, price_per_kwh=0.75)
    assert r["auto_consumption"] == 200       # 500 - 300
    assert r["total_consumed"] == 300         # 200 + 100
    assert r["net_metering_pool"] == 240      # 300 * 0.8
    assert r["savings_kwh"] == 300            # 200 auto + min(240, 100) taken
    assert r["savings_pln"] == 225.0          # 300 * 0.75
    assert r["carry_over_out"] == 140.0       # 240 - 100 = 140


def test_calc_monthly_no_price():
    r = calc_monthly(500, 300, 100, price_per_kwh=None)
    assert r["savings_pln"] is None


def test_calc_roi_not_achieved():
    readings = [
        {"period": "2024.07", "production_kwh": 500, "sent_to_grid_kwh": 300, "taken_from_grid_kwh": 100, "price_per_kwh": 0.75},
        {"period": "2024.08", "production_kwh": 400, "sent_to_grid_kwh": 200, "taken_from_grid_kwh": 200, "price_per_kwh": 0.75},
    ]
    roi = calc_roi(readings, total_investment_pln=10000)
    assert roi["roi_achieved"] is False
    assert roi["total_savings_pln"] > 0
    assert roi["remaining_to_roi"] > 0


def test_calc_roi_achieved():
    readings = [
        {"period": f"2024.{str(m).zfill(2)}", "production_kwh": 1000, "sent_to_grid_kwh": 0,
         "taken_from_grid_kwh": 0, "price_per_kwh": 1.0}
        for m in range(5, 10)
    ]
    roi = calc_roi(readings, total_investment_pln=100)
    assert roi["roi_achieved"] is True
    assert roi["remaining_to_roi"] <= 0


def test_roi_sensitivity():
    readings = [{"period": "2024.07", "production_kwh": 500, "sent_to_grid_kwh": 300, "taken_from_grid_kwh": 100, "price_per_kwh": None}]
    results = roi_sensitivity(readings, 10000, [0.50, 1.00])
    assert len(results) == 2
    assert results[1]["total_savings_pln"] > results[0]["total_savings_pln"]


# ── Fix #4: clamp ujemnej autokonsumpcji ─────────────────────────────────────

def test_calc_monthly_clamps_negative_auto_consumption():
    r = calc_monthly(production=100, sent_to_grid=150, taken_from_grid=50, price_per_kwh=1.0)
    assert r["auto_consumption"] == 0.0
    assert r["total_consumed"] == 50          # 0 auto + 50 taken
    assert r["savings_kwh"] == 50             # min(150 * 0.8, 50)


def test_calc_monthly_netbilling_clamps_negative_auto_consumption():
    r = calc_monthly_netbilling(100, 150, 50, retail_price_per_kwh=1.0, rce_price_per_kwh=0.4)
    assert r["auto_consumption"] == 0.0
    assert r["savings_pln"] == 60.0           # 0 * 1.0 + 150 * 0.4


def test_calc_monthly_carry_over_in_covers_taken():
    r = calc_monthly(production=50, sent_to_grid=0, taken_from_grid=200, carry_over_in=300)
    assert r["savings_kwh"] == 250            # 50 auto + 200 z puli
    assert r["carry_over_out"] == 100         # 300 - 200


# ── Fix #2: cena RCE opublikowana 29-31 dnia miesiąca ────────────────────────

@pytest.mark.parametrize("year, month, expected", [
    (2024, 2, "2024-02-29"),                  # rok przestępny
    (2023, 2, "2023-02-28"),
    (2024, 4, "2024-04-30"),
    (2024, 12, "2024-12-31"),
])
def test_period_last_day(year, month, expected):
    assert _period_last_day(year, month) == expected


def test_rce_price_published_end_of_month_applies_to_that_month():
    prices = [
        {"date": "2024-01-01", "price_per_kwh": 0.40},
        {"date": "2024-01-31", "price_per_kwh": 0.30},
    ]
    assert _get_rce_price("2024.01", prices) == 0.30


def test_rce_price_from_next_month_not_used():
    prices = [
        {"date": "2024-01-01", "price_per_kwh": 0.40},
        {"date": "2024-02-01", "price_per_kwh": 0.30},
    ]
    assert _get_rce_price("2024.01", prices) == 0.40


def test_rce_price_none_when_all_prices_later():
    assert _get_rce_price("2023.12", [{"date": "2024-01-01", "price_per_kwh": 0.40}]) is None


# ── Fix #1: konfigurowalny początek cyklu net-metering ───────────────────────

def test_custom_cycle_start_month_resets_pool():
    readings = [
        _r("2024.08", 500, 500, 0),           # pula 400
        _r("2024.09", 0, 0, 100),             # z puli 100 -> zostaje 300
        _r("2024.10", 0, 0, 100),             # reset w październiku -> 0 oszczędności
    ]
    out = enrich_readings_sequence(readings, cycle_start_month=10)
    assert out[1]["savings_kwh"] == 100
    assert out[1]["carry_over_out"] == 300
    assert out[2]["savings_kwh"] == 0
    assert out[2]["carry_over_out"] == 0


def test_default_cycle_does_not_reset_in_october():
    readings = [_r("2024.08", 500, 500, 0), _r("2024.10", 0, 0, 100)]
    out = enrich_readings_sequence(readings)
    assert out[1]["savings_kwh"] == 100


def test_calc_roi_respects_cycle_start_month():
    readings = [_r("2024.08", 500, 500, 0, price=1.0), _r("2024.10", 0, 0, 100, price=1.0)]
    default = calc_roi(readings, 10000)
    custom = calc_roi(readings, 10000, cycle_start_month=10)
    assert default["total_fv_savings_pln"] == 100.0
    assert custom["total_fv_savings_pln"] == 0.0


# ── Fix #3: oszczędności EV w ROI ────────────────────────────────────────────

def test_calc_roi_includes_ev_savings():
    readings = [_r("2024.07", 0, 0, 0, ev_kwh=100, ev_savings_pln=250.0)]
    roi = calc_roi(readings, 1000)
    assert roi["total_ev_savings_pln"] == 250.0
    assert roi["total_savings_pln"] == 250.0
    assert roi["ev_enrichment_missing"] is None


def test_calc_roi_warns_when_ev_not_enriched(caplog):
    readings = [
        _r("2024.07", 0, 0, 0, ev_kwh=100),               # brak ev_savings_pln
        _r("2024.08", 0, 0, 0, ev_kwh=0),                 # 0 kWh — nie ostrzegamy
    ]
    with caplog.at_level(logging.WARNING, logger="services.calculations"):
        roi = calc_roi(readings, 1000)
    assert roi["ev_enrichment_missing"] == ["2024.07"]
    assert roi["total_ev_savings_pln"] == 0.0
    assert "2024.07" in caplog.text


# ── calc_roi: przypadki brzegowe ─────────────────────────────────────────────

def test_calc_roi_empty_readings():
    roi = calc_roi([], 10000)
    assert roi["months_measured"] == 0
    assert roi["avg_monthly_savings"] == 0
    assert roi["months_to_roi"] == 0
    assert roi["roi_achieved"] is False


def test_calc_roi_months_to_roi():
    readings = [_r("2024.07", 100, 0, 0, price=1.0), _r("2024.08", 100, 0, 0, price=1.0)]
    roi = calc_roi(readings, 1000)
    assert roi["avg_monthly_savings"] == 100.0
    assert roi["remaining_to_roi"] == 800.0
    assert roi["months_to_roi"] == 8


# ── calc_ev_savings ──────────────────────────────────────────────────────────

def test_calc_ev_savings_km_from_efficiency():
    r = calc_ev_savings(ev_kwh=200, price_per_kwh=0.80, efficiency_kwh_per_100km=20,
                        fuel_consumption_l_per_100km=7, fuel_price_per_liter=6.50)
    assert r["km_driven"] == 1000.0           # 200 / 20 * 100
    assert r["liters_saved"] == 70.0          # 1000 / 100 * 7
    assert r["fuel_cost_equivalent"] == 455.0 # 70 * 6.50
    assert r["electricity_cost"] == 160.0     # 200 * 0.80
    assert r["ev_net_savings"] == 295.0


def test_calc_ev_savings_uses_odometer_km_when_given():
    r = calc_ev_savings(ev_kwh=200, price_per_kwh=0.80, efficiency_kwh_per_100km=20,
                        fuel_consumption_l_per_100km=7, fuel_price_per_liter=6.50, km_driven=800)
    assert r["km_driven"] == 800.0
    assert r["fuel_cost_equivalent"] == 364.0 # 8 * 7 * 6.50
    assert r["ev_net_savings"] == 204.0       # 364 - 160


def test_calc_ev_savings_can_be_negative():
    r = calc_ev_savings(ev_kwh=100, price_per_kwh=3.0, efficiency_kwh_per_100km=20,
                        fuel_consumption_l_per_100km=5, fuel_price_per_liter=6.0)
    assert r["ev_net_savings"] == -150.0      # 150 paliwo - 300 prąd
