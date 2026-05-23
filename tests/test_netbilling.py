"""Testy silnika kalkulacji net-billing i routingu per-model."""
import sys
sys.path.insert(0, "src")
from services.calculations import (
    calc_monthly_netbilling, _get_billing_model, _get_rce_price,
    enrich_readings_sequence, calc_roi,
)


# ── Routing ──────────────────────────────────────────────────────────────────

BILLING_PERIODS = [
    {"start_date": "2020-04-01", "end_date": "2022-06-30", "model": "net_metering"},
    {"start_date": "2022-07-01", "end_date": None,         "model": "net_billing"},
]


def test_model_routing_net_metering():
    assert _get_billing_model("2022.06", BILLING_PERIODS) == "net_metering"


def test_model_routing_net_billing():
    assert _get_billing_model("2022.07", BILLING_PERIODS) == "net_billing"
    assert _get_billing_model("2024.12", BILLING_PERIODS) == "net_billing"


def test_model_default_when_no_periods():
    assert _get_billing_model("2024.07", []) == "net_metering"


def test_model_default_before_any_period():
    assert _get_billing_model("2019.01", BILLING_PERIODS) == "net_metering"


# ── RCE price lookup ─────────────────────────────────────────────────────────

RCE_PRICES = [
    {"date": "2022-07-01", "price_per_kwh": 0.42},
    {"date": "2023-01-01", "price_per_kwh": 0.38},
    {"date": "2023-07-01", "price_per_kwh": 0.35},
]


def test_rce_lookup_latest_before_period():
    assert _get_rce_price("2023.08", RCE_PRICES) == 0.35


def test_rce_lookup_first_period():
    assert _get_rce_price("2022.07", RCE_PRICES) == 0.42


def test_rce_manual_override():
    assert _get_rce_price("2023.08", RCE_PRICES, sale_price_override=0.50) == 0.50


def test_rce_none_when_no_prices():
    assert _get_rce_price("2024.01", []) is None


# ── calc_monthly_netbilling ───────────────────────────────────────────────────

def test_netbilling_basic():
    r = calc_monthly_netbilling(
        production=500, sent_to_grid=300, taken_from_grid=100,
        retail_price_per_kwh=0.75, rce_price_per_kwh=0.35,
    )
    assert r["auto_consumption"] == 200.0
    assert r["savings_kwh"] == 200.0
    assert r["savings_pln"] == 255.0
    assert r["net_billing_income_pln"] == 105.0
    assert r["carry_over_out"] == 0.0
    assert r["model"] == "net_billing"


def test_netbilling_no_rce_price():
    r = calc_monthly_netbilling(500, 300, 100, 0.75, rce_price_per_kwh=None)
    assert r["savings_pln"] == 150.0
    assert r["net_billing_income_pln"] == 0.0


# ── enrich_readings_sequence z mieszaną historią ─────────────────────────────

def test_mixed_history_sequence():
    readings = [
        {"period": "2022.06", "production_kwh": 800, "sent_to_grid_kwh": 500,
         "taken_from_grid_kwh": 50, "price_per_kwh": 0.75},
        {"period": "2022.07", "production_kwh": 900, "sent_to_grid_kwh": 600,
         "taken_from_grid_kwh": 30, "price_per_kwh": 0.75},
        {"period": "2022.08", "production_kwh": 800, "sent_to_grid_kwh": 500,
         "taken_from_grid_kwh": 50, "price_per_kwh": 0.75},
    ]
    enriched = enrich_readings_sequence(
        readings, net_metering_ratio=0.80,
        billing_periods=BILLING_PERIODS, rce_prices=RCE_PRICES,
    )

    june = next(r for r in enriched if r["period"] == "2022.06")
    july = next(r for r in enriched if r["period"] == "2022.07")

    assert june.get("model") == "net_metering"
    assert july["model"] == "net_billing"

    assert july["carry_over_out"] == 0.0

    aug = next(r for r in enriched if r["period"] == "2022.08")
    assert aug["carry_over_out"] == 0.0


def test_carry_over_does_not_cross_into_netbilling():
    """Pula z net-metering nie może być użyta w miesiącu net-billing."""
    readings = [
        {"period": "2022.06", "production_kwh": 1000, "sent_to_grid_kwh": 600,
         "taken_from_grid_kwh": 10, "price_per_kwh": 0.75},
        {"period": "2022.07", "production_kwh": 50, "sent_to_grid_kwh": 0,
         "taken_from_grid_kwh": 300, "price_per_kwh": 0.75},
    ]
    enriched = enrich_readings_sequence(
        readings, billing_periods=BILLING_PERIODS, rce_prices=RCE_PRICES,
    )
    july = next(r for r in enriched if r["period"] == "2022.07")
    assert july["savings_kwh"] == 50.0


# ── calc_roi z mieszaną historią ─────────────────────────────────────────────

def test_roi_mixed_models():
    readings = [
        {"period": "2022.05", "production_kwh": 800, "sent_to_grid_kwh": 500,
         "taken_from_grid_kwh": 50, "price_per_kwh": 0.75},
        {"period": "2022.08", "production_kwh": 900, "sent_to_grid_kwh": 600,
         "taken_from_grid_kwh": 30, "price_per_kwh": 0.75},
    ]
    roi = calc_roi(readings, 10000, billing_periods=BILLING_PERIODS, rce_prices=RCE_PRICES)
    assert roi["total_fv_savings_pln"] > 0
    assert roi["roi_achieved"] is False
    assert roi["months_measured"] == 2
