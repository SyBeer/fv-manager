"""R-022 Zakładka „Wirtualny magazyn” (T-23), R-023 Szacunek stanu magazynu na dziś (T-24).

HA w testach: granica adaptera services.ha_stats.get_monthly_energy (jak R-020, B-47);
„dziś” podstawiane przez main._today.
"""
import json
import re
from datetime import date

import pytest

import main

ENCJE = """UPDATE app_settings SET ha_solar_entity = 'sensor.solar',
           ha_grid_consumed_entity = 'sensor.grid_in', ha_grid_returned_entity = 'sensor.grid_out'"""


def _flat(html: str) -> str:
    return " ".join(re.sub(r"<[^>]+>", " ", html).replace(" ", " ").split())


def _odczyty(seed, rows):
    vals = ",".join(f"('{p}', {p[:4]}, {int(p[5:])}, {max(sent, 1)}, {sent}, {taken}, 1.0)"
                    for p, sent, taken in rows)
    seed(f"""INSERT INTO readings (period, year, month, production_kwh, sent_to_grid_kwh, taken_from_grid_kwh, price_per_kwh)
             VALUES {vals};""")


def _dane(html: str) -> dict:
    m = re.search(r'<script id="magazyn-data" type="application/json">(.*?)</script>', html, re.S)
    assert m, "brak danych wykresów"
    return json.loads(m.group(1))


@pytest.fixture
def dzis(monkeypatch):
    def _set(d: date):
        monkeypatch.setattr(main, "_today", lambda: d)
    _set(date(2026, 10, 13))
    return _set


@pytest.fixture
def ha(monkeypatch):
    data, calls = {}, []

    async def fake(entity_id, year, month):
        calls.append((entity_id, year, month))
        return data.get((entity_id, year, month))
    monkeypatch.setattr(main.ha_stats, "get_monthly_energy", fake)
    return data, calls


# ── R-022 ──
def test_menu_ma_zakladke(client):
    html = client.get("/").text
    assert 'href="/magazyn"' in html and "Wirtualny magazyn" in html


def test_AC_022_1_wykres_stanu_40_70(client, seed, dzis, ha):
    _odczyty(seed, [("2026.04", 300, 200), ("2026.05", 100, 50)])
    d = _dane(client.get("/magazyn").text)
    assert d["stan"]["labels"] == ["2026.04", "2026.05"]
    assert d["stan"]["biezacy"] == [40, 70]


def test_AC_022_2_przeplyw_czerwca(client, seed, dzis, ha):
    _odczyty(seed, [("2026.04", 300, 200), ("2026.05", 100, 50), ("2026.06", 0, 100)])
    d = _dane(client.get("/magazyn").text)
    i = d["przeplyw"]["labels"].index("2026.06")
    assert d["przeplyw"]["odebrane"][i] == 70
    assert d["przeplyw"]["ponad_pule"][i] == 30
    assert d["stan"]["biezacy"][d["stan"]["labels"].index("2026.06")] == 0
    text = _flat(client.get("/magazyn").text)
    assert re.search(r"2026\.06 .*?70 .*?30", text)


def test_AC_022_3_przepadlo_40(client, seed, dzis, ha):
    _odczyty(seed, [("2026.03", 300, 200), ("2026.04", 0, 0)])
    text = _flat(client.get("/magazyn").text)
    assert re.search(r"2025\.04[–-]2026\.03 .*?przepadło 40 kWh", text)


def test_AC_022_4_do_wyzerowania_10_mies(client, seed, dzis, ha):
    _odczyty(seed, [("2026.04", 300, 200), ("2026.05", 100, 50)])
    assert "do wyzerowania: 10 mies." in _flat(client.get("/magazyn").text)


def test_poprzedni_cykl_na_wykresie(client, seed, dzis, ha):
    _odczyty(seed, [("2025.04", 300, 200), ("2025.05", 0, 0), ("2026.04", 100, 0)])
    d = _dane(client.get("/magazyn").text)
    assert d["stan"]["biezacy"][:1] == [80]
    assert d["stan"]["poprzedni"][:2] == [40, 40]


def test_luka_w_cyklu_wykres_wyrownany_po_miesiacu(client, seed, dzis, ha):
    # przegląd kodu: brak maja nie może przesunąć czerwca nad maj poprzedniego cyklu
    _odczyty(seed, [("2025.04", 300, 200), ("2025.05", 100, 0), ("2025.06", 100, 0),
                    ("2026.04", 100, 0), ("2026.06", 100, 0)])
    d = _dane(client.get("/magazyn").text)
    assert d["stan"]["labels"][:3] == ["2026.04", "mies. 05", "2026.06"]
    assert d["stan"]["biezacy"][:3] == [80, None, 160]
    assert d["stan"]["poprzedni"][:3] == [40, 120, 200]


def test_bez_odczytow(client, dzis, ha):
    r = client.get("/magazyn")
    assert r.status_code == 200 and "Brak odczytów" in r.text


# ── R-023 ──
def test_AC_023_1_szacunek_60(client, seed, dzis, ha):
    seed(ENCJE)
    _odczyty(seed, [("2026.09", 300, 200)])
    data, _ = ha
    data.update({("sensor.grid_out", 2026, 10): 50.0, ("sensor.grid_in", 2026, 10): 20.0})
    assert "Szacunek na dziś: 60 kWh" in _flat(client.get("/magazyn").text)


def test_AC_023_2_kwiecien_od_zera(client, seed, dzis, ha):
    seed(ENCJE)
    dzis(date(2026, 4, 10))
    _odczyty(seed, [("2026.03", 300, 200)])
    data, _ = ha
    data.update({("sensor.grid_out", 2026, 4): 10.0, ("sensor.grid_in", 2026, 4): 0.0})
    assert "Szacunek na dziś: 8 kWh" in _flat(client.get("/magazyn").text)


def test_AC_023_3_brak_danych_ha(client, seed, dzis, ha):
    seed(ENCJE)
    _odczyty(seed, [("2026.04", 300, 200), ("2026.09", 0, 0)])
    html = client.get("/magazyn").text
    text = _flat(html)
    assert "Brak danych z Home Assistant" in text
    assert "Do odebrania z magazynu" in text and "do wyzerowania" in text
    assert _dane(html)["stan"]["labels"]


def test_AC_023_3_bez_encji_ha(client, seed, dzis, ha):
    _odczyty(seed, [("2026.09", 300, 200)])
    assert "Brak danych z Home Assistant" in _flat(client.get("/magazyn").text)


def test_AC_023_4_luka_w_odczytach(client, seed, dzis, ha):
    seed(ENCJE)
    _odczyty(seed, [("2026.08", 300, 200)])
    text = _flat(client.get("/magazyn").text)
    assert "Uzupełnij odczyt za 2026.09" in text
    assert "Szacunek na dziś:" not in text
    assert ha[1] == []                                  # bez pytania HA


def test_odczyt_za_biezacy_miesiac_bez_ha(client, seed, dzis, ha):
    seed(ENCJE)
    _odczyty(seed, [("2026.10", 300, 200)])
    text = _flat(client.get("/magazyn").text)
    assert "Szacunek na dziś:" not in text and ha[1] == []


def test_AC_023_5_szacunek_nie_zapisuje(client, seed, dzis, ha, query):
    seed(ENCJE)
    _odczyty(seed, [("2026.09", 300, 200)])
    data, _ = ha
    data.update({("sensor.grid_out", 2026, 10): 50.0, ("sensor.grid_in", 2026, 10): 20.0})
    before = query("SELECT * FROM readings")
    client.get("/magazyn")
    assert query("SELECT * FROM readings") == before
    assert len(before) == 1


def test_net_billing_bez_szacunku(client, seed, dzis, ha):
    seed(ENCJE)
    seed("INSERT INTO billing_periods (start_date, end_date, model) VALUES ('2026-09-01', NULL, 'net_billing');")
    _odczyty(seed, [("2026.09", 300, 200)])
    r = client.get("/magazyn")
    assert r.status_code == 200
    assert "Szacunek na dziś:" not in _flat(r.text) and ha[1] == []


def test_wiele_brakujacych_odczytow(client, seed, dzis, ha):
    _odczyty(seed, [("2026.03", 300, 200)])
    text = _flat(client.get("/magazyn").text)
    assert "Uzupełnij odczyt za 2026.09" in text
    assert "Brak odczytów od 2026.04 (6 mies.)" in text
