import os
import aiosqlite
from pathlib import Path

_data_dir = Path(os.environ.get("DATA_PATH", Path(__file__).parent.parent.parent / "data"))
DB_PATH = _data_dir / "fv.db"


async def get_db() -> aiosqlite.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db() -> None:
    DB_PATH.parent.mkdir(exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS investments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                cost_pln REAL NOT NULL,
                power_kwp REAL,
                notes TEXT
            );

            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                period TEXT NOT NULL UNIQUE,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                days INTEGER,
                production_kwh REAL NOT NULL,
                sent_to_grid_kwh REAL NOT NULL,
                taken_from_grid_kwh REAL NOT NULL,
                ev_kwh REAL,
                price_per_kwh REAL,
                invoice_number TEXT,
                invoice_gross REAL,
                notes TEXT
            );

            CREATE TABLE IF NOT EXISTS ev_settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                efficiency_kwh_per_100km REAL NOT NULL DEFAULT 16.0,
                fuel_consumption_l_per_100km REAL NOT NULL DEFAULT 10.0,
                annual_km REAL NOT NULL DEFAULT 25000,
                fuel_type TEXT NOT NULL DEFAULT 'PB95',
                ha_url TEXT,
                ha_token TEXT,
                ha_entity TEXT
            );

            INSERT OR IGNORE INTO ev_settings (id) VALUES (1);

            CREATE TABLE IF NOT EXISTS fuel_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                price_per_liter REAL NOT NULL,
                fuel_type TEXT NOT NULL DEFAULT 'PB95',
                source TEXT
            );
        """)
        await db.commit()
