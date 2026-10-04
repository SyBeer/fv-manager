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
