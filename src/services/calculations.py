"""Core FV calculations — energy flows and ROI."""
from dataclasses import dataclass


@dataclass
class MonthlyStats:
    period: str
    production: float
    sent_to_grid: float
    taken_from_grid: float
    auto_consumption: float
    total_consumed: float
    savings_kwh: float
    savings_pln: float | None


def calc_monthly(
    production: float,
    sent_to_grid: float,
    taken_from_grid: float,
    price_per_kwh: float | None = None,
) -> dict:
    auto_consumption = production - sent_to_grid
    total_consumed = auto_consumption + taken_from_grid
    # Old net-metering: 80% of sent energy is returned to settlement pool
    net_metering_pool = sent_to_grid * 0.8
    savings_kwh = auto_consumption + min(net_metering_pool, taken_from_grid)
    savings_pln = savings_kwh * price_per_kwh if price_per_kwh else None
    production_value_pln = production * price_per_kwh if price_per_kwh else None
    return {
        "auto_consumption": round(auto_consumption, 3),
        "total_consumed": round(total_consumed, 3),
        "net_metering_pool": round(net_metering_pool, 3),
        "savings_kwh": round(savings_kwh, 3),
        "savings_pln": round(savings_pln, 2) if savings_pln else None,
        "production_value_pln": round(production_value_pln, 2) if production_value_pln else None,
    }


def calc_roi(
    readings: list[dict],
    total_investment_pln: float,
    default_price: float = 0.75,
) -> dict:
    """Calculate ROI state and break-even projection."""
    total_savings_pln = 0.0
    total_production = 0.0
    months_count = 0

    for r in readings:
        price = r.get("price_per_kwh") or default_price
        c = calc_monthly(r["production_kwh"], r["sent_to_grid_kwh"], r["taken_from_grid_kwh"], price)
        total_savings_pln += c["savings_pln"] or 0
        total_production += r["production_kwh"]
        months_count += 1

    remaining = total_investment_pln - total_savings_pln
    avg_monthly_savings = total_savings_pln / months_count if months_count > 0 else 0
    months_to_roi = remaining / avg_monthly_savings if avg_monthly_savings > 0 and remaining > 0 else 0

    return {
        "total_investment_pln": round(total_investment_pln, 2),
        "total_savings_pln": round(total_savings_pln, 2),
        "remaining_to_roi": round(remaining, 2),
        "roi_achieved": remaining <= 0,
        "avg_monthly_savings": round(avg_monthly_savings, 2),
        "months_to_roi": round(months_to_roi),
        "total_production_kwh": round(total_production, 1),
        "months_measured": months_count,
    }


def calc_ev_savings(
    ev_kwh: float,
    price_per_kwh: float,
    efficiency_kwh_per_100km: float,
    fuel_consumption_l_per_100km: float,
    fuel_price_per_liter: float,
) -> dict:
    """Additional savings from EV vs equivalent gasoline car."""
    km_driven = (ev_kwh / efficiency_kwh_per_100km) * 100
    fuel_cost = km_driven / 100 * fuel_consumption_l_per_100km * fuel_price_per_liter
    electricity_cost = ev_kwh * price_per_kwh
    net_savings = fuel_cost - electricity_cost
    return {
        "km_driven": round(km_driven, 1),
        "fuel_cost_equivalent": round(fuel_cost, 2),
        "electricity_cost": round(electricity_cost, 2),
        "ev_net_savings": round(net_savings, 2),
        "liters_saved": round(km_driven / 100 * fuel_consumption_l_per_100km, 2),
    }


def roi_sensitivity(
    readings: list[dict],
    total_investment_pln: float,
    prices: list[float],
) -> list[dict]:
    """ROI break-even at different energy prices."""
    results = []
    for price in prices:
        # Override all prices with this scenario price
        patched = [{**r, "price_per_kwh": price} for r in readings]
        roi = calc_roi(patched, total_investment_pln, price)
        results.append({"price_per_kwh": price, **roi})
    return results
