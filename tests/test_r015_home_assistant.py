"""R-015 Integracja z Home Assistant (#32). Bez mockowania HA - testy ścieżek bez połączenia i formatu."""
import main


def test_AC_015_1_format_wyniku_testu():
    assert main._ha_test_message("2026-10", 114.7) == "OK — 2026-10: 114.7 kWh"


def test_AC_015_1_ekran_dopisuje_okres(client):
    html = client.get("/import").text
    assert "/api/ha-test" in html
    assert "' (okres: ' + d.last_period_start + ')'" in html


def test_AC_015_1_bez_polaczenia_komunikat_bledu(client):
    r = client.get("/api/ha-test")
    assert r.status_code == 200
    assert "error" in r.json()


def test_encje_z_panelu_energy_zapisywane(client, query, post_form):
    r = post_form("/ev/settings", {
        "efficiency_kwh_per_100km": "16", "fuel_consumption_l_per_100km": "8", "annual_km": "15000",
        "ha_solar_entity": "sensor.solar_production", "ha_grid_consumed_entity": "sensor.energy_1_8_0",
        "ha_grid_returned_entity": "sensor.energy_2_8_0", "net_metering_ratio": "0.8"})
    assert r.status_code == 303
    s = query("SELECT ha_solar_entity, ha_grid_consumed_entity, ha_grid_returned_entity FROM app_settings")[0]
    assert s == {"ha_solar_entity": "sensor.solar_production", "ha_grid_consumed_entity": "sensor.energy_1_8_0",
                 "ha_grid_returned_entity": "sensor.energy_2_8_0"}

# AC-015-2 (sensor /api/summary = /roi): tests/test_roi_consistency.py::test_api_summary_matches_roi_page
