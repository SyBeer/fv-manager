"""R-009 Usunięcie pojazdu bez kasowania historii (#165) - D-034.

Usunięcie pojazdu domyślnie zostawia dane miesięczne - liczą się jak dane pojazdu
nieaktywnego (R-019). Dane miesięczne kasuje dopiero wyraźne potwierdzenie.
"""
import asyncio
import json


def _seed(seed):
    rows = ",".join(f"('2025.{m:02d}', 2, 180, 1000)" for m in range(1, 13))
    readings = ",".join(f"('2025.{m:02d}', 2025, {m}, 500, 300, 200, 1.0)" for m in range(1, 13))
    seed(f"""
        INSERT INTO vehicles (id, name, efficiency_kwh_per_100km, fuel_consumption_l_per_100km, fuel_type, przebieg_km)
            VALUES (1, 'Auto A', 18, 7, 'PB95', 10000), (2, 'Auto B', 18, 7, 'PB95', 20000);
        INSERT INTO investments (date, description, cost_pln) VALUES ('2025-01-01', 'Panele', 30000);
        INSERT INTO fuel_prices (date, price_per_liter, fuel_type) VALUES ('2025-01-01', 6.0, 'PB95');
        INSERT INTO readings (period, year, month, production_kwh, sent_to_grid_kwh, taken_from_grid_kwh, price_per_kwh)
            VALUES {readings};
        INSERT INTO ev_monthly (period, vehicle_id, kwh, km) VALUES {rows};
    """)


def _roi():
    import main
    import utils.db

    async def run():
        db = await utils.db.get_db()
        try:
            roi, readings, _ = await main._roi_state(db)
            return roi, {r["period"]: r.get("ev_savings_pln") for r in readings}
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


def _manage_names(html: str) -> bool:
    """Czy Auto B ma przyciski zarządzania (formularz usuwania) na /ev."""
    return "/ev/pojazdy/2/usun" in html


def test_usun_z_danymi_najpierw_pyta(client, seed, query, post_form):
    _seed(seed)
    r = post_form("/ev/pojazdy/2/usun")
    assert r.status_code == 200
    assert "12" in r.text                                   # liczba miesięcy z danymi
    assert 'name="history"' in r.text and 'value="keep"' in r.text and 'value="wipe"' in r.text
    assert query("SELECT deleted_at FROM vehicles WHERE id=2")[0]["deleted_at"] is None
    assert len(query("SELECT id FROM ev_monthly WHERE vehicle_id=2")) == 12


def test_AC_009_5_usuniecie_bez_potwierdzenia_zostawia_dane(client, seed, query, post_form):
    _seed(seed)
    roi_before, ev_before = _roi()
    cards_before = _cards_ev()
    assert roi_before["total_ev_savings_pln"] > 0
    r = post_form("/ev/pojazdy/2/usun", {"history": "keep"})
    assert r.status_code == 303
    v = query("SELECT deleted_at, is_active FROM vehicles WHERE id=2")[0]
    assert v["deleted_at"] and v["is_active"] == 0
    assert len(query("SELECT id FROM ev_monthly WHERE vehicle_id=2")) == 12
    roi_after, ev_after = _roi()
    assert roi_after["total_ev_savings_pln"] == roi_before["total_ev_savings_pln"]
    assert roi_after["remaining_to_roi"] == roi_before["remaining_to_roi"]
    assert ev_after == ev_before
    assert _cards_ev() == cards_before
    html = client.get("/ev").text
    assert not _manage_names(html)                          # pojazdu nie ma na liście /ev
    assert "/ev/pojazdy/1/usun" in html


def test_AC_009_6_usuniecie_z_potwierdzeniem_kasuje_historie(client, seed, query, post_form):
    _seed(seed)
    roi_before, _ = _roi()
    r = post_form("/ev/pojazdy/2/usun", {"history": "wipe"})
    assert r.status_code == 303
    assert query("SELECT id FROM ev_monthly WHERE vehicle_id=2") == []
    assert query("SELECT id FROM vehicles WHERE id=2") == []
    roi_after, _ = _roi()
    assert roi_after["total_ev_savings_pln"] == 0
    assert roi_after["remaining_to_roi"] > roi_before["remaining_to_roi"]


def test_usuniety_bez_pol_w_nowym_odczycie_z_polami_w_starym(client, seed, query, post_form):
    _seed(seed)
    post_form("/ev/pojazdy/2/usun", {"history": "keep"})
    assert 'name="ev_v_2"' not in client.get("/odczyty/nowy").text
    rid = query("SELECT id FROM readings WHERE period='2025.06'")[0]["id"]
    html = client.get(f"/odczyty/{rid}/edytuj").text
    assert 'name="ev_v_2"' in html and 'value="180' in html


def test_edycja_okresu_na_ev_nie_kasuje_danych_usunietego(client, seed, query, post_form):
    _seed(seed)
    post_form("/ev/pojazdy/2/usun", {"history": "keep"})
    html = client.get("/ev").text
    assert 'name="v_2"' in html                             # formularz edycji okresu ma pola usuniętego
    rid = query("SELECT id FROM readings WHERE period='2025.06'")[0]["id"]
    post_form(f"/odczyty/{rid}/edytuj", {"period": "2025.06", "year": "2025", "month": "6", "days": "30",
                                         "production_kwh": "510", "sent_to_grid_kwh": "300",
                                         "taken_from_grid_kwh": "200", "price_per_kwh": "1.0",
                                         "ev_v_2": "180", "ev_km_v_2": "1000"})
    assert len(query("SELECT id FROM ev_monthly WHERE vehicle_id=2")) == 12


def test_usuniety_nie_wraca_przez_strone_i_aktywnosc(client, seed, query, post_form):
    _seed(seed)
    post_form("/ev/pojazdy/2/usun", {"history": "keep"})
    assert client.get("/ev/pojazdy/2").status_code == 404
    assert post_form("/ev/pojazdy/2/aktywnosc", {"is_active": "1"}).status_code == 404
    assert query("SELECT is_active FROM vehicles WHERE id=2")[0]["is_active"] == 0


def test_pojazd_bez_danych_usuwany_od_razu(client, seed, query, post_form):
    _seed(seed)
    r = post_form("/ev/pojazdy/1/usun")
    assert r.status_code == 303
    assert query("SELECT id FROM vehicles WHERE id=1") == []


def test_kopia_bez_kolumny_deleted_at_przywraca_sie(client, seed, query):
    import main
    _seed(seed)
    backup = client.get("/backup/full").json()
    for v in backup["vehicles"]:
        v.pop("deleted_at", None)
    r = client.post("/restore", data={"csrf_token": main._csrf_generate()},
                    files={"file": ("kopia.json", json.dumps(backup), "application/json")}, follow_redirects=False)
    assert r.status_code in (200, 303)
    assert [v["deleted_at"] for v in query("SELECT deleted_at FROM vehicles ORDER BY id")] == [None, None]
