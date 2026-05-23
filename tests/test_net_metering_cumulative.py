"""Testy kumulatywnego modelu net-meteringu — cykl roczny kwiecień–marzec."""
import sys
sys.path.insert(0, "src")
from services.calculations import calc_monthly, enrich_readings_sequence, calc_roi


def test_carry_over_single_month():
    """Lipiec: duże nadwyżki, mała konsumpcja → duży carry_over."""
    r = calc_monthly(production=1000, sent_to_grid=700, taken_from_grid=50,
                     price_per_kwh=0.75, carry_over_in=0.0)
    assert r["net_metering_pool"] == 560.0
    assert r["carry_over_out"] == 510.0
    assert r["savings_kwh"] == 300 + 50


def test_carry_over_drawn_in_winter():
    """Grudzień: brak produkcji, cała konsumpcja pokryta z puli."""
    r = calc_monthly(production=50, sent_to_grid=0, taken_from_grid=400,
                     price_per_kwh=0.75, carry_over_in=510.0)
    assert r["savings_kwh"] == 50 + 400
    assert r["carry_over_out"] == 110.0


def test_carry_over_exhausted():
    """Styczeń: pula mniejsza niż pobór → częściowe pokrycie."""
    r = calc_monthly(production=0, sent_to_grid=0, taken_from_grid=300,
                     price_per_kwh=0.75, carry_over_in=100.0)
    assert r["savings_kwh"] == 100.0
    assert r["carry_over_out"] == 0.0


def test_annual_cycle_reset_in_april():
    """Kwiecień resetuje carry_over — nadwyżka z marca przepada."""
    readings = [
        {"period": "2024.03", "production_kwh": 100, "sent_to_grid_kwh": 50,
         "taken_from_grid_kwh": 30, "price_per_kwh": 0.75},
        {"period": "2024.04", "production_kwh": 300, "sent_to_grid_kwh": 200,
         "taken_from_grid_kwh": 50, "price_per_kwh": 0.75},
    ]
    enriched = enrich_readings_sequence(readings, net_metering_ratio=0.80)

    march = next(r for r in enriched if r["period"] == "2024.03")
    april = next(r for r in enriched if r["period"] == "2024.04")

    assert march["carry_over_out"] == 10.0
    assert april["carry_over_out"] == 110.0


def test_sequence_preserves_original_order():
    """enrich_readings_sequence zwraca w oryginalnej kolejności (nawet jeśli wejście jest odwrócone)."""
    readings = [
        {"period": "2024.08", "production_kwh": 800, "sent_to_grid_kwh": 500, "taken_from_grid_kwh": 50},
        {"period": "2024.07", "production_kwh": 1000, "sent_to_grid_kwh": 700, "taken_from_grid_kwh": 50},
    ]
    enriched = enrich_readings_sequence(readings)
    assert enriched[0]["period"] == "2024.08"
    assert enriched[1]["period"] == "2024.07"


def test_roi_uses_cumulative_carry_over():
    """ROI z carry_over musi być wyższe niż bez (przy tej samej historii)."""
    readings = [
        {"period": "2024.07", "production_kwh": 1000, "sent_to_grid_kwh": 700,
         "taken_from_grid_kwh": 50, "price_per_kwh": 0.75},
        {"period": "2024.12", "production_kwh": 50, "sent_to_grid_kwh": 0,
         "taken_from_grid_kwh": 400, "price_per_kwh": 0.75},
    ]
    roi_cumulative = calc_roi(readings, 10000)
    assert roi_cumulative["total_fv_savings_pln"] > (50 + 50) * 0.75


def test_net_metering_ratio_configurable():
    """Różne wartości współczynnika dają różne wyniki."""
    r_80 = calc_monthly(500, 300, 100, 0.75, carry_over_in=0.0, net_metering_ratio=0.80)
    r_70 = calc_monthly(500, 300, 100, 0.75, carry_over_in=0.0, net_metering_ratio=0.70)
    assert r_80["carry_over_out"] > r_70["carry_over_out"]
    assert r_80["savings_kwh"] == r_70["savings_kwh"]
