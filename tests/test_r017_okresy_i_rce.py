"""R-017 Okresy rozliczeniowe i ceny RCE (Redmine #17). Weryfikacja działania obecnego."""
import sys

sys.path.insert(0, "src")
from services.calculations import _get_billing_model, _get_rce_price, enrich_readings_sequence


def _reading(period: str) -> dict:
    return {"period": period, "production_kwh": 500.0, "sent_to_grid_kwh": 300.0,
            "taken_from_grid_kwh": 200.0, "price_per_kwh": 1.0}


def test_AC_017_1_bez_okresow_net_metering():
    assert _get_billing_model("2023.05", []) == "net_metering"


def test_AC_017_2_okres_net_billing_od_2024_07():
    periods = [{"start_date": "2024-07-01", "end_date": None, "model": "net_billing"}]
    assert _get_billing_model("2024.06", periods) == "net_metering"
    assert _get_billing_model("2024.08", periods) == "net_billing"


def test_AC_017_3_ostatnia_cena_rce_do_konca_miesiaca():
    rce = [{"date": "2024-07-01", "price_per_kwh": 0.40}, {"date": "2024-08-15", "price_per_kwh": 0.30}]
    assert _get_rce_price("2024.08", rce) == 0.30
    periods = [{"start_date": "2024-07-01", "end_date": None, "model": "net_billing"}]
    (r,) = enrich_readings_sequence([_reading("2024.08")], 0.8, 1.0, periods, rce)
    assert r["net_billing_income_pln"] == round(300 * 0.30, 2)


def test_AC_017_4_po_usunieciu_ceny_wraca_poprzednia(client, seed, query, post_form):
    seed("""
        INSERT INTO rce_prices (date, price_per_kwh) VALUES ('2024-07-01', 0.40), ('2024-08-15', 0.30);
    """)
    rid = query("SELECT id FROM rce_prices WHERE price_per_kwh = 0.30")[0]["id"]
    assert post_form(f"/pv/rce-price/{rid}/usun").status_code == 303
    rce = query("SELECT date, price_per_kwh FROM rce_prices")
    assert _get_rce_price("2024.08", rce) == 0.40


def test_okres_rozliczeniowy_dodany_i_usuniety_przez_pv(client, query, post_form):
    r = post_form("/pv/billing-period", {"start_date": "2024-07-01", "model": "net_billing"})
    assert r.status_code == 303
    (bp,) = query("SELECT * FROM billing_periods")
    assert bp["model"] == "net_billing" and bp["end_date"] is None
    post_form(f"/pv/billing-period/{bp['id']}/usun")
    assert query("SELECT * FROM billing_periods") == []


def test_AC_017_5_okres_od_srodka_miesiaca():
    periods = [{"start_date": "2024-07-15", "end_date": None, "model": "net_billing"}]
    assert _get_billing_model("2024.07", periods) == "net_metering"   # 1.07 jeszcze bez okresu (BR-013)
    assert _get_billing_model("2024.08", periods) == "net_billing"
