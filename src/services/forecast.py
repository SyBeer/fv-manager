"""Seasonal forecasting and break-even projection for Green Transition Tracker."""
from __future__ import annotations
import math
from datetime import date, timedelta
from calendar import monthrange


# ── Helpers ──────────────────────────────────────────────────────────────────

def _next_period(period: str) -> str:
    year, month = int(period[:4]), int(period[5:])
    if month == 12:
        return f"{year + 1}.01"
    return f"{year}.{month + 1:02d}"


def _period_to_date(period: str) -> date:
    year, month = int(period[:4]), int(period[5:])
    return date(year, month, 1)


def _months_between(start: str, end: str) -> int:
    sy, sm = int(start[:4]), int(start[5:])
    ey, em = int(end[:4]), int(end[5:])
    return (ey - sy) * 12 + (em - sm)


# ── 4.1 — Sezonowe srednie ──────────────────────────────────────────────────

def seasonal_averages(readings: list[dict]) -> dict[int, dict]:
    by_month: dict[int, list[float]] = {}
    for r in readings:
        month = int(r["period"].split(".")[1])
        by_month.setdefault(month, []).append(r["production_kwh"])

    result = {}
    for month, values in by_month.items():
        mean = sum(values) / len(values)
        if len(values) > 1:
            variance = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
            std = math.sqrt(variance)
        else:
            std = 0.0
        result[month] = {"mean": round(mean, 3), "std": round(std, 3), "count": len(values)}
    return result


# ── 4.2 — Model przejsciowy po rozbudowie ────────────────────────────────────

def get_capacity_stages(investments: list[dict]) -> list[dict]:
    stages = [
        {"date": i["date"], "kwp": i["power_kwp"]}
        for i in investments if i.get("power_kwp")
    ]
    return sorted(stages, key=lambda s: s["date"])


def get_scale_factor(
    readings: list[dict],
    stages: list[dict],
    months_for_phase_b: int = 12,
) -> tuple[float, str]:
    if not stages or len(stages) < 2:
        return 1.0, "B"

    latest_stage = stages[-1]
    prev_stage = stages[-2]
    if not readings:
        return 1.0, "B"

    last_period = max(r["period"] for r in readings)
    months_since_expansion = _months_between(latest_stage["date"][:7].replace("-", "."), last_period)

    if months_since_expansion < months_for_phase_b:
        scale = latest_stage["kwp"] / prev_stage["kwp"] if prev_stage["kwp"] else 1.0
        return round(scale, 4), "A"
    return 1.0, "B"


# ── 4.3 — Degradacja paneli ──────────────────────────────────────────────────

def apply_degradation(
    production_kwh: float,
    installation_date: str,
    forecast_period: str,
    annual_rate: float,
) -> float:
    if annual_rate <= 0:
        return production_kwh
    install_year = int(installation_date[:4])
    install_month = int(installation_date[5:7])
    f_year = int(forecast_period[:4])
    f_month = int(forecast_period[5:])
    months_elapsed = (f_year - install_year) * 12 + (f_month - install_month)
    years_elapsed = max(0, months_elapsed / 12)
    factor = (1 - annual_rate) ** years_elapsed
    return round(production_kwh * factor, 3)


# ── 4.4 — Prognoza miesieczna z eskalacja cen ────────────────────────────────

def forecast_months(
    readings: list[dict],
    investments: list[dict],
    months_ahead: int,
    degradation_rate: float,
    base_price: float,
    billing_periods: list[dict] | None = None,
    rce_prices: list[dict] | None = None,
    net_metering_ratio: float = 0.80,
) -> list[dict]:
    from services.calculations import _get_billing_model, _get_rce_price

    if not readings:
        return []

    avgs = seasonal_averages(readings)
    stages = get_capacity_stages(investments)
    scale, phase = get_scale_factor(readings, stages)

    installation_date = stages[0]["date"] if stages else None

    last_period = max(r["period"] for r in readings)
    bp_list = billing_periods or []
    rce_list = rce_prices or []

    result = []
    period = _next_period(last_period)

    for i in range(months_ahead):
        month = int(period.split(".")[1])
        month_data = avgs.get(month)
        warning = None

        if month_data is None:
            prod_base = 0.0
            std = 0.0
            data_points = 0
            warning = "Brak danych historycznych dla tego miesiaca"
        else:
            prod_base = month_data["mean"]
            std = month_data["std"]
            data_points = month_data["count"]
            if data_points < 3:
                warning = f"Malo danych ({data_points} mies.) — niska pewnosc prognozy"

        prod_scaled = prod_base * scale

        if installation_date:
            prod_forecast = apply_degradation(prod_scaled, installation_date, period, degradation_rate)
        else:
            prod_forecast = prod_scaled

        model = _get_billing_model(period, bp_list)

        if model == "net_billing":
            rce = _get_rce_price(period, rce_list)
            auto_frac = 0.4
            auto = prod_forecast * auto_frac
            sent = prod_forecast * (1 - auto_frac)
            savings_base = auto * base_price + sent * (rce or 0.0)
        else:
            savings_base = prod_forecast * base_price * 0.85

        result.append({
            "period": period,
            "production_forecast": round(prod_forecast, 1),
            "production_mean": round(prod_base, 1),
            "std": round(std, 1),
            "data_points": data_points,
            "savings_pln_base": round(savings_base, 2),
            "capacity_phase": phase,
            "model": model,
            "warning": warning,
        })

        period = _next_period(period)

    return result


# ── 4.5 — Przedzial ufnosci break-even ───────────────────────────────────────

def breakeven_scenarios(
    remaining_pln: float,
    forecast: list[dict],
    price_growth_rates: list[float],
    base_price: float,
) -> list[dict]:
    scenario_labels = {
        0.0: "pessimistic",
        0.03: "custom",
        0.07: "base",
        0.12: "optimistic",
    }

    results = []
    for rate in price_growth_rates:
        cumulative = 0.0
        months_to_roi = None
        for i, m in enumerate(forecast):
            price_factor = (1 + rate) ** ((i + 1) / 12)
            monthly_savings = m["savings_pln_base"] * price_factor
            cumulative += monthly_savings
            if cumulative >= remaining_pln and months_to_roi is None:
                months_to_roi = i + 1

        results.append({
            "growth_rate": rate,
            "label": f"+{int(rate*100)}%/rok" if rate > 0 else "0% (stale ceny)",
            "months_to_roi": months_to_roi,
            "cumulative_savings": round(cumulative, 2),
            "scenario": scenario_labels.get(rate, "custom"),
        })

    return results


def breakeven_confidence_interval(scenarios: list[dict]) -> dict:
    by_scenario = {s["scenario"]: s["months_to_roi"] for s in scenarios}
    return {
        "pessimistic": by_scenario.get("pessimistic"),
        "base": by_scenario.get("base"),
        "optimistic": by_scenario.get("optimistic"),
    }
