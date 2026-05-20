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


def _get_billing_model(period: str, billing_periods: list[dict]) -> str:
    year, month = period.split(".")
    period_date = f"{year}-{month.zfill(2)}-01"
    for bp in sorted(billing_periods, key=lambda b: b["start_date"], reverse=True):
        if bp["start_date"] <= period_date:
            if bp["end_date"] is None or bp["end_date"] >= period_date:
                return bp["model"]
    return "net_metering"


def _get_rce_price(
    period: str,
    rce_prices: list[dict],
    sale_price_override: float | None = None,
) -> float | None:
    if sale_price_override is not None:
        return sale_price_override
    if not rce_prices:
        return None
    year, month = period.split(".")
    period_end = f"{year}-{month.zfill(2)}-28"
    prices_desc = sorted(rce_prices, key=lambda p: p["date"], reverse=True)
    obj = next((p for p in prices_desc if p["date"] <= period_end), None)
    return obj["price_per_kwh"] if obj else None


def calc_monthly_netbilling(
    production: float,
    sent_to_grid: float,
    taken_from_grid: float,
    retail_price_per_kwh: float,
    rce_price_per_kwh: float | None,
) -> dict:
    auto_consumption = production - sent_to_grid
    total_consumed = auto_consumption + taken_from_grid
    rce = rce_price_per_kwh or 0.0
    savings_pln = auto_consumption * retail_price_per_kwh + sent_to_grid * rce
    production_value_pln = production * retail_price_per_kwh
    return {
        "auto_consumption": round(auto_consumption, 3),
        "total_consumed": round(total_consumed, 3),
        "net_metering_pool": 0.0,
        "savings_kwh": round(auto_consumption, 3),
        "savings_pln": round(savings_pln, 2),
        "production_value_pln": round(production_value_pln, 2),
        "carry_over_out": 0.0,
        "net_billing_income_pln": round(sent_to_grid * rce, 2),
        "model": "net_billing",
    }


def enrich_readings_sequence(
    readings: list[dict],
    net_metering_ratio: float = 0.80,
    default_price: float = 0.75,
    billing_periods: list[dict] | None = None,
    rce_prices: list[dict] | None = None,
) -> list[dict]:
    bp_list = billing_periods or []
    rce_list = rce_prices or []

    sorted_r = sorted(readings, key=lambda r: r["period"])
    carry_over = 0.0
    last_model = "net_metering"
    enriched_by_period: dict[str, dict] = {}

    for r in sorted_r:
        month = int(r["period"].split(".")[1])
        model = _get_billing_model(r["period"], bp_list)

        if month == 4 or (model == "net_billing" and last_model == "net_metering"):
            carry_over = 0.0
        if model == "net_metering" and last_model == "net_billing":
            carry_over = 0.0

        last_model = model
        price = r.get("price_per_kwh") or default_price

        if model == "net_billing":
            rce = _get_rce_price(r["period"], rce_list, r.get("sale_price_kwh"))
            c = calc_monthly_netbilling(
                r["production_kwh"], r["sent_to_grid_kwh"], r["taken_from_grid_kwh"],
                price, rce,
            )
            carry_over = 0.0
        else:
            c = calc_monthly(
                r["production_kwh"], r["sent_to_grid_kwh"], r["taken_from_grid_kwh"],
                price, carry_over, net_metering_ratio,
            )
            carry_over = c["carry_over_out"]
            c["model"] = "net_metering"

        enriched_by_period[r["period"]] = {**r, **c}

    return [enriched_by_period[r["period"]] for r in readings if r["period"] in enriched_by_period]


def calc_roi(
    readings: list[dict],
    total_investment_pln: float,
    default_price: float = 0.75,
    net_metering_ratio: float = 0.80,
    billing_periods: list[dict] | None = None,
    rce_prices: list[dict] | None = None,
) -> dict:
    """Calculate ROI state and break-even projection.

    Obsługuje mieszaną historię net-metering + net-billing.
    """
    bp_list = billing_periods or []
    rce_list = rce_prices or []

    sorted_r = sorted(readings, key=lambda r: r["period"])
    carry_over = 0.0
    last_model = "net_metering"
    total_fv_savings = 0.0
    total_ev_savings = 0.0
    total_production = 0.0
    months_count = 0

    for r in sorted_r:
        month = int(r["period"].split(".")[1])
        model = _get_billing_model(r["period"], bp_list)

        if month == 4 or (model == "net_billing" and last_model == "net_metering"):
            carry_over = 0.0
        if model == "net_metering" and last_model == "net_billing":
            carry_over = 0.0

        last_model = model
        price = r.get("price_per_kwh") or default_price

        if model == "net_billing":
            rce = _get_rce_price(r["period"], rce_list, r.get("sale_price_kwh"))
            c = calc_monthly_netbilling(
                r["production_kwh"], r["sent_to_grid_kwh"], r["taken_from_grid_kwh"],
                price, rce,
            )
            carry_over = 0.0
        else:
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
    billing_periods: list[dict] | None = None,
    rce_prices: list[dict] | None = None,
) -> list[dict]:
    """ROI break-even at different retail energy prices."""
    results = []
    for price in prices:
        patched = [{**r, "price_per_kwh": price} for r in readings]
        roi = calc_roi(patched, total_investment_pln, price, net_metering_ratio,
                      billing_periods, rce_prices)
        results.append({"price_per_kwh": price, **roi})
    return results
