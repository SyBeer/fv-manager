"""R-013 Eksport i kopia danych (#30), R-014 Wyczyść bazę (#31)."""
import json

import main

READINGS = ",".join(f"('2024.{m:02d}', 2024, {m}, 500, 300, 200, 1.0)" for m in range(1, 13))
FULL = f"""
    INSERT INTO investments (date, description, cost_pln, power_kwp) VALUES ('2023-12-01', 'Panele', 30000, 6.0);
    INSERT INTO readings (period, year, month, production_kwh, sent_to_grid_kwh, taken_from_grid_kwh, price_per_kwh)
        VALUES {READINGS};
    INSERT INTO vehicles (id, name, efficiency_kwh_per_100km, fuel_consumption_l_per_100km, przebieg_km, date_from)
        VALUES (1, 'Auto', 18, 7, 12000, '2024-01-01');
    INSERT INTO ev_monthly (period, vehicle_id, kwh, km, odometer_km, public_kwh, public_km, public_cost_pln)
        VALUES ('2024.01', 1, 180, 1000, 13000, 50, 300, 60);
    INSERT INTO fuel_prices (date, price_per_liter, fuel_type, source) VALUES ('2024-01-01', 6.0, 'PB95', 'Orlen');
    INSERT INTO billing_periods (start_date, model) VALUES ('2024-07-01', 'net_billing');
    INSERT INTO rce_prices (date, price_per_kwh) VALUES ('2024-07-01', 0.4);
"""
TABLES = ["readings", "investments", "vehicles", "ev_monthly", "fuel_prices", "billing_periods", "rce_prices"]


def _restore(client, payload: dict):
    return client.post("/restore", data={"csrf_token": main._csrf_generate()},
                       files={"file": ("kopia.json", json.dumps(payload).encode(), "application/json")},
                       follow_redirects=False)


# ── R-013 ──
def test_AC_013_1_eksport_csv_12_wierszy(client, seed):
    seed(FULL)
    lines = [l for l in client.get("/odczyty/export.csv").text.splitlines() if l.strip()]
    assert len(lines) == 1 + 12


def test_AC_013_2_pelna_kopia_json(client, seed):
    seed(FULL)
    r = client.get("/backup/full")
    assert r.headers["content-type"].startswith("application/json")
    data = r.json()
    assert len(data["readings"]) == 12


def test_AC_013_3_przywrocenie_nadpisuje_dane_ustawienia_zostaja(client, seed, query):
    seed(FULL)
    backup = client.get("/backup/full").json()
    backup["readings"] = backup["readings"][:5]
    seed("UPDATE app_settings SET panel_degradation_rate = 0.008")
    r = _restore(client, backup)
    assert r.status_code == 303
    assert len(query("SELECT * FROM readings")) == 5
    assert query("SELECT panel_degradation_rate FROM app_settings")[0]["panel_degradation_rate"] == 0.008


def test_przywrocenie_odtwarza_wszystkie_pola(client, seed, query):
    seed(FULL)
    before = {t: query(f"SELECT * FROM {t} ORDER BY id") for t in TABLES}
    backup = client.get("/backup/full").json()
    assert _restore(client, backup).status_code == 303
    after = {t: query(f"SELECT * FROM {t} ORDER BY id") for t in TABLES}
    assert after == before


# ── R-014 ──
def test_AC_014_1_wyczysc_baze_usuwa_wszystko_ustawienia_zostaja(client, seed, query, post_form):
    seed(FULL + "UPDATE app_settings SET panel_degradation_rate = 0.008;")
    assert post_form("/admin/clear-db").status_code == 303
    for t in TABLES:
        assert query(f"SELECT * FROM {t}") == [], t
    assert query("SELECT panel_degradation_rate FROM app_settings")[0]["panel_degradation_rate"] == 0.008


def test_AC_014_2_tekst_wymienia_dane_i_zaleca_kopie(client):
    html = " ".join(client.get("/import").text.split())
    zone = html[html.index("Niebezpieczna strefa"):]
    for word in ("odczyty", "etapy inwestycji", "pojazdy", "dane EV", "ceny paliwa",
                 "okresy rozliczeniowe", "ceny RCE"):
        assert word in zone, word
    assert "/backup/full" in zone
    assert "Ustawienia" in zone or "ustawienia" in zone
