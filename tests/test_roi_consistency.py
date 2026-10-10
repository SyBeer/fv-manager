"""ROI liczony jednakowo na wszystkich ekranach (/roi, /inwestycje).

Spec: ten sam stan bazy = ta sama kwota oszczędności i „pozostało do zwrotu”
na stronie ROI i na liście inwestycji. Wszystkie miejsca biorą
pod uwagę: okresy net-billingu, ceny RCE, współczynnik puli z ustawień
i oszczędność EV z ładowania domowego.
"""
import sqlite3
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, "src")
import main
import utils.db
from services.calculations import calc_roi


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(utils.db, "DB_PATH", tmp_path / "fv.db")
    monkeypatch.delenv("FV_AUTH_PASSWORD", raising=False)
    with TestClient(main.app) as c:
        con = sqlite3.connect(utils.db.DB_PATH)
        con.executescript("""
            UPDATE app_settings SET net_metering_ratio = 0.70;
            INSERT INTO investments (date, description, cost_pln, power_kwp)
                VALUES ('2024-01-15', 'Panele', 30000, 8.0);
            INSERT INTO billing_periods (start_date, end_date, model)
                VALUES ('2024-07-01', NULL, 'net_billing');
            INSERT INTO rce_prices (date, price_per_kwh) VALUES ('2024-07-01', 0.30);
            INSERT INTO fuel_prices (date, price_per_liter, fuel_type) VALUES ('2024-01-01', 6.50, 'PB95');
            INSERT INTO readings (period, year, month, production_kwh, sent_to_grid_kwh,
                                  taken_from_grid_kwh, ev_kwh, price_per_kwh)
            VALUES ('2024.05', 2024, 5, 900, 600, 300, 150, 0.80),
                   ('2024.06', 2024, 6, 1000, 700, 250, 150, 0.80),
                   ('2024.07', 2024, 7, 1100, 800, 200, 150, 0.80),
                   ('2024.08', 2024, 8, 950, 650, 280, 150, 0.80);
        """)
        con.commit()
        con.close()
        yield c


async def _reference_roi() -> dict:
    """ROI tak, jak liczy go strona /roi (pełny komplet parametrów)."""
    db = await utils.db.get_db()
    try:
        readings = await main._get_readings(db)
        investments = await main._get_investments(db)
        ev_settings = await main._get_ev_settings(db)
        fuel_prices = await main._get_fuel_prices(db)
        vehicles = await main._get_vehicles(db)
        ev_monthly = await main._get_ev_monthly_all(db)
        billing_periods = await main._get_billing_periods(db)
        rce_prices = await main._get_rce_prices(db)
    finally:
        await db.close()
    ev_monthly = main._inject_odometer_km(ev_monthly, vehicles)
    readings = main._ev_enrich(readings, ev_settings, fuel_prices, vehicles, ev_monthly)
    total = sum(i["cost_pln"] for i in investments)
    return calc_roi(readings, total, main._default_price(),
                    ev_settings["net_metering_ratio"], billing_periods, rce_prices)


async def test_investments_page_matches_roi_page(client):
    expected = await _reference_roi()

    html = client.get("/inwestycje").text

    assert main._fmt(expected["total_savings_pln"]) in html
    assert main._fmt(expected["remaining_to_roi"]) in html
