"""Smoke: każda strona HTML otwiera się bez błędu na pełnym zestawie danych."""
import pytest

FULL = """
    INSERT INTO investments (date, description, cost_pln, power_kwp) VALUES
        ('2021-09-15', 'Panele', 30000, 6.0), ('2021-11-01', 'Dofinansowanie', -5000, NULL),
        ('2024-03-01', 'Magazyn', 12000, 6.0);
    INSERT INTO vehicles (id, name, efficiency_kwh_per_100km, fuel_consumption_l_per_100km, przebieg_km, date_from)
        VALUES (1, 'Auto', 18, 7, 12000, '2022-01-01');
    INSERT INTO fuel_prices (date, price_per_liter, fuel_type) VALUES ('2022-01-01', 6.2, 'PB95');
    INSERT INTO billing_periods (start_date, model) VALUES ('2025-07-01', 'net_billing');
    INSERT INTO rce_prices (date, price_per_kwh) VALUES ('2025-07-01', 0.35);
    UPDATE app_settings SET fuel_tracking = 1, cycle_start_month = 5;
"""


@pytest.fixture
def full(client, seed):
    rows, ev = [], []
    for y in range(2021, 2026):
        for m in range(1, 13):
            if (y, m) < (2021, 10):
                continue
            rows.append(f"('{y}.{m:02d}', {y}, {m}, {200 + 40 * (6 - abs(6 - m))}, 120, 250, 0.9)")
            ev.append(f"('{y}.{m:02d}', 1, 150, 800, 20, 100, 30)")
    seed(FULL + f"""
        INSERT INTO readings (period, year, month, production_kwh, sent_to_grid_kwh, taken_from_grid_kwh, price_per_kwh)
            VALUES {",".join(rows)};
        INSERT INTO ev_monthly (period, vehicle_id, kwh, km, public_kwh, public_km, public_cost_pln)
            VALUES {",".join(ev)};
    """)
    import main
    main._FUEL_TRACKING = True
    return client


@pytest.mark.parametrize("path", ["/", "/odczyty", "/odczyty/nowy", "/inwestycje", "/roi", "/ev",
                                  "/ev/pojazdy/1", "/ev/ceny-paliwa", "/pv", "/import", "/metodologia",
                                  "/odczyty/export.csv", "/backup/full"])
def test_strona_otwiera_sie(full, path):
    r = full.get(path)
    assert r.status_code == 200, (path, r.text[:300])
