import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import sqlite3

import pytest


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Aplikacja na pustej bazie w katalogu tymczasowym, bez Basic Auth."""
    from fastapi.testclient import TestClient
    import main
    import utils.db
    monkeypatch.setattr(utils.db, "DB_PATH", tmp_path / "fv.db")
    monkeypatch.delenv("FV_AUTH_PASSWORD", raising=False)
    with TestClient(main.app) as c:
        yield c


@pytest.fixture
def seed(client):
    """Wykonuje SQL na bazie testowej aplikacji (po init_db)."""
    import utils.db

    def _run(sql: str) -> None:
        con = sqlite3.connect(utils.db.DB_PATH)
        con.executescript(sql)
        con.commit()
        con.close()
    return _run


@pytest.fixture
def query(client):
    """Zwraca wiersze z bazy testowej jako listę dict."""
    import utils.db

    def _q(sql: str, params: tuple = ()) -> list[dict]:
        con = sqlite3.connect(utils.db.DB_PATH)
        con.row_factory = sqlite3.Row
        rows = [dict(r) for r in con.execute(sql, params)]
        con.close()
        return rows
    return _q


@pytest.fixture
def post_form(client):
    """POST formularza z poprawnym tokenem CSRF (bez podążania za przekierowaniem)."""
    import main

    def _post(url: str, data: dict | None = None):
        return client.post(url, data={**(data or {}), "csrf_token": main._csrf_generate()},
                           follow_redirects=False)
    return _post
