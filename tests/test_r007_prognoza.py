"""R-007 Prognoza zwrotu (#25; D-013, D-019)."""
import re
import sys

sys.path.insert(0, "src")
from services.forecast import apply_degradation


def test_AC_007_1_degradacja_488_1():
    assert round(apply_degradation(500.0, "2022-06-01", "2026.06", 0.006), 1) == 488.1


def test_AC_007_2_domyslna_degradacja_w_ustawieniach(client):
    html = client.get("/pv").text
    assert re.search(r'name="panel_degradation_rate_pct"[^>]*value="0\.6"', " ".join(html.split()))


def _seed_long_payback(seed, cost: int):
    rows = ",".join(f"('{y}.{m:02d}', {y}, {m}, 300, 100, 300, 1.0)" for y in (2024, 2025) for m in range(1, 13))
    seed(f"""
        INSERT INTO investments (date, description, cost_pln, power_kwp) VALUES ('2023-12-01', 'Panele', {cost}, 6.0);
        INSERT INTO readings (period, year, month, production_kwh, sent_to_grid_kwh, taken_from_grid_kwh, price_per_kwh)
        VALUES {rows};
    """)


def test_AC_007_3_tabela_scenariuszy_zwrot_po_36_mies(client, seed):
    _seed_long_payback(seed, 40000)   # ok. 300 zł/mies. -> zwrot po ponad 36 mies.
    html = " ".join(client.get("/roi").text.split())
    table = html[html.index("Break-even przy różnym"):]
    found = [int(n) for n in re.findall(r"zwrot za (\d+) mies\.", table)]
    assert len(found) >= 4, found                     # każdy z 4 scenariuszy
    assert all(n > 36 for n in found[:4])
    # wykres prognozy nadal 36 miesięcy
    labels = re.search(r"const fLabels = (\[.*?\]);", html).group(1)
    assert labels.count('"') // 2 == 36
