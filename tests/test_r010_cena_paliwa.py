"""R-010 Oszczędności EV (#28) - jedna reguła ceny paliwa (D-023, D-029).

Cena paliwa rodzaju używanego przez pojazd; miesiąc liczy się wg ostatniej ceny
wpisanej do końca miesiąca; miesiące przed pierwszą ceną - wg pierwszej ceny.
Ta sama reguła na kartach /ev, stronie pojazdu i w ROI.
"""
import asyncio

import pytest


def _seed_ev(seed, periods, prices):
    rows = ",".join(f"('{p}', {p[:4]}, {int(p[5:])}, 500, 300, 200, 1.0)" for p in periods)
    ev = ",".join(f"('{p}', 1, 180, 1000)" for p in periods)
    fp = ",".join(f"('{d}', {c}, '{t}')" for d, c, t in prices)
    seed(f"""
        INSERT INTO vehicles (id, name, efficiency_kwh_per_100km, fuel_consumption_l_per_100km, fuel_type, przebieg_km)
            VALUES (1, 'Auto', 18, 7, 'PB95', 12000);
        INSERT INTO readings (period, year, month, production_kwh, sent_to_grid_kwh, taken_from_grid_kwh, price_per_kwh)
            VALUES {rows};
        INSERT INTO ev_monthly (period, vehicle_id, kwh, km) VALUES {ev};
        INSERT INTO fuel_prices (date, price_per_liter, fuel_type) VALUES {fp};
    """)


def _state():
    """Oszczędność EV z FV per miesiąc wg ROI (_ev_enrich) i wg kart /ev (_agg_vehicles_ev)."""
    import main
    import utils.db

    async def run():
        db = await utils.db.get_db()
        try:
            readings = await main._get_readings(db)
            vehicles = await main._get_vehicles(db)
            ev_monthly = await main._get_ev_monthly_all(db)
            prices = await main._get_fuel_prices(db)
            settings = await main._get_ev_settings(db)
        finally:
            await db.close()
        enriched = main._ev_enrich(readings, settings, prices, vehicles, ev_monthly)
        roi = {r["period"]: r.get("ev_savings_pln") for r in enriched}
        price_map = {r["period"]: r["price_per_kwh"] for r in readings}
        agg = main._agg_vehicles_ev(vehicles, ev_monthly, price_map, prices, 1.0)
        return roi, agg[0]["total_savings_home"]
    return asyncio.run(run())


def test_funkcja_ceny_paliwa_dla_miesiaca():
    import main
    prices = [{"date": "2026-03-10", "price_per_liter": 6.0, "fuel_type": "PB95"},
              {"date": "2026-05-31", "price_per_liter": 6.5, "fuel_type": "PB95"},
              {"date": "2026-04-05", "price_per_liter": 7.0, "fuel_type": "ON"}]
    f = main._fuel_price_for_month
    assert f(prices, "PB95", "2026.02") == 6.0      # przed pierwszą ceną - pierwsza cena (D-029)
    assert f(prices, "PB95", "2026.04") == 6.0      # cena ON nie dotyczy pojazdu na PB95
    assert f(prices, "PB95", "2026.05") == 6.5      # wpis z ostatniego dnia miesiąca liczy się
    assert f(prices, "LPG", "2026.05") is None      # brak ceny tego rodzaju


def test_AC_010_3_cena_od_wpisu_do_wpisu_tak_samo_ev_i_roi(client, seed):
    _seed_ev(seed, ["2026.03", "2026.04", "2026.05"],
             [("2026-03-10", 6.0, "PB95"), ("2026-05-20", 6.5, "PB95"), ("2026-04-05", 7.0, "ON")])
    roi, ev_total = _state()
    # 1000 km × 7 l/100 km × cena − 180 kWh × 1,00 zł
    assert roi == {"2026.03": 240.0, "2026.04": 240.0, "2026.05": 275.0}
    assert ev_total == pytest.approx(sum(roi.values()))


def test_AC_010_4_miesiace_przed_pierwsza_cena_wg_pierwszej(client, seed):
    periods = ["2025.11", "2025.12", "2026.01", "2026.02", "2026.03", "2026.04", "2026.05"]
    _seed_ev(seed, periods, [("2026-02-10", 6.0, "PB95"), ("2026-05-20", 6.5, "PB95")])
    roi, ev_total = _state()
    assert {p: roi[p] for p in periods[:-1]} == {p: 240.0 for p in periods[:-1]}
    assert roi["2026.05"] == 275.0
    assert ev_total == pytest.approx(sum(roi.values()))


def test_AC_010_4_strona_pojazdu_i_karty_ev(client, seed):
    _seed_ev(seed, ["2025.11", "2026.05"], [("2026-02-10", 6.0, "PB95"), ("2026-05-20", 6.5, "PB95")])
    html = client.get("/ev/pojazdy/1").text
    assert "420" in html and "455" in html          # koszt paliwa odpowiednika: 2025.11 po 6,00, 2026.05 po 6,50
    ev = client.get("/ev").text
    assert "420" in ev and "455" in ev
