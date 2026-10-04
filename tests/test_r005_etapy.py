"""R-005 Etapy inwestycji (#23). Weryfikacja działania obecnego (D-014..D-017, D-021)."""
import sys

sys.path.insert(0, "src")
from services.calculations import investment_as_of
from services.forecast import forecast_months


def _add(post_form, date, cost, power=""):
    return post_form("/inwestycje/nowa", {"date": date, "description": "etap", "cost_pln": cost, "power_kwp": power})


def _total(query):
    return investment_as_of(query("SELECT date, cost_pln FROM investments"), "2099.12")


def test_AC_005_1_dodanie_etapu(client, query, post_form):
    assert _add(post_form, "2022-06-01", "30000", "6").status_code == 303
    (inv,) = query("SELECT * FROM investments")
    assert inv["cost_pln"] == 30000 and inv["power_kwp"] == 6
    assert _total(query) == 30000
    assert "30" in client.get("/inwestycje").text


def test_AC_005_2_usuniecie_etapu(client, query, post_form):
    _add(post_form, "2022-06-01", "30000")
    _add(post_form, "2023-06-01", "10000")
    second = query("SELECT id FROM investments WHERE cost_pln = 10000")[0]["id"]
    post_form(f"/inwestycje/{second}/usun")
    assert _total(query) == 30000


def test_AC_005_3_zmiana_kosztu(client, query, post_form):
    _add(post_form, "2022-06-01", "30000")
    iid = query("SELECT id FROM investments")[0]["id"]
    r = post_form(f"/inwestycje/{iid}/edytuj", {"date": "2022-06-01", "description": "etap", "cost_pln": "32000"})
    assert r.status_code == 303
    assert _total(query) == 32000


def test_AC_005_4_koszt_zero(client, query, post_form):
    _add(post_form, "2022-06-01", "30000")
    assert _add(post_form, "2023-01-01", "0").status_code == 303
    assert len(query("SELECT * FROM investments")) == 2
    assert _total(query) == 30000


def test_AC_005_5_dofinansowanie_ujemne(client, query, post_form):
    _add(post_form, "2022-06-01", "30000")
    assert _add(post_form, "2022-09-01", "-5000").status_code == 303
    assert _total(query) == 25000


def test_AC_005_6_etap_serwisowy_bez_mocy_nie_zmienia_prognozy():
    readings = [{"period": f"2023.{m:02d}", "production_kwh": 400.0 + m, "sent_to_grid_kwh": 100.0,
                 "taken_from_grid_kwh": 200.0, "price_per_kwh": 1.0} for m in range(1, 13)]
    base = [{"date": "2022-06-01", "cost_pln": 30000.0, "power_kwp": 6.0}]
    serwis = base + [{"date": "2023-10-01", "cost_pln": 800.0, "power_kwp": None}]
    assert forecast_months(readings, base, 12, 0.006, 1.0) == forecast_months(readings, serwis, 12, 0.006, 1.0)
    assert investment_as_of(serwis, "2023.12") - investment_as_of(base, "2023.12") == 800.0
