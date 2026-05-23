"""Testy modulu prognozowania sezonowego."""
import sys
sys.path.insert(0, "src")
from services.forecast import (
    seasonal_averages, get_capacity_stages, get_scale_factor,
    apply_degradation, forecast_months, breakeven_scenarios,
    breakeven_confidence_interval, _next_period,
)


# ── Helpery ───────────────────────────────────────────────────────────────────

def test_next_period_normal():
    assert _next_period("2024.07") == "2024.08"

def test_next_period_year_rollover():
    assert _next_period("2024.12") == "2025.01"


# ── 4.1 Sezonowe srednie ─────────────────────────────────────────────────────

READINGS_2Y = [
    {"period": "2022.07", "production_kwh": 800},
    {"period": "2022.08", "production_kwh": 720},
    {"period": "2022.12", "production_kwh": 80},
    {"period": "2023.07", "production_kwh": 840},
    {"period": "2023.08", "production_kwh": 700},
    {"period": "2023.12", "production_kwh": 100},
]

def test_seasonal_averages_mean():
    avgs = seasonal_averages(READINGS_2Y)
    assert avgs[7]["mean"] == 820.0
    assert avgs[7]["count"] == 2
    assert avgs[12]["mean"] == 90.0

def test_seasonal_averages_std():
    avgs = seasonal_averages(READINGS_2Y)
    assert abs(avgs[7]["std"] - 28.28) < 0.1

def test_seasonal_averages_single_point():
    avgs = seasonal_averages([{"period": "2024.03", "production_kwh": 500}])
    assert avgs[3]["std"] == 0.0
    assert avgs[3]["count"] == 1


# ── 4.2 Etapy rozbudowy ──────────────────────────────────────────────────────

INVESTMENTS = [
    {"date": "2020-04-01", "power_kwp": 5.0, "cost_pln": 20000},
    {"date": "2022-01-01", "power_kwp": 8.0, "cost_pln": 10000},
    {"date": "2022-02-01", "power_kwp": None, "cost_pln": 500},
]

def test_get_capacity_stages_filters_none():
    stages = get_capacity_stages(INVESTMENTS)
    assert len(stages) == 2
    assert stages[0]["kwp"] == 5.0
    assert stages[1]["kwp"] == 8.0

def test_scale_factor_phase_b():
    stages = get_capacity_stages(INVESTMENTS)
    readings = [{"period": "2023.04"}]
    scale, phase = get_scale_factor(readings, stages)
    assert phase == "B"
    assert scale == 1.0

def test_scale_factor_phase_a():
    stages = get_capacity_stages(INVESTMENTS)
    readings = [{"period": "2022.06"}]
    scale, phase = get_scale_factor(readings, stages)
    assert phase == "A"
    assert abs(scale - 8/5) < 0.001

def test_scale_factor_single_stage():
    stages = get_capacity_stages([{"date": "2020-04-01", "power_kwp": 5.0, "cost_pln": 20000}])
    scale, phase = get_scale_factor([{"period": "2024.07"}], stages)
    assert phase == "B"
    assert scale == 1.0


# ── 4.3 Degradacja ───────────────────────────────────────────────────────────

def test_apply_degradation_zero_rate():
    result = apply_degradation(1000, "2020-04-01", "2023.04", annual_rate=0.0)
    assert result == 1000.0

def test_apply_degradation_three_years():
    result = apply_degradation(1000, "2020-04-01", "2023.04", annual_rate=0.006)
    assert abs(result - 982.05) < 0.5

def test_apply_degradation_zero_elapsed():
    result = apply_degradation(1000, "2024-07-01", "2024.07", annual_rate=0.006)
    assert result == 1000.0


# ── 4.4 / 4.5 Break-even scenariusze ─────────────────────────────────────────

FORECAST_SIMPLE = [{"savings_pln_base": 100.0, "period": f"2025.{m:02d}",
                     "production_forecast": 500, "production_mean": 500,
                     "std": 50, "data_points": 2, "capacity_phase": "B",
                     "model": "net_metering", "warning": None}
                   for m in range(1, 25)]

def test_breakeven_zero_growth():
    scenarios = breakeven_scenarios(1000.0, FORECAST_SIMPLE, [0.0], base_price=0.75)
    assert scenarios[0]["months_to_roi"] == 10

def test_breakeven_with_growth():
    # remaining=2000 żeby wzrost cen miał szansę skrócić czas
    scenarios = breakeven_scenarios(2000.0, FORECAST_SIMPLE, [0.0, 0.12], base_price=0.75)
    assert scenarios[1]["months_to_roi"] <= scenarios[0]["months_to_roi"]
    # Przy większym horyzoncie 12% powinno dać faktycznie mniej miesięcy
    scenarios2 = breakeven_scenarios(2200.0, FORECAST_SIMPLE, [0.0, 0.12], base_price=0.75)
    assert scenarios2[1]["months_to_roi"] < scenarios2[0]["months_to_roi"]

def test_breakeven_not_achieved():
    scenarios = breakeven_scenarios(999999.0, FORECAST_SIMPLE, [0.0], base_price=0.75)
    assert scenarios[0]["months_to_roi"] is None

def test_confidence_interval():
    scenarios = breakeven_scenarios(1000.0, FORECAST_SIMPLE,
                                    [0.0, 0.03, 0.07, 0.12], base_price=0.75)
    ci = breakeven_confidence_interval(scenarios)
    assert ci["pessimistic"] is not None
    assert ci["base"] is not None
    assert ci["optimistic"] is not None
    assert ci["pessimistic"] >= ci["base"] >= ci["optimistic"]

def test_forecast_months_basic():
    readings = READINGS_2Y
    investments = [{"date": "2021-04-01", "power_kwp": 5.0, "cost_pln": 20000}]
    result = forecast_months(
        readings, investments, months_ahead=3,
        degradation_rate=0.006, base_price=0.75,
    )
    assert len(result) == 3
    # Ostatni odczyt to 2023.12, więc prognoza: 2024.01, 2024.02, 2024.03
    assert result[0]["period"] == "2024.01"
    assert result[2]["period"] == "2024.03"
    # Sty-Mar nie mają danych historycznych (mamy lip/sie/gru) — warning ustawiony
    assert result[0]["warning"] is not None  # brak danych dla stycznia
    assert result[0]["data_points"] == 0

def test_forecast_months_no_readings():
    result = forecast_months([], [], months_ahead=3, degradation_rate=0.006, base_price=0.75)
    assert result == []
