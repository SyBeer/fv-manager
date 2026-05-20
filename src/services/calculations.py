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
    carry_over_in: float = 0.0,
    net_metering_ratio: float = 0.80,
) -> dict:
    """Oblicz miesięczne przepływy energii z kumulatywną pulą net-meteringu.

    carry_over_in  — pula przeniesiona z poprzednich miesięcy bieżącego cyklu.
    net_metering_ratio — ułamek oddanej energii wracający do puli (domyślnie 0.80).
    Zwraca carry_over_out — pulę do przekazania do następnego miesiąca.
    """
    auto_consumption = production - sent_to_grid
    total_consumed = auto_consumption + taken_from_grid
    pool_this_month = sent_to_grid * net_metering_ratio
    available = carry_over_in + pool_this_month
    used = min(available, taken_from_grid)
    savings_kwh = auto_consumption + used
    carry_over_out = available - used
    savings_pln = savings_kwh * price_per_kwh if price_per_kwh else None
    production_value_pln = production * price_per_kwh if price_per_kwh else None
    return {
        "auto_consumption": round(auto_consumption, 3),
        "total_consumed": round(total_consumed, 3),
        "net_metering_pool": round(pool_this_month, 3),
        "savings_kwh": round(savings_kwh, 3),
        "savings_pln": round(savings_pln, 2) if savings_pln else None,
        "production_value_pln": round(production_value_pln, 2) if production_value_pln else None,
        "carry_over_out": round(carry_over_out, 3),
    }


def enrich_readings_sequence(
    readings: list[dict],
    net_metering_ratio: float = 0.80,
    default_price: float = 0.75,
) -> list[dict]:
    """Przetwarza odczyty chronologicznie, przewijając carry_over w cyklu kwiecień–marzec.

    Resetuje carry_over w kwietniu (początek nowego cyklu rocznego net-meteringu).
    Zwraca listę odczytów wzbogaconych o wyniki calc_monthly (w tej samej kolejności co wejście).
    """
    sorted_r = sorted(readings, key=lambda r: r["period"])
    carry_over = 0.0
    enriched_by_period: dict[str, dict] = {}

    for r in sorted_r:
        month = int(r["period"].split(".")[1])
        if month == 4:
            carry_over = 0.0
        price = r.get("price_per_kwh") or default_price
        c = calc_monthly(
            r["production_kwh"], r["sent_to_grid_kwh"], r["taken_from_grid_kwh"],
            price, carry_over, net_metering_ratio,
        )
        carry_over = c["carry_over_out"]
        enriched_by_period[r["period"]] = {**r, **c}

    return [enriched_by_period[r["period"]] for r in readings if r["period"] in enriched_by_period]


def calc_roi(
    readings: list[dict],
    total_investment_pln: float,
    default_price: float = 0.75,
    net_metering_ratio: float = 0.80,
) -> dict:
    """Calculate ROI state and break-even projection.

    Processes readings chronologically with cumulative net-metering carry_over.
    Readings must have 'period' key in format 'YYYY.MM'.
    """
    sorted_r = sorted(readings, key=lambda r: r["period"])
    carry_over = 0.0
    total_fv_savings = 0.0
    total_ev_savings = 0.0
    total_production = 0.0
    months_count = 0

    for r in sorted_r:
        month = int(r["period"].split(".")[1])
        if month == 4:
            carry_over = 0.0
        price = r.get("price_per_kwh") or default_price
        c = calc_monthly(
            r["production_kwh"], r["sent_to_grid_kwh"], r["taken_from_grid_kwh"],
            price, carry_over, net_metering_ratio,
        )
        carry_over = c["carry_over_out"]
        total_fv_savings += c["savings_pln"] or 0
        total_ev_savings += r.get("ev_savings_pln") or 0
        total_production += r["production_kwh"]
        months_count += 1

    total_savings_pln = total_fv_savings + total_ev_savings
    remaining = total_investment_pln - total_savings_pln
    avg_monthly_savings = total_savings_pln / months_count if months_count > 0 else 0
    months_to_roi = remaining / avg_monthly_savings if avg_monthly_savings > 0 and remaining > 0 else 0

    return {
        "total_investment_pln": round(total_investment_pln, 2),
        "total_savings_pln": round(total_savings_pln, 2),
        "total_fv_savings_pln": round(total_fv_savings, 2),
        "total_ev_savings_pln": round(total_ev_savings, 2),
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
    """EV savings vs equivalent gasoline car.

    Formula: savings = avoided_fuel_cost - (ev_kwh * price_per_kwh)

    ev_kwh to całkowita energia naładowana do pojazdu — bez rozróżniania
    źródła (PV / sieć), bo dwukierunkowy licznik już abstrahuje przepływy.
    """
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
    net_metering_ratio: float = 0.80,
) -> list[dict]:
    """ROI break-even at different energy prices."""
    results = []
    for price in prices:
        patched = [{**r, "price_per_kwh": price} for r in readings]
        roi = calc_roi(patched, total_investment_pln, price, net_metering_ratio)
        results.append({"price_per_kwh": price, **roi})
    return results
