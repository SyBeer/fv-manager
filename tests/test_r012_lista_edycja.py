"""R-012 Lista i edycja odczytów (#22). Weryfikacja działania obecnego."""

SEED = """
    INSERT INTO investments (date, description, cost_pln) VALUES ('2023-01-01', 'Panele', 30000);
    INSERT INTO readings (period, year, month, production_kwh, sent_to_grid_kwh, taken_from_grid_kwh, price_per_kwh)
    VALUES ('2024.01', 2024, 1, 300, 100, 400, 1.0),
           ('2024.02', 2024, 2, 400, 150, 350, 1.0),
           ('2024.03', 2024, 3, 600, 300, 250, 1.0);
"""


def test_AC_012_1_kolumny_listy(client, seed):
    seed(SEED)
    html = client.get("/odczyty").text
    for col in ("Produkcja", "Autokons.", "Oddane", "Pobrane", "Zużycie", "Oszczędności [zł]"):
        assert col in html, col
    for period in ("2024.01", "2024.02", "2024.03"):
        assert period in html


def test_AC_012_2_podglad_roi_przed_i_po(client, seed, query):
    seed(SEED)
    rid = query("SELECT id FROM readings WHERE period='2024.03'")[0]["id"]
    r = client.post("/api/roi-preview", json={"id": rid, "production_kwh": 900})
    assert r.status_code == 200
    data = r.json()
    assert data["after"]["total_savings_pln"] > data["before"]["total_savings_pln"]
    assert data["after"]["remaining_to_roi"] < data["before"]["remaining_to_roi"]


def test_formularz_edycji_wola_podglad(client, seed, query):
    seed(SEED)
    rid = query("SELECT id FROM readings WHERE period='2024.03'")[0]["id"]
    assert "/api/roi-preview" in client.get(f"/odczyty/{rid}/edytuj").text
