"""R-019 Pojazd nieaktywny (#111) - D-025, D-028.

Pojazd nieaktywny: dane dalej w oszczędnościach i ROI; w formularzu odczytu nowego
miesiąca bez pól EV; przy edycji odczytu, w którym ma dane - pola widoczne.
"""
import asyncio


def _seed(seed):
    seed("""
        INSERT INTO vehicles (id, name, efficiency_kwh_per_100km, fuel_consumption_l_per_100km, fuel_type, przebieg_km)
            VALUES (1, 'Auto A', 18, 7, 'PB95', 10000), (2, 'Auto B', 18, 7, 'PB95', 20000);
        INSERT INTO investments (date, description, cost_pln) VALUES ('2025-01-01', 'Panele', 30000);
        INSERT INTO fuel_prices (date, price_per_liter, fuel_type) VALUES ('2025-01-01', 6.0, 'PB95');
        INSERT INTO readings (period, year, month, production_kwh, sent_to_grid_kwh, taken_from_grid_kwh, price_per_kwh)
            VALUES ('2025.06', 2025, 6, 500, 300, 200, 1.0);
        INSERT INTO ev_monthly (period, vehicle_id, kwh, km) VALUES ('2025.06', 2, 180, 1000);
    """)


def _roi_ev():
    import main
    import utils.db

    async def run():
        db = await utils.db.get_db()
        try:
            return (await main._roi_state(db))[0]["total_ev_savings_pln"]
        finally:
            await db.close()
    return asyncio.run(run())


def _cards_ev():
    import main
    import utils.db

    async def run():
        db = await utils.db.get_db()
        try:
            vehicles = await main._get_vehicles(db)
            ev = main._inject_odometer_km(await main._get_ev_monthly_all(db), vehicles)
            prices = await main._get_fuel_prices(db)
            readings = await main._get_readings(db)
        finally:
            await db.close()
        price_map = {r["period"]: r["price_per_kwh"] for r in readings}
        return {v["id"]: v["total_savings"] for v in main._agg_vehicles_ev(vehicles, ev, price_map, prices, 1.0)}
    return asyncio.run(run())


def test_nowy_pojazd_domyslnie_aktywny(client, seed, query):
    _seed(seed)
    assert [v["is_active"] for v in query("SELECT is_active FROM vehicles ORDER BY id")] == [1, 1]


def test_AC_019_1_nieaktywny_dalej_w_roi_i_kartach_ev(client, seed, query, post_form):
    _seed(seed)
    before = _roi_ev()
    assert before == 240.0
    cards_before = _cards_ev()
    r = post_form("/ev/pojazdy/2/aktywnosc", {"is_active": "0"})
    assert r.status_code == 303
    assert query("SELECT is_active FROM vehicles WHERE id=2")[0]["is_active"] == 0
    assert _roi_ev() == before
    assert _cards_ev() == cards_before                 # karty /ev: te same oszczędności
    html = client.get("/ev").text
    assert "Auto B" in html and "nieaktywny" in html


def test_AC_019_2_formularz_nowego_miesiaca_bez_pol_nieaktywnego(client, seed, post_form):
    _seed(seed)
    post_form("/ev/pojazdy/2/aktywnosc", {"is_active": "0"})
    html = client.get("/odczyty/nowy").text
    assert 'name="ev_v_1"' in html
    assert 'name="ev_v_2"' not in html


def test_AC_019_2_odczyt_z_pustymi_polami_aktywnego_zapisuje_sie(client, seed, query, post_form):
    _seed(seed)
    post_form("/ev/pojazdy/2/aktywnosc", {"is_active": "0"})
    r = post_form("/odczyty/nowy", {"period": "2026.10", "year": "2026", "month": "10", "days": "31",
                                    "production_kwh": "400", "sent_to_grid_kwh": "200",
                                    "taken_from_grid_kwh": "150", "price_per_kwh": "1.0", "ev_v_1": ""})
    assert r.status_code == 303
    assert query("SELECT period FROM readings WHERE period='2026.10'")


def test_AC_019_3_edycja_odczytu_pokazuje_dane_nieaktywnego(client, seed, query, post_form):
    _seed(seed)
    post_form("/ev/pojazdy/2/aktywnosc", {"is_active": "0"})
    rid = query("SELECT id FROM readings WHERE period='2025.06'")[0]["id"]
    html = client.get(f"/odczyty/{rid}/edytuj").text
    assert 'name="ev_v_2"' in html and 'value="180' in html
    assert 'name="ev_v_1"' in html                     # aktywny pojazd też ma pola


def test_AC_019_3_zapis_edycji_zachowuje_dane_nieaktywnego(client, seed, query, post_form):
    _seed(seed)
    post_form("/ev/pojazdy/2/aktywnosc", {"is_active": "0"})
    rid = query("SELECT id FROM readings WHERE period='2025.06'")[0]["id"]
    post_form(f"/odczyty/{rid}/edytuj", {"period": "2025.06", "year": "2025", "month": "6", "days": "30",
                                         "production_kwh": "510", "sent_to_grid_kwh": "300",
                                         "taken_from_grid_kwh": "200", "price_per_kwh": "1.0",
                                         "ev_v_2": "180", "ev_km_v_2": "1000"})
    assert query("SELECT kwh FROM ev_monthly WHERE vehicle_id=2")[0]["kwh"] == 180


def test_ponowna_aktywacja(client, seed, query, post_form):
    _seed(seed)
    post_form("/ev/pojazdy/2/aktywnosc", {"is_active": "0"})
    post_form("/ev/pojazdy/2/aktywnosc", {"is_active": "1"})
    assert 'name="ev_v_2"' in client.get("/odczyty/nowy").text


def test_stan_licznika_bez_kwh_zapisuje_sie(client, seed, query, post_form):
    """D-026: właściciel wpisuje stan licznika - wpis bez kWh nie może zginąć."""
    _seed(seed)
    post_form("/odczyty/nowy", {"period": "2026.10", "year": "2026", "month": "10", "days": "31",
                                "production_kwh": "400", "sent_to_grid_kwh": "200",
                                "taken_from_grid_kwh": "150", "price_per_kwh": "1.0", "ev_odometer_v_1": "11000"})
    assert query("SELECT odometer_km FROM ev_monthly WHERE period='2026.10' AND vehicle_id=1")[0]["odometer_km"] == 11000


# ── Poprawki po przeglądzie kodu (3.3.2) ──
def test_edycja_na_ev_nie_gubi_wpisu_z_samym_stanem_licznika(client, seed, query, post_form):
    _seed(seed)
    seed("INSERT INTO ev_monthly (period, vehicle_id, kwh, odometer_km) VALUES ('2025.06', 1, 0, 10500);")
    post_form("/ev/monthly/2025.06/edytuj", {"v_2": "180", "km_v_2": "1000", "odometer_v_1": "10500"})
    assert query("SELECT odometer_km FROM ev_monthly WHERE vehicle_id=1")[0]["odometer_km"] == 10500


def test_wpis_bez_kwh_nie_daje_oszczednosci(client, seed):
    _seed(seed)
    seed("INSERT INTO ev_monthly (period, vehicle_id, kwh, odometer_km) VALUES ('2025.06', 1, 0, 10500);")
    assert _roi_ev() == 240.0                          # tylko Auto B: 420 − 180


def test_edycja_na_ev_nie_wpisuje_wyliczonych_km_jako_recznych(client, seed):
    _seed(seed)
    seed("UPDATE ev_monthly SET km=NULL, odometer_km=21000 WHERE vehicle_id=2;")
    html = client.get("/ev").text
    assert 'name="km_v_2"' in html
    import re
    field = re.search(r'<input[^>]*name="km_v_2"[^>]*>', html, re.S).group(0)
    assert 'value=""' in field or "value=" not in field
