"""R-020 Kontrakt: liczniki energii z Home Assistant (wejście) (#166).

Brak HA w środowisku testów: kontrakt sprawdzany na granicy adaptera
services.ha_stats.get_monthly_energy (zwraca kWh albo None). Wywołania HTTP do HA
pokrywa tests/test_ha_stats.py; prawdziwy HA - test UAT.
"""
import pytest

import main

ENCJE = """UPDATE app_settings SET ha_solar_entity = 'sensor.solar',
           ha_grid_consumed_entity = 'sensor.grid_in', ha_grid_returned_entity = 'sensor.grid_out'"""


@pytest.fixture
def ha(monkeypatch):
    """Dane liczników w HA: {(encja, rok, miesiąc): kWh}; brak klucza = brak danych (None)."""
    data, calls = {}, []

    async def fake(entity_id, year, month):
        calls.append((entity_id, year, month))
        return data.get((entity_id, year, month))
    monkeypatch.setattr(main.ha_stats, "get_monthly_energy", fake)
    return data, calls


def test_AC_020_1_liczniki_za_miesiac_w_kwh(client, seed, ha):
    seed(ENCJE)
    data, _ = ha
    data.update({("sensor.solar", 2026, 9): 612.3456, ("sensor.grid_in", 2026, 9): 210.1,
                 ("sensor.grid_out", 2026, 9): 380.0})
    assert client.get("/api/ha-solar-fetch", params={"period": "2026.09"}).json()["production_kwh"] == 612.346
    assert client.get("/api/ha-grid-fetch", params={"period": "2026.09", "direction": "consumed"}).json()["kwh"] == 210.1
    assert client.get("/api/ha-grid-fetch", params={"period": "2026.09", "direction": "returned"}).json()["kwh"] == 380.0
    # wartości trafiają do edytowalnych pól formularza przed zapisem
    html = client.get("/odczyty/nowy").text
    assert "getElementById('production_kwh').value = d.production_kwh" in html
    assert 'id="production_kwh"' in html


def test_AC_020_2_zapisany_odczyt_nie_nadpisuje_sie(client, seed, query, post_form, ha):
    seed(ENCJE)
    data, calls = ha
    r = post_form("/odczyty/nowy", {"period": "2026.08", "year": "2026", "month": "8", "days": "31",
                                    "production_kwh": "600", "sent_to_grid_kwh": "350",
                                    "taken_from_grid_kwh": "200", "price_per_kwh": "1.0"})
    assert r.status_code == 303
    data[("sensor.solar", 2026, 8)] = 999.0               # dane w HA zmienione po zapisie
    assert client.get("/odczyty").status_code == 200
    assert calls == []                                     # lista nie odpytuje HA
    assert query("SELECT production_kwh FROM readings WHERE period='2026.08'")[0]["production_kwh"] == 600


def test_AC_020_3_brak_danych_komunikat_i_wpis_reczny(client, seed, query, post_form, ha):
    seed(ENCJE)
    r = client.get("/api/ha-solar-fetch", params={"period": "2026.09"})
    assert r.json()["error"] == "Brak danych dla sensor.solar za 2026-09"
    r = client.get("/api/ha-grid-fetch", params={"period": "2026.09", "direction": "returned"})
    assert r.json()["error"] == "Brak danych dla sensor.grid_out za 2026-09"
    html = client.get("/odczyty/nowy").text
    assert "if (d.error) { document.getElementById('solar-status').textContent = '❌ ' + d.error; return; }" in html
    r = post_form("/odczyty/nowy", {"period": "2026.09", "year": "2026", "month": "9", "days": "30",
                                    "production_kwh": "500", "sent_to_grid_kwh": "300",
                                    "taken_from_grid_kwh": "200", "price_per_kwh": "1.0"})
    assert r.status_code == 303
    assert query("SELECT production_kwh FROM readings WHERE period='2026.09'")[0]["production_kwh"] == 500
