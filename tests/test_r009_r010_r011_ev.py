"""R-009 Dodanie pojazdu (#27), R-010 Oszczędności EV (#28), R-011 Śledzenie cen paliwa (#29)."""
import asyncio
import sys

sys.path.insert(0, "src")
from services.calculations import calc_ev_savings

VEHICLE = {"name": "Auto 1", "efficiency_kwh_per_100km": "18", "fuel_consumption_l_per_100km": "7",
           "fuel_type": "PB95", "przebieg_km": "12000", "fuel_tracking": "1"}


# ── R-009 ──
def test_AC_009_1_pojazd_dodany(client, query, post_form):
    assert post_form("/ev/pojazdy/nowy", VEHICLE).status_code == 303
    (v,) = query("SELECT * FROM vehicles")
    assert (v["name"], v["efficiency_kwh_per_100km"], v["fuel_consumption_l_per_100km"], v["przebieg_km"]) == \
        ("Auto 1", 18, 7, 12000)
    assert "Auto 1" in client.get("/ev").text


def test_AC_009_2_bez_przebiegu_nie_dodany(client, query, post_form):
    post_form("/ev/pojazdy/nowy", {**VEHICLE, "przebieg_km": ""})
    assert query("SELECT * FROM vehicles") == []


# ── R-010 ──
def test_AC_010_1_oszczednosc_ev_z_fv_240_zl():
    ev = calc_ev_savings(180, 1.0, 18, 7, 6.0, km_driven=1000)
    assert ev["fuel_cost_equivalent"] == 420.0
    assert ev["ev_net_savings"] == 240.0


def test_AC_010_2_ladowanie_publiczne_poza_roi(client, seed, query, post_form):
    post_form("/ev/pojazdy/nowy", VEHICLE)
    vid = query("SELECT id FROM vehicles")[0]["id"]
    seed(f"""
        INSERT INTO investments (date, description, cost_pln) VALUES ('2024-01-01', 'Panele', 30000);
        INSERT INTO fuel_prices (date, price_per_liter, fuel_type) VALUES ('2024-01-01', 6.0, 'PB95');
        INSERT INTO readings (period, year, month, production_kwh, sent_to_grid_kwh, taken_from_grid_kwh, price_per_kwh)
            VALUES ('2024.05', 2024, 5, 500, 300, 200, 1.0);
        INSERT INTO ev_monthly (period, vehicle_id, kwh, km, public_kwh, public_km, public_cost_pln)
            VALUES ('2024.05', {vid}, 180, 1000, 50, 300, 60);
    """)
    import main, utils.db

    async def roi():
        db = await utils.db.get_db()
        try:
            return (await main._roi_state(db))[0]
        finally:
            await db.close()
    assert asyncio.run(roi())["total_ev_savings_pln"] == 240.0   # tylko ładowanie domowe
    html = client.get(f"/ev/pojazdy/{vid}").text
    assert "publiczn" in html.lower()                              # publiczne widoczne na stronie pojazdu


# ── R-011 ──
def test_AC_011_1_pierwszy_samochod_pyta_o_ceny_paliwa(client, post_form):
    q = "Czy chcesz śledzić ceny paliwa?"
    html = client.get("/ev").text
    assert q in html and 'type="radio" name="fuel_tracking"' in html
    post_form("/ev/pojazdy/nowy", VEHICLE)
    assert q not in client.get("/ev").text                          # przy kolejnym aucie już nie pyta


def test_AC_011_2_sledzenie_wlaczone_pozycja_menu(client, query, post_form):
    post_form("/ev/pojazdy/nowy", VEHICLE)
    assert query("SELECT fuel_tracking FROM app_settings")[0]["fuel_tracking"] == 1
    html = client.get("/").text
    assert 'href="/ev/ceny-paliwa"' in html
    page = client.get("/ev/ceny-paliwa").text
    for field in ('name="date"', 'name="price_per_liter"', 'name="fuel_type"', 'name="source"'):
        assert field in page, field


def test_AC_011_3_sledzenie_wylaczone_brak_pozycji(client, query, post_form):
    post_form("/ev/pojazdy/nowy", {**VEHICLE, "fuel_tracking": "0"})
    assert query("SELECT fuel_tracking FROM app_settings")[0]["fuel_tracking"] == 0
    assert "/ev/ceny-paliwa" not in client.get("/").text
    assert "/ev/ceny-paliwa" not in client.get("/ev").text
    assert client.get("/ev/ceny-paliwa", follow_redirects=False).status_code == 303


def test_cena_paliwa_dodana_przez_strone(client, query, post_form):
    post_form("/ev/pojazdy/nowy", VEHICLE)
    r = post_form("/ev/fuel-price", {"date": "2024-05-01", "price_per_liter": "6.29", "fuel_type": "PB95", "source": "Orlen"})
    assert r.status_code == 303
    assert query("SELECT source FROM fuel_prices")[0]["source"] == "Orlen"


def test_AC_011_4_wlacz_i_wylacz_sledzenie_pozniej(client, query, post_form):
    post_form("/ev/pojazdy/nowy", {**VEHICLE, "fuel_tracking": "0"})
    post_form("/ev/fuel-tracking", {"fuel_tracking": "1"})
    assert query("SELECT fuel_tracking FROM app_settings")[0]["fuel_tracking"] == 1
    assert 'href="/ev/ceny-paliwa"' in client.get("/").text
    post_form("/ev/fuel-tracking", {"fuel_tracking": "0"})
    assert 'href="/ev/ceny-paliwa"' not in client.get("/").text


def test_istniejaca_instalacja_z_pojazdem_ma_sledzenie_wlaczone(client, seed, query):
    seed("""UPDATE app_settings SET fuel_tracking = NULL;
            INSERT INTO vehicles (name, efficiency_kwh_per_100km, fuel_consumption_l_per_100km, przebieg_km)
            VALUES ('Stare auto', 16, 8, 1000);""")
    import utils.db
    asyncio.run(utils.db.init_db())
    assert query("SELECT fuel_tracking FROM app_settings")[0]["fuel_tracking"] == 1
