"""R-016 Poprawki tekstów (#33), R-018 Wycofanie Tesla Fleet API (#34)."""
import asyncio
import re
import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")


def _flat(html: str) -> str:
    return " ".join(re.sub(r"<[^>]+>", " ", html).split())


# ── R-016 ──
def test_AC_016_1_rce_i_paliwo_recznie(client):
    text = _flat(client.get("/metodologia").text)
    assert "pobiera automatycznie" not in text.lower() or "RCE" not in text.split("pobiera automatycznie")[1][:200]
    assert re.search(r"ceny RCE.{0,80}wpisujesz ręcznie|wpisujesz ręcznie.{0,120}ceny RCE", text, re.I)
    assert re.search(r"ceny paliwa.{0,80}wpisujesz ręcznie|wpisujesz ręcznie.{0,160}ceny paliwa", text, re.I)


def test_AC_016_2_pula_w_cyklu(client):
    text = _flat(client.get("/metodologia").text).lower()
    assert "przechodzi na kolejny miesiąc" in text and "miesiącu startu cyklu" in text
    readme = README.lower()
    assert "przechodzi na kolejny miesiąc" in readme and "miesiącu startu cyklu" in readme


def test_AC_016_3_wrazliwosc_7_cen_i_wspolczynnik(client, seed):
    seed("""UPDATE app_settings SET net_metering_ratio = 0.7;
            INSERT INTO investments (date, description, cost_pln) VALUES ('2024-01-01', 'P', 30000);
            INSERT INTO readings (period, year, month, production_kwh, sent_to_grid_kwh, taken_from_grid_kwh, price_per_kwh)
            VALUES ('2024.05', 2024, 5, 500, 300, 200, 1.0);""")
    roi = _flat(client.get("/roi").text)
    assert "×0.8" not in roi
    assert "współczynnik puli 0.7" in roi
    text = _flat(client.get("/metodologia").text)
    assert "wzrost o 20%" not in text
    assert "7 stałych cen" in text


def test_AC_016_4_readme_przyklad_csv():
    block = README[README.index("### Format CSV"):]
    example = block[block.index("```") + 3: block.index("```", block.index("```") + 3)]
    first = example.strip().splitlines()[0]
    assert first.startswith("Okres;") and "Produkcja [kWh]" in first


def test_AC_016_5_metodologia_bez_dat_ustawowych(client):
    text = _flat(client.get("/metodologia").text)
    assert not re.search(r"VII 2022|2022|1\.07\.2024|lipca 2024", text)
    assert "okres" in text.lower() and "umow" in text.lower()


# ── R-018 ──
def test_AC_018_1_brak_tesla_w_kodzie():
    out = subprocess.run(["grep", "-rli", "tesla", "src", "templates", "--include=*.py", "--include=*.html"],
                         cwd=ROOT, capture_output=True, text=True).stdout.split()
    assert out == ["src/utils/db.py"], out          # tylko migracja usuwająca kolumny
    db_src = (ROOT / "src/utils/db.py").read_text()
    assert all("DROP COLUMN" in l or "for col in" in l for l in db_src.splitlines() if "tesla" in l.lower())


def test_AC_018_2_readme_i_changelog():
    assert "tesla" not in README.lower()
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    top = changelog[: changelog.index("## [3.2.5]")]
    assert "Tesla Fleet API" in top and "wycofan" in top.lower()


def test_AC_018_3_migracja_nie_rusza_danych(tmp_path, monkeypatch):
    import utils.db
    db_path = tmp_path / "stara.db"
    monkeypatch.setattr(utils.db, "DB_PATH", db_path)
    asyncio.run(utils.db.init_db())
    con = sqlite3.connect(db_path)
    for col in ("tesla_access_token", "tesla_site_id", "tesla_api_base"):
        con.execute(f"ALTER TABLE app_settings ADD COLUMN {col} TEXT")
    con.executescript("""
        UPDATE app_settings SET tesla_access_token = 'tok', tesla_site_id = '123';
        INSERT INTO readings (period, year, month, production_kwh, sent_to_grid_kwh, taken_from_grid_kwh)
            VALUES ('2024.01', 2024, 1, 500, 300, 200);
        INSERT INTO vehicles (name, efficiency_kwh_per_100km, fuel_consumption_l_per_100km, przebieg_km)
            VALUES ('Auto', 16, 8, 1000);
    """)
    con.commit()
    con.close()
    asyncio.run(utils.db.init_db())
    con = sqlite3.connect(db_path)
    cols = [r[1] for r in con.execute("PRAGMA table_info(app_settings)")]
    assert not any(c.startswith("tesla") for c in cols)
    assert con.execute("SELECT COUNT(*) FROM readings").fetchone()[0] == 1
    assert con.execute("SELECT COUNT(*) FROM vehicles").fetchone()[0] == 1
    con.close()
