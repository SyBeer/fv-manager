"""R-002 Oszczędność PV miesiąca (#18) i R-003 Miesiąc startu cyklu rozliczeniowego (#19)."""
import sys

sys.path.insert(0, "src")
from services.calculations import calc_monthly, calc_monthly_netbilling, enrich_readings_sequence


def _r(period, prod, sent, taken, **kw):
    return {"period": period, "production_kwh": prod, "sent_to_grid_kwh": sent,
            "taken_from_grid_kwh": taken, "price_per_kwh": 1.0, **kw}


# ── R-002 ──
def test_AC_002_1_net_metering_pula():
    c = calc_monthly(500, 300, 200, 1.0, carry_over_in=0.0, net_metering_ratio=0.80)
    assert c["auto_consumption"] == 200
    assert c["net_metering_pool"] == 240
    assert c["savings_kwh"] == 200 + 200          # autokonsumpcja + 200 kWh z puli
    assert c["carry_over_out"] == 40


def test_AC_002_2_pula_zeruje_sie_w_kwietniu():
    seq = enrich_readings_sequence(
        [_r("2024.03", 500, 300, 200), _r("2024.04", 0, 0, 100)], 0.80, 1.0, [], [], 4)
    assert seq[0]["carry_over_out"] == 40
    assert seq[1]["savings_kwh"] == 0              # pula z marca nie przechodzi na kwiecień


def test_AC_002_3_net_billing_320_zl():
    c = calc_monthly_netbilling(500, 300, 200, 1.0, 0.40)
    assert c["auto_consumption"] == 200
    assert c["savings_pln"] == 320.0


def test_AC_002_4_cena_sprzedazy_nadpisuje_rce():
    periods = [{"start_date": "2024-07-01", "end_date": None, "model": "net_billing"}]
    rce = [{"date": "2024-07-01", "price_per_kwh": 0.40}]
    (r,) = enrich_readings_sequence([_r("2024.08", 500, 300, 200, sale_price_kwh=0.50)],
                                    0.80, 1.0, periods, rce)
    assert r["net_billing_income_pln"] == 150.0


# ── R-003 ──
def test_AC_003_1_domyslnie_kwiecien(client, query):
    (s,) = query("SELECT cycle_start_month FROM app_settings WHERE id = 1")
    assert s["cycle_start_month"] == 4


def test_AC_003_2_ustawiony_czerwiec_zeruje_pule_w_czerwcu(client, seed, query, post_form):
    r = post_form("/pv/settings", {"panel_degradation_rate_pct": "0.6", "cycle_start_month": "6"})
    assert r.status_code == 303
    assert query("SELECT cycle_start_month FROM app_settings")[0]["cycle_start_month"] == 6
    # pula 40 kWh z kwietnia i maja przechodzi przez kwiecień, zeruje się w czerwcu
    seed("""
        INSERT INTO readings (period, year, month, production_kwh, sent_to_grid_kwh, taken_from_grid_kwh, price_per_kwh)
        VALUES ('2024.03', 2024, 3, 500, 300, 200, 1.0),
               ('2024.04', 2024, 4, 0, 0, 10, 1.0),
               ('2024.06', 2024, 6, 0, 0, 10, 1.0);
    """)
    html = client.get("/odczyty").text
    # kwiecień korzysta z puli (10 kWh oszczędności), czerwiec już nie (0 kWh)
    import main, asyncio, utils.db
    async def run():
        db = await utils.db.get_db()
        try:
            return await main._enriched_readings(db)
        finally:
            await db.close()
    by = {r["period"]: r for r in asyncio.run(run())}
    assert by["2024.04"]["savings_kwh"] == 10
    assert by["2024.06"]["savings_kwh"] == 0
    assert html  # strona renderuje się z ustawieniem


def test_AC_003_niepoprawny_miesiac_odrzucony(client, query, post_form):
    post_form("/pv/settings", {"panel_degradation_rate_pct": "0.6", "cycle_start_month": "13"})
    assert query("SELECT cycle_start_month FROM app_settings")[0]["cycle_start_month"] == 4


def test_AC_003_pole_w_ustawieniach_pv(client):
    html = client.get("/pv").text
    assert 'name="cycle_start_month"' in html
    assert '<option value="4" selected>kwiecień</option>' in " ".join(html.split())
