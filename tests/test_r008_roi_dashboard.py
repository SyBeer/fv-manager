"""R-008 Ekran ROI i dashboard (#26)."""
import re


def _flat(html: str) -> str:
    return " ".join(html.replace(" ", " ").split())


def _card(html: str, label: str) -> str:
    """Wartość karty stat-value stojącej bezpośrednio przed etykietą."""
    m = re.findall(r'class="stat-value"[^>]*>((?:(?!stat-value).)*?)</div> <div class="stat-label">'
                   + re.escape(label), html)
    assert m, label
    return re.sub(r"<[^>]+>", "", m[-1]).strip()


def _seed(seed, months: int, cost: int):
    rows = []
    y, m = 2024, 1
    for _ in range(months):
        rows.append(f"('{y}.{m:02d}', {y}, {m}, 500, 0, 0, 1.0)")   # 500 zł oszczędności / mies.
        m += 1
        if m > 12:
            y, m = y + 1, 1
    seed(f"""
        INSERT INTO investments (date, description, cost_pln, power_kwp) VALUES ('2023-12-01', 'Panele', {cost}, 6.0);
        INSERT INTO readings (period, year, month, production_kwh, sent_to_grid_kwh, taken_from_grid_kwh, price_per_kwh)
        VALUES {",".join(rows)};
    """)


def test_AC_008_1_karty_wykres_wrazliwosc(client, seed):
    _seed(seed, 10, 27000)          # 5 000 zł oszczędności, pozostało 22 000 zł, 44 mies.
    html = _flat(client.get("/roi").text)
    assert _card(html, "Łączna inwestycja") == "27 000 zł"
    assert _card(html, "Łączne oszczędności") == "5 000 zł"
    assert _card(html, "Pozostało do zwrotu") == "22 000 zł"
    assert _card(html, "Mies. do ROI") == "44 mies."
    assert 'id="roiChart"' in html
    for price in ("0.50", "0.60", "0.70", "0.80", "0.90", "1.00", "1.20"):
        assert f"<strong>{price}</strong>" in html, price


def test_AC_008_2_dashboard_baner_i_12_miesiecy(client, seed):
    _seed(seed, 15, 27000)
    html = _flat(client.get("/").text)
    assert "Do zwrotu inwestycji" in html
    assert "Ostatnie 12 miesięcy" in html
    assert "2025.03" in html and "2024.03" not in html   # tylko 12 ostatnich


def test_AC_008_3_dashboard_po_36_miesiacach(client, seed):
    _seed(seed, 10, 29000)          # pozostało 24 000 zł / 500 zł = 48 mies.
    html = _flat(client.get("/").text)
    assert _card(html, "Do zwrotu inwestycji") == "48 mies."
