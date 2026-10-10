"""R-001 Wpisanie odczytu miesiąca (#20). Weryfikacja działania obecnego."""
import re


def _form(period="2026.09", prod="500", sent="300", taken="200"):
    y, m = period.split(".")[0], (period.split(".") + ["9"])[1]
    return {"period": period, "year": y, "month": str(int(re.sub(r"\D", "", m) or 9)), "days": "30",
            "production_kwh": prod, "sent_to_grid_kwh": sent, "taken_from_grid_kwh": taken,
            "price_per_kwh": "1.0"}


def test_AC_001_1_poprawny_odczyt_na_liscie(client, query, post_form):
    r = post_form("/odczyty/nowy", _form())
    assert r.status_code == 303
    assert [x["period"] for x in query("SELECT period FROM readings")] == ["2026.09"]
    assert "2026.09" in client.get("/odczyty").text


def test_AC_001_2_zly_format_okresu(client, query, post_form):
    r = post_form("/odczyty/nowy", {**_form(), "period": "2026-9"})
    assert r.status_code == 200
    assert "okres" in r.text.lower() or "RRRR.MM" in r.text
    assert query("SELECT * FROM readings") == []


def test_AC_001_3_oddane_wieksze_niz_produkcja(client, query, post_form):
    r = post_form("/odczyty/nowy", _form(prod="400", sent="500"))
    assert r.status_code == 200
    assert "nie może przekroczyć produkcji" in r.text
    assert query("SELECT * FROM readings") == []


def test_AC_001_4_przyciski_pobierz_z_ha(client, seed):
    seed("""UPDATE app_settings SET ha_solar_entity = 'sensor.solar',
            ha_grid_consumed_entity = 'sensor.grid_in', ha_grid_returned_entity = 'sensor.grid_out'""")
    html = client.get("/odczyty/nowy").text
    assert html.count("Pobierz z HA") == 3          # produkcja, oddane, pobrane
    assert "/api/ha-solar-fetch?period=" in html
    assert "/api/ha-grid-fetch?period=" in html


def test_ha_fetch_bez_ha_zwraca_blad_zamiast_wyjatku(client):
    r = client.get("/api/ha-solar-fetch", params={"period": "2026.09"})
    assert r.status_code < 500 or r.headers["content-type"].startswith("application/json")


def test_bez_encji_ha_brak_przyciskow(client):
    assert "Pobierz z HA" not in client.get("/odczyty/nowy").text


def test_AC_001_5_km_ze_stanu_licznika():
    import main
    vehicles = [{"id": 1, "przebieg_km": 12000.0}]
    ev = [{"period": "2026.01", "vehicle_id": 1, "km": None, "odometer_km": 13000.0},
          {"period": "2026.02", "vehicle_id": 1, "km": None, "odometer_km": 14200.0}]
    km = {e["period"]: e["km"] for e in main._inject_odometer_km(ev, vehicles)}
    assert km == {"2026.01": 1000.0, "2026.02": 1200.0}


def test_AC_001_6_kwota_faktury_poza_obliczeniami(client, seed, query, post_form):
    import asyncio
    import utils.db
    seed("INSERT INTO investments (date, description, cost_pln) VALUES ('2026-01-01', 'Panele', 30000)")
    post_form("/odczyty/nowy", {**_form(), "invoice_number": "FV/09/2026", "invoice_gross": "350"})

    def state():
        async def run():
            db = await utils.db.get_db()
            try:
                roi, readings, _ = await main._roi_state(db)
                er = await main._enriched_readings(db)
                return er[0]["savings_pln"], roi["remaining_to_roi"]
            finally:
                await db.close()
        return asyncio.run(run())
    import main
    before = state()
    rid = query("SELECT id FROM readings")[0]["id"]
    post_form(f"/odczyty/{rid}/edytuj", {**_form(), "invoice_number": "FV/09/2026", "invoice_gross": "400"})
    assert query("SELECT invoice_gross FROM readings")[0]["invoice_gross"] == 400
    assert state() == before
