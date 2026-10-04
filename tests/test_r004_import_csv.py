"""R-004 Import odczytów z CSV - cały plik albo nic (#21, D-009, BR-002)."""
import main

HEADER = "Okres;Rok;Miesiąc;Dni;Produkcja [kWh];Oddane [kWh];Pobrane [kWh];Cena kWh [zł]"


def _csv(rows: list[str]) -> bytes:
    return ("\n".join([HEADER, *rows]) + "\n").encode("utf-8")


def _row(y: int, m: int, prod="500", sent="300", taken="200") -> str:
    return f"{y}.{m:02d};{y};{m};30;{prod};{sent};{taken};1,05"


def _upload(client, content: bytes):
    return client.post("/import/csv", data={"csrf_token": main._csrf_generate()},
                       files={"file": ("odczyty.csv", content, "text/csv")}, follow_redirects=False)


def test_import_przechodzi_csrf_multipart(client):
    assert _upload(client, _csv([])).status_code != 403


def test_import_bez_tokenu_odrzucony(client):
    r = client.post("/import/csv", files={"file": ("a.csv", _csv([]), "text/csv")}, follow_redirects=False)
    assert r.status_code == 403


def test_AC_004_1_dziesiec_poprawnych_wierszy(client, query):
    r = _upload(client, _csv([_row(2024, m) for m in range(1, 11)]))
    assert r.status_code == 303
    assert "imported=10" in r.headers["location"]
    rows = query("SELECT period, price_per_kwh FROM readings ORDER BY period")
    assert len(rows) == 10
    assert rows[0]["price_per_kwh"] == 1.05          # przecinek dziesiętny


def test_AC_004_2_blad_w_wierszu_4_nic_nie_zapisane(client, query):
    rows = [_row(2024, m) for m in range(1, 6)]
    rows[2] = _row(2024, 3, prod="-10")              # 3. wiersz danych = wiersz 4 pliku (1 = nagłówek)
    r = _upload(client, _csv(rows))
    assert r.status_code == 200
    assert query("SELECT * FROM readings") == []
    assert "wiersz 4" in r.text
    assert "ujemna" in r.text.lower()


def test_raport_wymienia_wszystkie_bledne_wiersze(client, query):
    rows = [_row(2024, 1), "2024-2;2024;2;30;500;300;200;1", _row(2024, 3, prod="100", sent="200")]
    r = _upload(client, _csv(rows))
    assert query("SELECT * FROM readings") == []
    assert "wiersz 3" in r.text and "wiersz 4" in r.text
    assert "wiersz 2" not in r.text


def test_istniejacy_okres_pomijany_jak_dzis(client, seed, query):
    seed("INSERT INTO readings (period, year, month, production_kwh, sent_to_grid_kwh, taken_from_grid_kwh) "
         "VALUES ('2024.01', 2024, 1, 999, 1, 1)")
    r = _upload(client, _csv([_row(2024, 1), _row(2024, 2)]))
    assert r.status_code == 303
    assert "imported=1" in r.headers["location"] and "skipped=1" in r.headers["location"]
    assert query("SELECT production_kwh FROM readings WHERE period='2024.01'")[0]["production_kwh"] == 999
