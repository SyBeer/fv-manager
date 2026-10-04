"""R-006 Pozostało do zwrotu (PRD 03-spec/PRD.md, Redmine #24).

Etap inwestycji liczy się od miesiąca swojej daty (D-015); etap sprzed
pierwszego odczytu - od pierwszego miesiąca z odczytem (D-021).
"""
import sys

sys.path.insert(0, "src")
from services.calculations import calc_roi, investment_as_of, roi_chart_series


def _readings(n: int, start_year: int = 2022, start_month: int = 1, ev_pln: float = 0.0,
              public_pln: float = 0.0) -> list[dict]:
    """n odczytów: 500 kWh autokonsumpcji x 1,00 zł = 500 zł oszczędności PV na miesiąc."""
    out = []
    y, m = start_year, start_month
    for _ in range(n):
        out.append({
            "period": f"{y}.{m:02d}", "production_kwh": 500.0, "sent_to_grid_kwh": 0.0,
            "taken_from_grid_kwh": 0.0, "price_per_kwh": 1.0,
            "ev_savings_pln": ev_pln, "ev_public_savings_pln": public_pln,
        })
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return out


def test_AC_006_1_pozostalo_bez_ladowania_publicznego():
    # 30 mies. x 500 zł = 15 000 zł PV; 30 x 100 zł = 3 000 zł EV z FV; publiczne 2 000 zł poza ROI
    readings = _readings(30, ev_pln=100.0, public_pln=2000.0 / 30)
    roi = calc_roi(readings, 40000.0, 1.0)
    assert roi["total_fv_savings_pln"] == 15000.0
    assert roi["total_ev_savings_pln"] == 3000.0
    assert roi["remaining_to_roi"] == 22000.0


def test_AC_006_2_zwrot_osiagniety():
    roi = calc_roi(_readings(30), 15000.0, 1.0)
    assert roi["roi_achieved"] is True


def test_AC_006_3_inwestycja_schodkowo_wg_dat_etapow():
    investments = [
        {"date": "2022-06-01", "cost_pln": 30000.0},
        {"date": "2025-03-10", "cost_pln": 10000.0},
    ]
    assert investment_as_of(investments, "2024.12") == 30000.0
    assert investment_as_of(investments, "2025.03") == 40000.0

    series = roi_chart_series(_readings(36, 2022, 6), investments)
    by_period = {p["period"]: p for p in series}
    assert by_period["2024.12"]["investment"] == 30000.0
    assert by_period["2025.03"]["investment"] == 40000.0


def test_AC_006_4_miesiace_do_zwrotu_z_karty():
    # pozostało 22 000 zł, średnia oszczędność 500 zł/mies. -> 44 mies.
    roi = calc_roi(_readings(30), 37000.0, 1.0)
    assert roi["remaining_to_roi"] == 22000.0
    assert roi["avg_monthly_savings"] == 500.0
    assert roi["months_to_roi"] == 44


def test_AC_006_5_etap_sprzed_pierwszego_odczytu():
    investments = [{"date": "2021-09-15", "cost_pln": 30000.0}]
    series = roi_chart_series(_readings(3, 2021, 10), investments)
    assert series[0]["period"] == "2021.10"
    assert series[0]["investment"] == 30000.0


def test_dofinansowanie_obniza_inwestycje_od_swojej_daty():
    investments = [
        {"date": "2022-06-01", "cost_pln": 30000.0},
        {"date": "2022-09-01", "cost_pln": -5000.0},
    ]
    assert investment_as_of(investments, "2022.08") == 30000.0
    assert investment_as_of(investments, "2022.09") == 25000.0


# ── Ekran /roi: wykres pokazuje inwestycję schodkowo (AC-006-3 na poziomie strony) ──
import json
import re


def test_AC_006_3_wykres_roi_inwestycja_schodkowo(client, seed):
    rows = ",".join(
        f"('{y}.{m:02d}', {y}, {m}, 500, 0, 0, 1.0)"
        for y in (2024, 2025) for m in range(1, 13)
    )
    seed(f"""
        INSERT INTO investments (date, description, cost_pln, power_kwp) VALUES
            ('2022-06-01', 'Panele', 30000, 6.0), ('2025-03-10', 'Magazyn', 10000, NULL);
        INSERT INTO readings (period, year, month, production_kwh, sent_to_grid_kwh,
                              taken_from_grid_kwh, price_per_kwh) VALUES {rows};
    """)
    html = client.get("/roi").text
    labels = json.loads(re.search(r"const labels = (\[.*?\]);", html).group(1))
    series = json.loads(re.search(r"const investmentSeries = (\[.*?\]);", html).group(1))
    inv = dict(zip(labels, series))
    assert inv["2024.12"] == 30000.0
    assert inv["2025.03"] == 40000.0
