"""R-009 Dodanie pojazdu (#27) - zmiana przebiegu startowego (D-027, BR-012).

Przy zapisanych stanach licznika aplikacja pyta, czy przesunąć je o różnicę.
Tak: stany przesunięte, km bez zmian. Nie: zmienia się tylko start, stany licznika
niższe niż nowa wartość są usuwane (dane ładowania zostają).
"""
FORM = {"name": "Auto", "efficiency_kwh_per_100km": "18", "fuel_consumption_l_per_100km": "7",
        "fuel_type": "PB95", "notes": "", "date_from": "", "date_to": ""}


def _seed(seed):
    seed("""
        INSERT INTO vehicles (id, name, efficiency_kwh_per_100km, fuel_consumption_l_per_100km, fuel_type, przebieg_km)
            VALUES (1, 'Auto', 18, 7, 'PB95', 12000);
        INSERT INTO ev_monthly (period, vehicle_id, kwh, odometer_km, public_kwh) VALUES
            ('2026.01', 1, 150, 13000, 20), ('2026.02', 1, 180, 14200, NULL);
    """)


def _km(query):
    import main
    v = query("SELECT * FROM vehicles WHERE id=1")
    ev = query("SELECT * FROM ev_monthly WHERE vehicle_id=1 ORDER BY period")
    return {e["period"]: e["km"] for e in main._inject_odometer_km(ev, v)}


def _odo(query):
    return {e["period"]: e["odometer_km"] for e in query("SELECT * FROM ev_monthly ORDER BY period")}


def test_AC_009_3_zmiana_bez_wyboru_pokazuje_ostrzezenie_i_nie_zapisuje(client, seed, query, post_form):
    _seed(seed)
    r = post_form("/ev/pojazdy/1/edytuj", {**FORM, "przebieg_km": "12500"})
    assert r.status_code == 200
    assert "przeliczy" in r.text and 'name="odometer_shift"' in r.text and "csrf_token" in r.text
    assert query("SELECT przebieg_km FROM vehicles")[0]["przebieg_km"] == 12000
    assert _odo(query) == {"2026.01": 13000, "2026.02": 14200}


def test_AC_009_3_tak_przesuwa_stany_licznika_km_bez_zmian(client, seed, query, post_form):
    _seed(seed)
    r = post_form("/ev/pojazdy/1/edytuj", {**FORM, "przebieg_km": "12500", "odometer_shift": "shift"})
    assert r.status_code == 303
    assert query("SELECT przebieg_km FROM vehicles")[0]["przebieg_km"] == 12500
    assert _odo(query) == {"2026.01": 13500, "2026.02": 14700}
    assert _km(query) == {"2026.01": 1000.0, "2026.02": 1200.0}


def test_AC_009_4_nie_usuwa_nizsze_stany_licznika_dane_ladowania_zostaja(client, seed, query, post_form):
    _seed(seed)
    r = post_form("/ev/pojazdy/1/edytuj", {**FORM, "przebieg_km": "13500", "odometer_shift": "keep"})
    assert r.status_code == 303
    assert query("SELECT przebieg_km FROM vehicles")[0]["przebieg_km"] == 13500
    assert _odo(query) == {"2026.01": None, "2026.02": 14200}
    (jan,) = query("SELECT kwh, public_kwh FROM ev_monthly WHERE period='2026.01'")
    assert (jan["kwh"], jan["public_kwh"]) == (150, 20)
    assert _km(query)["2026.02"] == 700.0


def test_bez_zmiany_przebiegu_zapis_bez_ostrzezenia(client, seed, query, post_form):
    _seed(seed)
    r = post_form("/ev/pojazdy/1/edytuj", {**FORM, "name": "Nowa nazwa", "przebieg_km": "12000"})
    assert r.status_code == 303
    assert query("SELECT name FROM vehicles")[0]["name"] == "Nowa nazwa"


def test_bez_stanow_licznika_zapis_bez_ostrzezenia(client, seed, query, post_form):
    seed("""INSERT INTO vehicles (id, name, efficiency_kwh_per_100km, fuel_consumption_l_per_100km, fuel_type, przebieg_km)
            VALUES (1, 'Auto', 18, 7, 'PB95', 12000);""")
    r = post_form("/ev/pojazdy/1/edytuj", {**FORM, "przebieg_km": "15000"})
    assert r.status_code == 303
    assert query("SELECT przebieg_km FROM vehicles")[0]["przebieg_km"] == 15000
