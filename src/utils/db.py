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
        # Migration: ev_settings → app_settings (must run before CREATE TABLE app_settings)
        try:
            await db.execute("ALTER TABLE ev_settings RENAME TO app_settings")
            await db.commit()
        except Exception:
            pass

        await db.executescript("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TEXT NOT NULL DEFAULT (datetime('now')),
                description TEXT
            );
            INSERT OR IGNORE INTO schema_version (version, description) VALUES (1, 'initial');

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
                sale_price_kwh REAL,
                invoice_number TEXT,
                invoice_gross REAL,
                notes TEXT
            );

            CREATE TABLE IF NOT EXISTS app_settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                efficiency_kwh_per_100km REAL NOT NULL DEFAULT 16.0,
                fuel_consumption_l_per_100km REAL NOT NULL DEFAULT 10.0,
                annual_km REAL NOT NULL DEFAULT 25000,
                fuel_type TEXT NOT NULL DEFAULT 'PB95',
                ha_url TEXT,
                ha_entity TEXT,
                net_metering_ratio REAL NOT NULL DEFAULT 0.80,
                panel_degradation_rate REAL NOT NULL DEFAULT 0.006
            );

            INSERT OR IGNORE INTO app_settings (id) VALUES (1);

            CREATE TABLE IF NOT EXISTS fuel_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                price_per_liter REAL NOT NULL,
                fuel_type TEXT NOT NULL DEFAULT 'PB95',
                source TEXT
            );

            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                efficiency_kwh_per_100km REAL NOT NULL DEFAULT 16.0,
                fuel_consumption_l_per_100km REAL NOT NULL DEFAULT 10.0,
                fuel_type TEXT NOT NULL DEFAULT 'PB95',
                notes TEXT,
                date_from TEXT,
                date_to TEXT,
                przebieg_km REAL
            );

            CREATE TABLE IF NOT EXISTS ev_monthly (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                period TEXT NOT NULL,
                vehicle_id INTEGER NOT NULL REFERENCES vehicles(id),
                kwh REAL NOT NULL,
                km REAL,
                UNIQUE(period, vehicle_id)
            );

            CREATE TABLE IF NOT EXISTS billing_periods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_date TEXT NOT NULL,
                end_date   TEXT,
                model      TEXT NOT NULL CHECK (model IN ('net_metering', 'net_billing')),
                description TEXT
            );

            CREATE TABLE IF NOT EXISTS rce_prices (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                date          TEXT NOT NULL,
                price_per_kwh REAL NOT NULL,
                source        TEXT
            );
        """)

        # Migrations — safe ALTER TABLE for columns added after initial deploy
        for col, definition in [
            ("ev_kwh", "REAL"),
            ("sale_price_kwh", "REAL"),
        ]:
            try:
                await db.execute(f"ALTER TABLE readings ADD COLUMN {col} {definition}")
                await db.commit()
            except Exception:
                pass

        try:
            await db.execute("ALTER TABLE ev_monthly ADD COLUMN km REAL")
            await db.commit()
        except Exception:
            pass

        for col in ["date_from", "date_to"]:
            try:
                await db.execute(f"ALTER TABLE vehicles ADD COLUMN {col} TEXT")
                await db.commit()
            except Exception:
                pass

        try:
            await db.execute("ALTER TABLE vehicles ADD COLUMN przebieg_km REAL")
            await db.commit()
        except Exception:
            pass

        for col, definition in [
            ("ha_solar_entity", "TEXT"),
            ("ha_grid_consumed_entity", "TEXT"),
            ("ha_grid_returned_entity", "TEXT"),
            ("net_metering_ratio", "REAL NOT NULL DEFAULT 0.80"),
            ("panel_degradation_rate", "REAL NOT NULL DEFAULT 0.006"),
        ]:
            try:
                await db.execute(f"ALTER TABLE app_settings ADD COLUMN {col} {definition}")
                await db.commit()
            except Exception:
                pass

        # Record rename migration
        try:
            await db.execute(
                "INSERT OR IGNORE INTO schema_version (version, description) VALUES (2, 'rename ev_settings to app_settings')"
            )
            await db.commit()
        except Exception:
            pass

        try:
            await db.execute(
                "INSERT OR IGNORE INTO schema_version (version, description) VALUES (3, 'add billing_periods, rce_prices, readings.sale_price_kwh')"
            )
            await db.commit()
        except Exception:
            pass

        # Drop dead columns from existing databases (SQLite >= 3.35.0)
        try:
            await db.execute("ALTER TABLE app_settings DROP COLUMN ha_token")
            await db.commit()
        except Exception:
            pass
        for col in ("tesla_access_token", "tesla_site_id", "tesla_api_base"):
            try:
                await db.execute(f"ALTER TABLE app_settings DROP COLUMN {col}")
                await db.commit()
            except Exception:
                pass

        await db.commit()
