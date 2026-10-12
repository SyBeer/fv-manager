"""R-021 Stan wirtualnego magazynu na dashboardzie (T-22, D-035, D-036)."""
import re


def _flat(html: str) -> str:
    return " ".join(re.sub(r"<[^>]+>", " ", html).replace(" ", " ").split())


def _magazyn(client) -> str | None:
    m = re.search(r"Do odebrania z magazynu:? (\S+) kWh", _flat(client.get("/").text))
    return m.group(1) if m else None


def _odczyty(seed, rows):
    vals = ",".join(f"('{p}', {p[:4]}, {int(p[5:])}, {prod}, {sent}, {taken}, 1.0)" for p, prod, sent, taken in rows)
    seed(f"""INSERT INTO readings (period, year, month, production_kwh, sent_to_grid_kwh, taken_from_grid_kwh, price_per_kwh)
             VALUES {vals};""")


def test_AC_021_1_po_odczycie_40_kwh(client, seed):
    _odczyty(seed, [("2026.05", 500, 300, 200)])
    assert _magazyn(client) == "40"


def test_AC_021_2_pula_z_marca_przepada_w_kwietniu(client, seed):
    _odczyty(seed, [("2026.03", 500, 300, 200), ("2026.04", 100, 100, 50)])
    assert _magazyn(client) == "30"


def test_AC_021_3_kolejny_odczyt_zmniejsza_magazyn(client, seed, post_form):
    _odczyty(seed, [("2026.08", 500, 300, 200)])
    assert _magazyn(client) == "40"
    r = post_form("/odczyty/nowy", {"period": "2026.09", "year": "2026", "month": "9", "days": "30",
                                    "production_kwh": "0",
                                    "sent_to_grid_kwh": "0", "taken_from_grid_kwh": "25",
                                    "price_per_kwh": "1.0"})
    assert r.status_code == 303
    assert _magazyn(client) == "15"


def test_magazyn_pusty_pokazuje_0(client, seed):
    _odczyty(seed, [("2026.05", 100, 0, 50)])
    assert _magazyn(client) == "0"


def test_bez_odczytow_brak_karty(client):
    assert "Do odebrania z magazynu" not in client.get("/").text


def test_ostatni_odczyt_w_net_billingu_brak_karty(client, seed):
    # Q-066 zaparkowane: w net-billingu pula nie istnieje - karta znika zamiast pokazywać 0 (B-55)
    seed("INSERT INTO billing_periods (start_date, end_date, model) VALUES ('2026-06-01', NULL, 'net_billing');")
    _odczyty(seed, [("2026.05", 500, 300, 200), ("2026.06", 500, 300, 200)])
    assert "Do odebrania z magazynu" not in client.get("/").text
