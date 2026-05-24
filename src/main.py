import calendar
import os
import re
import secrets as _secrets
import base64
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def _ha_conn() -> tuple[str, str]:
    """Return (base_api_url, token). Base URL includes /api suffix.

    HA add-on: uses SUPERVISOR_TOKEN (auto-injected via homeassistant_api: true).
    Standalone: uses HA_URL + HA_TOKEN env vars.
    """
    sup = os.getenv("SUPERVISOR_TOKEN", "")
    if sup:
        return "http://supervisor/core/api", sup
    url = os.getenv("HA_URL", "").rstrip("/")
    token = os.getenv("HA_TOKEN", "")
    return (f"{url}/api" if url else ""), token


def _default_price() -> float:
    raw = os.getenv("DEFAULT_PRICE_KWH", "0.75")
    try:
        return float(raw)
    except (ValueError, TypeError):
        return 0.75

import aiosqlite
from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from itsdangerous import URLSafeSerializer, BadSignature
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from utils.db import init_db, get_db, DB_PATH
from services.calculations import (
    calc_monthly, calc_monthly_netbilling, calc_roi, roi_sensitivity,
    calc_ev_savings, enrich_readings_sequence,
    _get_billing_model, _get_rce_price,
)
from services.forecast import forecast_months, breakeven_scenarios, breakeven_confidence_interval
from services import ha_stats

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR.parent / "templates"
STATIC_DIR = BASE_DIR.parent / "static"

def _read_version() -> str:
    if v := os.getenv("APP_VERSION"):
        return v
    cfg = BASE_DIR.parent / "config.yaml"
    if cfg.exists():
        import re
        m = re.search(r'version:\s*"([^"]+)"', cfg.read_text())
        if m:
            return m.group(1)
    return "dev"

APP_VERSION = _read_version()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="FV Manager", lifespan=lifespan)


# ── Basic Auth middleware ────────────────────────────────────────────────────

class BasicAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        password = os.getenv("FV_AUTH_PASSWORD", "").strip()
        if not password:
            return await call_next(request)

        if request.url.path.startswith("/api/summary"):
            return await call_next(request)

        auth = request.headers.get("Authorization", "")
        if auth.startswith("Basic "):
            try:
                decoded = base64.b64decode(auth[6:]).decode("utf-8")
                _, pwd = decoded.split(":", 1)
                if _secrets.compare_digest(pwd, password):
                    return await call_next(request)
            except Exception:
                pass

        return Response(
            content="Wymagane uwierzytelnienie",
            status_code=401,
            headers={"WWW-Authenticate": 'Basic realm="FV Manager"'},
        )


# ── CSRF middleware ──────────────────────────────────────────────────────────

_CSRF_SECRET = os.getenv("SECRET_KEY", _secrets.token_hex(32))
_csrf_signer = URLSafeSerializer(_CSRF_SECRET, salt="csrf")


def _csrf_generate() -> str:
    return _secrets.token_hex(32)


def _csrf_sign(token: str) -> str:
    return _csrf_signer.dumps(token)


def _csrf_verify(signed: str, token: str) -> bool:
    try:
        return _csrf_signer.loads(signed) == token
    except BadSignature:
        return False


class CSRFMiddleware(BaseHTTPMiddleware):
    EXEMPT_PATHS = {"/api/summary", "/api/ha-fetch", "/api/ha-test",
                    "/api/roi-preview", "/api/ha-solar-fetch", "/api/ha-grid-fetch",
                    "/backup/full"}

    async def dispatch(self, request, call_next):
        if request.method == "POST":
            path = request.url.path
            if not any(path.startswith(p) for p in self.EXEMPT_PATHS):
                cookie_signed = request.cookies.get("csrf_token", "")
                if not cookie_signed:
                    return Response("Nieprawidłowy token CSRF", status_code=403)
                # Read raw body to extract csrf_token without consuming the stream
                body = await request.body()
                form_token = ""
                for part in body.decode("utf-8", errors="replace").split("&"):
                    if part.startswith("csrf_token="):
                        from urllib.parse import unquote_plus
                        form_token = unquote_plus(part.split("=", 1)[1])
                        break
                if not _csrf_verify(cookie_signed, form_token):
                    return Response("Nieprawidłowy token CSRF", status_code=403)

        response = await call_next(request)

        if request.method == "GET" and response.status_code == 200:
            token = _csrf_generate()
            signed = _csrf_sign(token)
            response.set_cookie("csrf_token", signed, httponly=True, samesite="strict")
            response.set_cookie("csrf_token_plain", token, httponly=False, samesite="strict")

        return response


app.add_middleware(CSRFMiddleware)
app.add_middleware(BasicAuthMiddleware)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.filters["urldecode"] = lambda s: __import__("urllib.parse", fromlist=["unquote_plus"]).unquote_plus(s)


def _fmt(value, decimals: int = 0) -> str:
    if value is None:
        return "—"
    try:
        formatted = f"{float(value):,.{decimals}f}"
        # thousands sep: comma → non-breaking space; decimal sep: dot stays
        return formatted.replace(",", "\u00a0")
    except (TypeError, ValueError):
        return "—"


templates.env.filters["fmtn"] = _fmt
templates.env.globals["app_version"] = APP_VERSION


def _t(request: Request, name: str, context: dict | None = None):
    """TemplateResponse helper — injects root_path into every context."""
    ctx = {"rp": request.scope.get("root_path", ""), **(context or {})}
    return templates.TemplateResponse(request=request, name=name, context=ctx)


if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_readings(db: aiosqlite.Connection) -> list[dict]:
    cur = await db.execute("SELECT * FROM readings ORDER BY year, month")
    rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def _get_investments(db: aiosqlite.Connection) -> list[dict]:
    cur = await db.execute("SELECT * FROM investments ORDER BY date")
    rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def _get_fuel_prices(db: aiosqlite.Connection) -> list[dict]:
    cur = await db.execute("SELECT * FROM fuel_prices ORDER BY date")
    rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def _get_billing_periods(db: aiosqlite.Connection) -> list[dict]:
    cur = await db.execute("SELECT * FROM billing_periods ORDER BY start_date")
    rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def _get_rce_prices(db: aiosqlite.Connection) -> list[dict]:
    cur = await db.execute("SELECT * FROM rce_prices ORDER BY date")
    rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def _get_vehicles(db: aiosqlite.Connection) -> list[dict]:
    cur = await db.execute("SELECT * FROM vehicles ORDER BY id")
    rows = await cur.fetchall()
    return [dict(r) for r in rows]


def _vehicles_for_period(vehicles: list[dict], period: str) -> list[dict]:
    result = []
    for v in vehicles:
        df = v.get("date_from")
        dt = v.get("date_to")
        if df and period < df:
            continue
        if dt and period > dt:
            continue
        result.append(v)
    return result


async def _get_ev_monthly_all(db: aiosqlite.Connection) -> list[dict]:
    cur = await db.execute("SELECT * FROM ev_monthly ORDER BY period, vehicle_id")
    rows = await cur.fetchall()
    return [dict(r) for r in rows]


def _inject_odometer_km(ev_monthly: list[dict]) -> list[dict]:
    """For records without manual km but with odometer_km, inject computed km from delta.

    The computed value is runtime-only — never written back to the database.
    Priority: manual km > odometer delta > None (estimated from kWh).
    """
    from collections import defaultdict
    by_vehicle: dict[int, list[dict]] = defaultdict(list)
    for e in ev_monthly:
        by_vehicle[e["vehicle_id"]].append(e)
    for entries in by_vehicle.values():
        entries.sort(key=lambda x: x["period"])

    result = []
    for e in ev_monthly:
        e = dict(e)
        if e.get("km") is None and e.get("odometer_km") is not None:
            entries = by_vehicle[e["vehicle_id"]]
            idx = next((i for i, x in enumerate(entries) if x["period"] == e["period"]), None)
            if idx is not None and idx > 0:
                prev_odometer = entries[idx - 1].get("odometer_km")
                if prev_odometer is not None:
                    e["km"] = max(0.0, e["odometer_km"] - prev_odometer)
        result.append(e)
    return result


def _agg_vehicles_ev(
    vehicles: list[dict],
    ev_monthly: list[dict],
    price_map: dict,
    all_fuel_prices: list[dict],
    default_price: float,
) -> list[dict]:
    """Aggregate total km, kWh, savings per vehicle from ev_monthly entries."""
    prices_desc = sorted(all_fuel_prices, key=lambda p: p["date"], reverse=True)
    vmap = {v["id"]: v for v in vehicles}
    agg: dict[int, dict] = {}

    for e in ev_monthly:
        vid = e["vehicle_id"]
        v = vmap.get(vid)
        if not v or not e.get("kwh"):
            continue
        if vid not in agg:
            agg[vid] = {"kwh": 0.0, "km": 0.0, "savings": 0.0}
        agg[vid]["kwh"] += e["kwh"]

        year, month_str = e["period"].split(".")
        period_end = f"{year}-{month_str.zfill(2)}-28"
        fuel_obj = next(
            (p for p in prices_desc if p["fuel_type"] == v["fuel_type"] and p["date"] <= period_end),
            next((p for p in prices_desc if p["fuel_type"] == v["fuel_type"]), None),
        )
        if fuel_obj:
            calc = calc_ev_savings(
                ev_kwh=e["kwh"],
                price_per_kwh=price_map.get(e["period"]) or default_price,
                efficiency_kwh_per_100km=v["efficiency_kwh_per_100km"],
                fuel_consumption_l_per_100km=v["fuel_consumption_l_per_100km"],
                fuel_price_per_liter=fuel_obj["price_per_liter"],
                km_driven=e.get("km"),
            )
            agg[vid]["km"] += calc["km_driven"]
            agg[vid]["savings"] += calc["ev_net_savings"]

    result = []
    for v in vehicles:
        if v["id"] not in agg:
            continue
        s = agg[v["id"]]
        result.append({
            "id": v["id"],
            "name": v["name"],
            "total_kwh": round(s["kwh"], 1),
            "total_km": round(s["km"], 1),
            "total_savings": round(s["savings"], 2),
        })
    return result


def _ev_enrich(
    readings: list[dict],
    ev_settings: dict,
    fuel_prices: list[dict],
    vehicles: list[dict] | None = None,
    ev_monthly: list[dict] | None = None,
) -> list[dict]:
    """Add ev_savings_pln per reading.

    Prefers multi-vehicle model (vehicles + ev_monthly).
    Falls back to single-vehicle (ev_settings + readings.ev_kwh).
    """
    if not fuel_prices:
        return readings
    prices_desc = sorted(fuel_prices, key=lambda p: p["date"], reverse=True)
    default_price = _default_price()

    def _fuel_price_for(period: str) -> float | None:
        year_s, month_s = period.split(".")
        y, m = int(year_s), int(month_s)
        # Fix #2: ostatni dzień miesiąca zamiast hardkodowanego 28
        last_day = calendar.monthrange(y, m)[1]
        period_end = f"{year_s}-{month_s.zfill(2)}-{last_day}"
        obj = next((p for p in prices_desc if p["date"] <= period_end), prices_desc[-1] if prices_desc else None)
        return obj["price_per_liter"] if obj else None

    # Multi-vehicle path
    if vehicles and ev_monthly:
        vmap = {v["id"]: v for v in vehicles}
        by_period: dict[str, list[dict]] = {}
        for e in ev_monthly:
            by_period.setdefault(e["period"], []).append(e)
        result = []
        for r in readings:
            entries = by_period.get(r["period"], [])
            if not entries:
                result.append(r)
                continue
            fuel_price = _fuel_price_for(r["period"])
            if fuel_price is None:
                result.append(r)
                continue
            price_kwh = r.get("price_per_kwh") or default_price
            savings = sum(
                calc_ev_savings(e["kwh"], price_kwh,
                                vmap[e["vehicle_id"]]["efficiency_kwh_per_100km"],
                                vmap[e["vehicle_id"]]["fuel_consumption_l_per_100km"],
                                fuel_price,
                                km_driven=e.get("km"))["ev_net_savings"]
                for e in entries if e["vehicle_id"] in vmap
            )
            result.append({**r, "ev_savings_pln": savings})
        return result

    # Single-vehicle fallback
    if not ev_settings:
        return readings
    efficiency = ev_settings.get("efficiency_kwh_per_100km") or 16.0
    fuel_cons = ev_settings.get("fuel_consumption_l_per_100km") or 10.0
    result = []
    for r in readings:
        ev_kwh = r.get("ev_kwh")
        if not ev_kwh:
            result.append(r)
            continue
        fuel_price = _fuel_price_for(r["period"])
        if fuel_price is None:
            result.append(r)
            continue
        price_kwh = r.get("price_per_kwh") or default_price
        ev = calc_ev_savings(ev_kwh, price_kwh, efficiency, fuel_cons, fuel_price)
        result.append({**r, "ev_savings_pln": ev["ev_net_savings"]})
    return result


def _validate_reading(
    period: str,
    production_kwh: float,
    sent_to_grid_kwh: float,
    taken_from_grid_kwh: float,
) -> str | None:
    if not re.match(r'^\d{4}\.(0[1-9]|1[0-2])$', period):
        return "Nieprawidłowy format okresu — wymagany: RRRR.MM (np. 2024.07)"
    if production_kwh < 0:
        return "Produkcja nie może być ujemna"
    if sent_to_grid_kwh < 0:
        return "Oddana energia nie może być ujemna"
    if taken_from_grid_kwh < 0:
        return "Pobrana energia nie może być ujemna"
    if sent_to_grid_kwh > production_kwh:
        return f"Oddana energia ({sent_to_grid_kwh} kWh) nie może przekroczyć produkcji ({production_kwh} kWh)"
    return None


# ── Pages ─────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    db = await get_db()
    try:
        readings = await _get_readings(db)
        investments = await _get_investments(db)
        ev_settings = await _get_ev_settings(db)
        fuel_prices = await _get_fuel_prices(db)
        vehicles = await _get_vehicles(db)
        ev_monthly = await _get_ev_monthly_all(db)
        billing_periods = await _get_billing_periods(db)
        rce_prices = await _get_rce_prices(db)
    finally:
        await db.close()

    ev_monthly = _inject_odometer_km(ev_monthly)
    readings = _ev_enrich(readings, ev_settings, fuel_prices, vehicles, ev_monthly)
    total_investment = sum(i["cost_pln"] for i in investments)
    default_price = _default_price()
    nm_ratio = ev_settings.get("net_metering_ratio") or 0.80
    roi = calc_roi(readings, total_investment, default_price, nm_ratio, billing_periods, rce_prices) if readings and total_investment > 0 else None
    enriched = enrich_readings_sequence(readings, nm_ratio, default_price, billing_periods, rce_prices)

    price_map = {r["period"]: r.get("price_per_kwh") for r in readings}
    vehicles_summary = _agg_vehicles_ev(vehicles, ev_monthly, price_map, fuel_prices, default_price)

    last12 = enriched[-12:]
    pv_production_12m = sum(r["production_kwh"] for r in last12)
    pv_auto_12m = sum(r.get("auto_consumption") or 0 for r in last12)
    pv_sent_12m = sum(r["sent_to_grid_kwh"] for r in last12)
    pv_taken_12m = sum(r["taken_from_grid_kwh"] for r in last12)
    pv_savings_12m = sum(r.get("savings_pln") or 0 for r in last12)
    pv_auto_pct = round(pv_auto_12m / pv_production_12m * 100, 1) if pv_production_12m > 0 else None
    pv_stats = {
        "production_12m": round(pv_production_12m, 1),
        "auto_12m": round(pv_auto_12m, 1),
        "auto_pct": pv_auto_pct,
        "sent_12m": round(pv_sent_12m, 1),
        "taken_12m": round(pv_taken_12m, 1),
        "savings_12m": round(pv_savings_12m, 2),
        "avg_monthly_prod": round(pv_production_12m / len(last12), 1) if last12 else None,
    } if last12 else None

    return _t(request, "dashboard.html", {
        "readings": last12,
        "investments": investments,
        "roi": roi,
        "total_months": len(readings),
        "vehicles_summary": vehicles_summary,
        "pv_stats": pv_stats,
    })


@app.get("/odczyty", response_class=HTMLResponse)
async def readings_list(request: Request):
    db = await get_db()
    try:
        readings = await _get_readings(db)
        ev_settings = await _get_ev_settings(db)
        billing_periods = await _get_billing_periods(db)
        rce_prices = await _get_rce_prices(db)
    finally:
        await db.close()

    default_price = _default_price()
    nm_ratio = ev_settings.get("net_metering_ratio") or 0.80
    enriched = enrich_readings_sequence(readings, nm_ratio, default_price, billing_periods, rce_prices)
    for r in enriched:
        r["effective_price"] = r.get("price_per_kwh") or default_price

    return _t(request, "readings.html", {"readings": list(reversed(enriched))})


@app.get("/odczyty/export.csv")
async def export_readings_csv():
    import csv, io
    db = await get_db()
    try:
        readings = await _get_readings(db)
        ev_settings = await _get_ev_settings(db)
        billing_periods = await _get_billing_periods(db)
        rce_prices = await _get_rce_prices(db)
    finally:
        await db.close()

    default_price = _default_price()
    nm_ratio = ev_settings.get("net_metering_ratio") or 0.80
    enriched_map = {r["period"]: r for r in enrich_readings_sequence(readings, nm_ratio, default_price, billing_periods, rce_prices)}
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow([
        "Okres", "Rok", "Miesiąc", "Dni",
        "Produkcja [kWh]", "Oddane [kWh]", "Pobrane [kWh]",
        "Autokonsumpcja [kWh]", "Zużycie [kWh]", "Oszczędności [kWh]",
        "Cena kWh [zł]", "Oszczędności [zł]", "Wartość produkcji [zł]",
        "EV [kWh]", "Nr faktury", "Faktura brutto [zł]", "Notatki",
    ])
    for r in readings:
        c = enriched_map[r["period"]]
        price = r.get("price_per_kwh") or default_price
        writer.writerow([
            r["period"], r["year"], r["month"], r.get("days", ""),
            r["production_kwh"], r["sent_to_grid_kwh"], r["taken_from_grid_kwh"],
            c["auto_consumption"], c["total_consumed"], c["savings_kwh"],
            price, c["savings_pln"], c["production_value_pln"],
            r.get("ev_kwh", ""), r.get("invoice_number", ""),
            r.get("invoice_gross", ""), r.get("notes", ""),
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=odczyty-fv.csv"},
    )


async def _next_period(db) -> tuple[int, int]:
    row = await db.execute_fetchall(
        "SELECT year, month FROM readings ORDER BY year DESC, month DESC LIMIT 1"
    )
    if row:
        y, m = row[0]["year"], row[0]["month"]
        return (y, m + 1) if m < 12 else (y + 1, 1)
    from datetime import date
    d = date.today()
    return d.year, d.month


@app.get("/odczyty/nowy", response_class=HTMLResponse)
async def new_reading_form(request: Request):
    db = await get_db()
    try:
        vehicles = await _get_vehicles(db)
        settings = await _get_ev_settings(db)
        next_year, next_month = await _next_period(db)
    finally:
        await db.close()
    next_period = f"{next_year}.{str(next_month).zfill(2)}"
    return _t(request, "reading_form.html", {
        "vehicles": _vehicles_for_period(vehicles, next_period),
        "settings": settings,
        "next_year": next_year,
        "next_month": next_month,
    })


@app.post("/odczyty/nowy")
async def create_reading(request: Request):
    form = await request.form()
    period = form["period"]
    year = int(form["year"])
    month = int(form["month"])
    days = int(form["days"]) if form.get("days") else None
    production_kwh = float(form["production_kwh"])
    sent_to_grid_kwh = float(form["sent_to_grid_kwh"])
    taken_from_grid_kwh = float(form["taken_from_grid_kwh"])
    price_per_kwh = float(form["price_per_kwh"]) if form.get("price_per_kwh") else None
    invoice_number = form.get("invoice_number") or None
    invoice_gross = float(form["invoice_gross"]) if form.get("invoice_gross") else None
    notes = form.get("notes") or None

    error = _validate_reading(period, production_kwh, sent_to_grid_kwh, taken_from_grid_kwh)
    if error:
        db = await get_db()
        try:
            vehicles = await _get_vehicles(db)
            settings = await _get_ev_settings(db)
        finally:
            await db.close()
        return _t(request, "reading_form.html", {
            "error": error,
            "form_data": dict(form),
            "vehicles": _vehicles_for_period(vehicles, period),
            "settings": settings,
            "next_year": year,
            "next_month": month,
        })

    ev_entries = [(int(k.removeprefix("ev_v_")), float(v)) for k, v in form.items() if k.startswith("ev_v_") and v]
    km_entries = {int(k.removeprefix("ev_km_v_")): float(v) for k, v in form.items() if k.startswith("ev_km_v_") and v}
    odometer_entries = {int(k.removeprefix("ev_odometer_v_")): float(v) for k, v in form.items() if k.startswith("ev_odometer_v_") and v}
    legacy_kwh = float(form["ev_kwh"]) if form.get("ev_kwh") else None
    ev_kwh_total = (sum(v for _, v in ev_entries) if ev_entries else legacy_kwh) or None

    db = await get_db()
    try:
        await db.execute(
            """INSERT OR REPLACE INTO readings
               (period, year, month, days, production_kwh, sent_to_grid_kwh,
                taken_from_grid_kwh, ev_kwh, price_per_kwh, invoice_number, invoice_gross, notes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (period, year, month, days, production_kwh, sent_to_grid_kwh,
             taken_from_grid_kwh, ev_kwh_total, price_per_kwh, invoice_number, invoice_gross, notes),
        )
        for vid, kwh in ev_entries:
            km = km_entries.get(vid)
            odometer = odometer_entries.get(vid)
            await db.execute(
                "INSERT OR REPLACE INTO ev_monthly (period, vehicle_id, kwh, km, odometer_km) VALUES (?,?,?,?,?)",
                (period, vid, kwh, km, odometer),
            )
        await db.commit()
    finally:
        await db.close()
    rp = request.scope.get("root_path", "")
    return RedirectResponse(f"{rp}/odczyty", status_code=303)


@app.get("/odczyty/{reading_id}/edytuj", response_class=HTMLResponse)
async def edit_reading_form(request: Request, reading_id: int):
    db = await get_db()
    try:
        cur = await db.execute("SELECT * FROM readings WHERE id=?", (reading_id,))
        row = await cur.fetchone()
        vehicles = await _get_vehicles(db)
        settings = await _get_ev_settings(db)
        ev_cur = await db.execute("SELECT * FROM ev_monthly WHERE period=(SELECT period FROM readings WHERE id=?)", (reading_id,))
        ev_rows = {r["vehicle_id"]: {"kwh": r["kwh"], "km": r["km"], "odometer_km": r["odometer_km"]} for r in [dict(r) for r in await ev_cur.fetchall()]}
    finally:
        await db.close()
    if not row:
        return HTMLResponse("Nie znaleziono.", status_code=404)
    reading_dict = dict(row)
    return _t(request, "reading_form.html", {
        "reading": reading_dict,
        "vehicles": _vehicles_for_period(vehicles, reading_dict["period"]),
        "ev_rows": ev_rows,
        "settings": settings,
    })


@app.post("/odczyty/{reading_id}/edytuj")
async def update_reading(request: Request, reading_id: int):
    form = await request.form()
    period = form["period"]
    year = int(form["year"])
    month = int(form["month"])
    days = int(form["days"]) if form.get("days") else None
    production_kwh = float(form["production_kwh"])
    sent_to_grid_kwh = float(form["sent_to_grid_kwh"])
    taken_from_grid_kwh = float(form["taken_from_grid_kwh"])
    price_per_kwh = float(form["price_per_kwh"]) if form.get("price_per_kwh") else None
    invoice_number = form.get("invoice_number") or None
    invoice_gross = float(form["invoice_gross"]) if form.get("invoice_gross") else None
    notes = form.get("notes") or None

    error = _validate_reading(period, production_kwh, sent_to_grid_kwh, taken_from_grid_kwh)
    if error:
        db = await get_db()
        try:
            cur = await db.execute("SELECT * FROM readings WHERE id=?", (reading_id,))
            reading = await cur.fetchone()
            vehicles = await _get_vehicles(db)
            settings = await _get_ev_settings(db)
        finally:
            await db.close()
        return _t(request, "reading_form.html", {
            "error": error,
            "reading": dict(reading) if reading else None,
            "form_data": dict(form),
            "vehicles": _vehicles_for_period(vehicles, period),
            "settings": settings,
        })

    ev_entries = [(int(k.removeprefix("ev_v_")), float(v)) for k, v in form.items() if k.startswith("ev_v_") and v]
    km_entries = {int(k.removeprefix("ev_km_v_")): float(v) for k, v in form.items() if k.startswith("ev_km_v_") and v}
    odometer_entries = {int(k.removeprefix("ev_odometer_v_")): float(v) for k, v in form.items() if k.startswith("ev_odometer_v_") and v}
    legacy_kwh = float(form["ev_kwh"]) if form.get("ev_kwh") else None
    ev_kwh_total = (sum(v for _, v in ev_entries) if ev_entries else legacy_kwh) or None

    db = await get_db()
    try:
        await db.execute(
            """UPDATE readings SET period=?, year=?, month=?, days=?, production_kwh=?,
               sent_to_grid_kwh=?, taken_from_grid_kwh=?, ev_kwh=?, price_per_kwh=?,
               invoice_number=?, invoice_gross=?, notes=? WHERE id=?""",
            (period, year, month, days, production_kwh, sent_to_grid_kwh,
             taken_from_grid_kwh, ev_kwh_total, price_per_kwh, invoice_number, invoice_gross, notes, reading_id),
        )
        # Replace ev_monthly for this period
        cur = await db.execute("SELECT period FROM readings WHERE id=?", (reading_id,))
        orig = await cur.fetchone()
        if orig:
            await db.execute("DELETE FROM ev_monthly WHERE period=?", (orig["period"],))
        for vid, kwh in ev_entries:
            km = km_entries.get(vid)
            odometer = odometer_entries.get(vid)
            await db.execute(
                "INSERT OR REPLACE INTO ev_monthly (period, vehicle_id, kwh, km, odometer_km) VALUES (?,?,?,?,?)",
                (period, vid, kwh, km, odometer),
            )
        await db.commit()
    finally:
        await db.close()
    rp = request.scope.get("root_path", "")
    return RedirectResponse(f"{rp}/odczyty", status_code=303)


@app.post("/odczyty/{reading_id}/usun")
async def delete_reading(request: Request, reading_id: int):
    db = await get_db()
    try:
        await db.execute("DELETE FROM readings WHERE id=?", (reading_id,))
        await db.commit()
    finally:
        await db.close()
    rp = request.scope.get("root_path", "")
    return RedirectResponse(f"{rp}/odczyty", status_code=303)


# ── Investments ───────────────────────────────────────────────────────────────

@app.get("/inwestycje", response_class=HTMLResponse)
async def investments_list(request: Request):
    db = await get_db()
    try:
        investments = await _get_investments(db)
        readings = await _get_readings(db)
        ev_settings = await _get_ev_settings(db)
        fuel_prices = await _get_fuel_prices(db)
        vehicles = await _get_vehicles(db)
        ev_monthly = await _get_ev_monthly_all(db)
    finally:
        await db.close()
    ev_monthly = _inject_odometer_km(ev_monthly)
    readings = _ev_enrich(readings, ev_settings, fuel_prices, vehicles, ev_monthly)
    total = sum(i["cost_pln"] for i in investments)
    roi = calc_roi(readings, total) if readings and total > 0 else None
    return _t(request, "investments.html", {"investments": investments, "total": total, "roi": roi})


@app.post("/inwestycje/nowa")
async def create_investment(
    request: Request,
    date: str = Form(...),
    description: str = Form(...),
    cost_pln: float = Form(...),
    power_kwp: float = Form(None),
    notes: str = Form(None),
):
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO investments (date, description, cost_pln, power_kwp, notes) VALUES (?,?,?,?,?)",
            (date, description, cost_pln, power_kwp, notes),
        )
        await db.commit()
    finally:
        await db.close()
    rp = request.scope.get("root_path", "")
    return RedirectResponse(f"{rp}/inwestycje", status_code=303)


@app.get("/inwestycje/{inv_id}/edytuj", response_class=HTMLResponse)
async def edit_investment_form(request: Request, inv_id: int):
    db = await get_db()
    try:
        cur = await db.execute("SELECT * FROM investments WHERE id=?", (inv_id,))
        inv = await cur.fetchone()
    finally:
        await db.close()
    if not inv:
        return RedirectResponse(request.scope.get("root_path", "") + "/inwestycje", status_code=303)
    return _t(request, "investment_form.html", {"inv": dict(inv)})


@app.post("/inwestycje/{inv_id}/edytuj")
async def update_investment(
    request: Request,
    inv_id: int,
    date: str = Form(...),
    description: str = Form(...),
    cost_pln: float = Form(...),
    power_kwp: float | None = Form(None),
    notes: str | None = Form(None),
):
    db = await get_db()
    try:
        await db.execute(
            "UPDATE investments SET date=?, description=?, cost_pln=?, power_kwp=?, notes=? WHERE id=?",
            (date, description, cost_pln, power_kwp or None, notes or None, inv_id),
        )
        await db.commit()
    finally:
        await db.close()
    rp = request.scope.get("root_path", "")
    return RedirectResponse(f"{rp}/inwestycje", status_code=303)


@app.post("/inwestycje/{inv_id}/usun")
async def delete_investment(request: Request, inv_id: int):
    db = await get_db()
    try:
        await db.execute("DELETE FROM investments WHERE id=?", (inv_id,))
        await db.commit()
    finally:
        await db.close()
    rp = request.scope.get("root_path", "")
    return RedirectResponse(f"{rp}/inwestycje", status_code=303)


# ── ROI ───────────────────────────────────────────────────────────────────────

@app.get("/roi", response_class=HTMLResponse)
async def roi_page(request: Request):
    db = await get_db()
    try:
        readings = await _get_readings(db)
        investments = await _get_investments(db)
        ev_settings = await _get_ev_settings(db)
        fuel_prices = await _get_fuel_prices(db)
        vehicles = await _get_vehicles(db)
        ev_monthly = await _get_ev_monthly_all(db)
        billing_periods = await _get_billing_periods(db)
        rce_prices = await _get_rce_prices(db)
    finally:
        await db.close()

    ev_monthly = _inject_odometer_km(ev_monthly)
    readings = _ev_enrich(readings, ev_settings, fuel_prices, vehicles, ev_monthly)
    total = sum(i["cost_pln"] for i in investments)
    default_price = _default_price()
    nm_ratio = ev_settings.get("net_metering_ratio") or 0.80

    roi = calc_roi(readings, total, default_price, nm_ratio, billing_periods, rce_prices) if readings and total > 0 else None
    sensitivity = roi_sensitivity(readings, total, [0.50, 0.60, 0.70, 0.80, 0.90, 1.00, 1.20], nm_ratio, billing_periods, rce_prices) if readings and total > 0 else []

    # Monthly savings for chart — FV + EV stacked
    monthly_savings = []
    cumulative_fv = 0.0
    cumulative_ev = 0.0
    enriched_seq = enrich_readings_sequence(readings, nm_ratio, default_price, billing_periods, rce_prices)
    for r in enriched_seq:
        cumulative_fv += r.get("savings_pln") or 0
        cumulative_ev += r.get("ev_savings_pln") or 0
        monthly_savings.append({
            "period": r["period"],
            "cumulative": round(cumulative_fv + cumulative_ev, 2),
            "cumulative_fv": round(cumulative_fv, 2),
            "cumulative_ev": round(cumulative_ev, 2),
        })

    # Forecast i break-even
    degradation_rate = ev_settings.get("panel_degradation_rate") or 0.006
    FORECAST_HORIZON = 36

    has_enough_data = len(readings) >= 12
    forecast = forecast_months(
        readings, investments, FORECAST_HORIZON, degradation_rate,
        default_price, billing_periods, rce_prices, nm_ratio,
    ) if readings else []

    remaining_pln = roi["remaining_to_roi"] if roi and not roi["roi_achieved"] else 0.0
    growth_rates = [0.0, 0.03, 0.07, 0.12]
    scenarios = breakeven_scenarios(remaining_pln, forecast, growth_rates, default_price) if forecast and remaining_pln > 0 else []
    confidence = breakeven_confidence_interval(scenarios) if scenarios else None

    return _t(request, "roi.html", {
        "roi": roi, "sensitivity": sensitivity,
        "monthly_savings": monthly_savings, "total_investment": total, "investments": investments,
        "has_ev": any(r.get("ev_savings_pln") for r in readings),
        "forecast": forecast,
        "scenarios": scenarios,
        "confidence": confidence,
        "has_enough_data": has_enough_data,
    })


# ── Import ────────────────────────────────────────────────────────────────────

@app.get("/import", response_class=HTMLResponse)
async def import_page(request: Request):
    db = await get_db()
    try:
        settings = await _get_ev_settings(db)
    finally:
        await db.close()
    return _t(request, "import.html", {"settings": settings})




CSV_HEADERS = [
    "Okres", "Rok", "Miesiąc", "Dni",
    "Produkcja [kWh]", "Oddane [kWh]", "Pobrane [kWh]",
    "Autokonsumpcja [kWh]", "Zużycie [kWh]", "Oszczędności [kWh]",
    "Cena kWh [zł]", "Oszczędności [zł]", "Wartość produkcji [zł]",
    "EV [kWh]", "Nr faktury", "Faktura brutto [zł]", "Notatki",
]


@app.get("/import/template.csv")
async def download_csv_template():
    import csv, io
    output = io.StringIO()
    csv.writer(output, delimiter=";").writerow(CSV_HEADERS)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=fv-szablon.csv"},
    )


@app.post("/import/csv")
async def do_import_csv(request: Request, file: UploadFile = File(...)):
    import csv, io
    rp = request.scope.get("root_path", "")
    content = (await file.read()).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content), delimiter=";")
    db = await get_db()
    imported = skipped = 0
    try:
        for row in reader:
            period = row.get("Okres", "").strip()
            if not period:
                continue
            try:
                year, month = int(period.split(".")[0]), int(period.split(".")[1])
                production_kwh = float(row["Produkcja [kWh]"])
                sent_to_grid_kwh = float(row["Oddane [kWh]"])
                taken_from_grid_kwh = float(row["Pobrane [kWh]"])
                err = _validate_reading(period, production_kwh, sent_to_grid_kwh, taken_from_grid_kwh)
                if err:
                    skipped += 1
                    continue
                await db.execute(
                    """INSERT OR IGNORE INTO readings
                       (period, year, month, days, production_kwh, sent_to_grid_kwh,
                        taken_from_grid_kwh, ev_kwh, price_per_kwh, invoice_number, invoice_gross, notes)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        period, year, month,
                        row.get("Dni") or None,
                        production_kwh,
                        sent_to_grid_kwh,
                        taken_from_grid_kwh,
                        row.get("EV [kWh]") or None,
                        row.get("Cena kWh [zł]") or None,
                        row.get("Nr faktury") or None,
                        row.get("Faktura brutto [zł]") or None,
                        row.get("Notatki") or None,
                    ),
                )
                if db.total_changes > imported:
                    imported += 1
                else:
                    skipped += 1
            except Exception:
                skipped += 1
        await db.commit()
    finally:
        await db.close()
    return RedirectResponse(
        f"{rp}/import?imported={imported}&skipped={skipped}&rejected=0",
        status_code=303,
    )


@app.post("/admin/clear-db")
async def clear_db(request: Request):
    db = await get_db()
    try:
        for table in ["ev_monthly", "readings", "investments", "fuel_prices",
                      "vehicles", "billing_periods", "rce_prices"]:
            await db.execute(f"DELETE FROM {table}")
        await db.commit()
    finally:
        await db.close()
    rp = request.scope.get("root_path", "")
    return RedirectResponse(f"{rp}/import?cleared=1", status_code=303)


@app.get("/backup/full")
async def backup_full():
    """Pełny backup wszystkich danych jako JSON — do pobrania."""
    import json
    from datetime import datetime

    db = await get_db()
    try:
        async def fetch(query: str) -> list[dict]:
            cur = await db.execute(query)
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

        data = {
            "version": 2,
            "exported_at": datetime.utcnow().isoformat(),
            "readings":        await fetch("SELECT * FROM readings ORDER BY year, month"),
            "investments":     await fetch("SELECT * FROM investments ORDER BY date"),
            "app_settings":    await fetch("SELECT * FROM app_settings"),
            "fuel_prices":     await fetch("SELECT * FROM fuel_prices ORDER BY date"),
            "vehicles":        await fetch("SELECT * FROM vehicles ORDER BY id"),
            "ev_monthly":      await fetch("SELECT * FROM ev_monthly ORDER BY period"),
            "billing_periods": await fetch("SELECT * FROM billing_periods ORDER BY start_date"),
            "rce_prices":      await fetch("SELECT * FROM rce_prices ORDER BY date"),
        }
    finally:
        await db.close()

    filename = f"fv-backup-{datetime.utcnow().strftime('%Y%m%d-%H%M')}.json"
    return StreamingResponse(
        iter([json.dumps(data, ensure_ascii=False, indent=2)]),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/restore")
async def restore_backup(request: Request, file: UploadFile = File(...)):
    """Przywróć dane z pliku JSON wygenerowanego przez /backup/full.

    UWAGA: nadpisuje istniejące dane (INSERT OR REPLACE).
    app_settings NIE są nadpisywane — zostają bieżące ustawienia.
    """
    import json

    rp = request.scope.get("root_path", "")

    try:
        content = await file.read()
        data = json.loads(content.decode("utf-8"))
    except Exception as e:
        return _t(request, "import.html", {"error": f"Nie można odczytać pliku backup: {e}"})

    if data.get("version") not in (1, 2):
        return _t(request, "import.html", {"error": "Nieznany format backup (oczekiwano version=2)"})

    db = await get_db()
    try:
        for table in ["ev_monthly", "readings", "investments", "fuel_prices",
                      "vehicles", "billing_periods", "rce_prices"]:
            await db.execute(f"DELETE FROM {table}")

        restored = 0

        for inv in data.get("investments", []):
            await db.execute(
                "INSERT OR REPLACE INTO investments (id, date, description, cost_pln, power_kwp, notes) VALUES (?,?,?,?,?,?)",
                (inv.get("id"), inv["date"], inv["description"], inv["cost_pln"],
                 inv.get("power_kwp"), inv.get("notes")),
            )
            restored += 1

        for r in data.get("readings", []):
            await db.execute(
                """INSERT OR REPLACE INTO readings
                   (id, period, year, month, days, production_kwh, sent_to_grid_kwh,
                    taken_from_grid_kwh, ev_kwh, price_per_kwh, sale_price_kwh,
                    invoice_number, invoice_gross, notes)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (r.get("id"), r["period"], r["year"], r["month"], r.get("days"),
                 r["production_kwh"], r["sent_to_grid_kwh"], r["taken_from_grid_kwh"],
                 r.get("ev_kwh"), r.get("price_per_kwh"), r.get("sale_price_kwh"),
                 r.get("invoice_number"), r.get("invoice_gross"), r.get("notes")),
            )
            restored += 1

        for fp in data.get("fuel_prices", []):
            await db.execute(
                "INSERT OR REPLACE INTO fuel_prices (id, date, price_per_liter, fuel_type, source) VALUES (?,?,?,?,?)",
                (fp.get("id"), fp["date"], fp["price_per_liter"],
                 fp.get("fuel_type", "PB95"), fp.get("source")),
            )
            restored += 1

        for v in data.get("vehicles", []):
            await db.execute(
                """INSERT OR REPLACE INTO vehicles
                   (id, name, efficiency_kwh_per_100km, fuel_consumption_l_per_100km, fuel_type, notes)
                   VALUES (?,?,?,?,?,?)""",
                (v.get("id"), v["name"], v["efficiency_kwh_per_100km"],
                 v["fuel_consumption_l_per_100km"], v.get("fuel_type", "PB95"), v.get("notes")),
            )
            restored += 1

        for em in data.get("ev_monthly", []):
            await db.execute(
                "INSERT OR REPLACE INTO ev_monthly (id, period, vehicle_id, kwh) VALUES (?,?,?,?)",
                (em.get("id"), em["period"], em["vehicle_id"], em["kwh"]),
            )
            restored += 1

        for bp in data.get("billing_periods", []):
            await db.execute(
                "INSERT OR REPLACE INTO billing_periods (id, start_date, end_date, model, description) VALUES (?,?,?,?,?)",
                (bp.get("id"), bp["start_date"], bp.get("end_date"),
                 bp["model"], bp.get("description")),
            )
            restored += 1

        for rce in data.get("rce_prices", []):
            await db.execute(
                "INSERT OR REPLACE INTO rce_prices (id, date, price_per_kwh, source) VALUES (?,?,?,?)",
                (rce.get("id"), rce["date"], rce["price_per_kwh"], rce.get("source")),
            )
            restored += 1

        await db.commit()
    except Exception as e:
        await db.close()
        return _t(request, "import.html", {"error": f"Błąd podczas przywracania: {e}"})
    finally:
        await db.close()

    return RedirectResponse(f"{rp}/import?restored={restored}", status_code=303)


# ── EV ───────────────────────────────────────────────────────────────────────

async def _get_ev_settings(db: aiosqlite.Connection) -> dict:
    cur = await db.execute("SELECT * FROM app_settings WHERE id=1")
    row = await cur.fetchone()
    return dict(row) if row else {}


async def _get_latest_fuel_price(db: aiosqlite.Connection) -> dict | None:
    cur = await db.execute("SELECT * FROM fuel_prices ORDER BY date DESC LIMIT 1")
    row = await cur.fetchone()
    return dict(row) if row else None


@app.get("/ev", response_class=HTMLResponse)
async def ev_page(request: Request):
    db = await get_db()
    try:
        readings = await _get_readings(db)
        settings = await _get_ev_settings(db)
        fuel_prices_cur = await db.execute("SELECT * FROM fuel_prices ORDER BY date DESC LIMIT 12")
        prices = [dict(r) for r in await fuel_prices_cur.fetchall()]
        latest_fuel = prices[0] if prices else None
        vehicles = await _get_vehicles(db)
        ev_monthly_all = await _get_ev_monthly_all(db)
        all_fuel_prices = await _get_fuel_prices(db)
    finally:
        await db.close()

    ev_monthly_all = _inject_odometer_km(ev_monthly_all)
    vmap = {v["id"]: v for v in vehicles}
    by_period: dict[str, list[dict]] = {}
    for e in ev_monthly_all:
        by_period.setdefault(e["period"], []).append(e)

    prices_desc = sorted(all_fuel_prices, key=lambda p: p["date"], reverse=True)
    default_price = _default_price()

    monthly_ev = []
    total_ev_savings = 0.0
    total_km = 0.0
    total_liters_saved = 0.0

    for r in readings:
        entries = by_period.get(r["period"], [])
        # fallback: use legacy ev_kwh + settings if no ev_monthly entries
        if not entries and r.get("ev_kwh") and settings:
            entries = [{"vehicle_id": None, "kwh": r["ev_kwh"]}]
        if not entries:
            continue

        year, month = r["period"].split(".")
        period_end = f"{year}-{month.zfill(2)}-28"
        fuel_obj = next((p for p in prices_desc if p["date"] <= period_end), prices_desc[-1] if prices_desc else None)
        fuel_price = fuel_obj["price_per_liter"] if fuel_obj else (latest_fuel["price_per_liter"] if latest_fuel else 6.5)
        price_kwh = r.get("price_per_kwh") or default_price

        period_total_kwh = 0.0
        period_savings = 0.0
        period_km = 0.0
        period_liters = 0.0
        vehicle_rows = []

        for e in entries:
            v = vmap.get(e["vehicle_id"]) if e["vehicle_id"] else None
            eff = v["efficiency_kwh_per_100km"] if v else settings.get("efficiency_kwh_per_100km", 16)
            fuel_cons = v["fuel_consumption_l_per_100km"] if v else settings.get("fuel_consumption_l_per_100km", 10)
            s = calc_ev_savings(e["kwh"], price_kwh, eff, fuel_cons, fuel_price, km_driven=e.get("km"))
            period_total_kwh += e["kwh"]
            period_savings += s["ev_net_savings"]
            period_km += s["km_driven"]
            period_liters += s["liters_saved"]
            vehicle_rows.append({
                "name": v["name"] if v else "—",
                "vehicle_id": e["vehicle_id"],
                "kwh": e["kwh"],
                "km_actual": e.get("km") is not None,
                **s,
            })

        active_vids = [v["id"] for v in _vehicles_for_period(vehicles, r["period"])]
        monthly_ev.append({
            "period": r["period"],
            "ev_kwh": period_total_kwh,
            "ev_net_savings": round(period_savings, 2),
            "km_driven": round(period_km, 1),
            "km_actual": any(x.get("km_actual") for x in vehicle_rows),
            "liters_saved": round(period_liters, 2),
            "fuel_cost_equivalent": round(sum(x["fuel_cost_equivalent"] for x in vehicle_rows), 2),
            "electricity_cost": round(sum(x["electricity_cost"] for x in vehicle_rows), 2),
            "vehicles": vehicle_rows,
            "active_vehicle_ids": active_vids,
        })
        total_ev_savings += period_savings
        total_km += period_km
        total_liters_saved += period_liters

    # ev_raw: period → {vehicle_id → {kwh, km, odometer_km}} — for pre-filling edit forms
    ev_raw: dict[str, dict[int, dict]] = {}
    for e in ev_monthly_all:
        if e["vehicle_id"] is not None:
            ev_raw.setdefault(e["period"], {})[e["vehicle_id"]] = {
                "kwh": e["kwh"],
                "km": e.get("km"),
                "odometer_km": e.get("odometer_km"),
            }

    price_map_ev = {r["period"]: r.get("price_per_kwh") for r in readings}
    vehicles_summary = _agg_vehicles_ev(vehicles, ev_monthly_all, price_map_ev, all_fuel_prices, default_price)

    return _t(request, "ev.html", {
        "settings": settings, "prices": prices, "latest_fuel": latest_fuel,
        "vehicles": vehicles,
        "monthly_ev": list(reversed(monthly_ev)),
        "ev_raw": ev_raw,
        "total_ev_savings": round(total_ev_savings, 2),
        "total_km": round(total_km, 1),
        "total_liters_saved": round(total_liters_saved, 2),
        "vehicles_summary": vehicles_summary,
    })


@app.get("/ev/pojazdy/{vehicle_id}", response_class=HTMLResponse)
async def vehicle_detail(request: Request, vehicle_id: int):
    db = await get_db()
    try:
        cur = await db.execute("SELECT * FROM vehicles WHERE id=?", (vehicle_id,))
        row = await cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Pojazd nie znaleziony")
        vehicle = dict(row)

        cur = await db.execute(
            "SELECT * FROM ev_monthly WHERE vehicle_id=? ORDER BY period ASC", (vehicle_id,)
        )
        entries_raw = [dict(r) for r in await cur.fetchall()]
        original_km = {e["period"]: e.get("km") for e in entries_raw}
        entries = _inject_odometer_km(entries_raw)

        cur = await db.execute("SELECT period, price_per_kwh FROM readings")
        price_map = {r["period"]: r["price_per_kwh"] for r in await cur.fetchall()}

        all_fuel_prices = await _get_fuel_prices(db)
    finally:
        await db.close()

    prices_desc = sorted(
        [p for p in all_fuel_prices if p["fuel_type"] == vehicle["fuel_type"]],
        key=lambda p: p["date"], reverse=True,
    )
    default_price = _default_price()

    monthly = []
    for e in entries:
        year, month_str = e["period"].split(".")
        period_end = f"{year}-{month_str.zfill(2)}-28"
        fuel_obj = next((p for p in prices_desc if p["date"] <= period_end), prices_desc[-1] if prices_desc else None)
        fuel_price = fuel_obj["price_per_liter"] if fuel_obj else None
        price_kwh = price_map.get(e["period"]) or default_price
        km = e.get("km")
        km_actual = km is not None
        orig = original_km.get(e["period"])
        if km is None:
            km_source = "est"
        elif orig is None and e.get("odometer_km") is not None:
            km_source = "licznik"
        else:
            km_source = "manual"

        if fuel_price and e["kwh"]:
            calc = calc_ev_savings(
                ev_kwh=e["kwh"],
                price_per_kwh=price_kwh,
                efficiency_kwh_per_100km=vehicle["efficiency_kwh_per_100km"],
                fuel_consumption_l_per_100km=vehicle["fuel_consumption_l_per_100km"],
                fuel_price_per_liter=fuel_price,
                km_driven=km,
            )
        else:
            calc = None

        monthly.append({
            "period": e["period"],
            "kwh": e["kwh"],
            "km": km,
            "odometer_km": e.get("odometer_km"),
            "km_actual": km_actual,
            "km_source": km_source,
            "price_per_kwh": price_kwh,
            "fuel_price": fuel_price,
            **(calc if calc else {
                "km_driven": None, "fuel_cost_equivalent": None,
                "electricity_cost": None, "ev_net_savings": None, "liters_saved": None,
            }),
        })

    total_kwh = sum(m["kwh"] for m in monthly if m["kwh"])
    total_km = sum(m["km_driven"] for m in monthly if m["km_driven"])
    total_savings = sum(m["ev_net_savings"] for m in monthly if m["ev_net_savings"])
    total_liters = sum(m["liters_saved"] for m in monthly if m["liters_saved"])
    real_km_entries = [(m["kwh"], m["km"]) for m in monthly if m["km_actual"] and m["kwh"] and m["km"]]
    avg_efficiency = (
        sum(kwh for kwh, _ in real_km_entries) / sum(km for _, km in real_km_entries) * 100
        if real_km_entries else None
    )

    return _t(request, "vehicle_detail.html", {
        "vehicle": vehicle,
        "monthly": list(reversed(monthly)),
        "total_kwh": round(total_kwh, 1),
        "total_km": round(total_km, 1),
        "total_savings": round(total_savings, 2),
        "total_liters": round(total_liters, 2),
        "avg_efficiency": round(avg_efficiency, 2) if avg_efficiency else None,
    })


@app.post("/ev/settings")
async def save_ev_settings(
    request: Request,
    efficiency_kwh_per_100km: float = Form(...),
    fuel_consumption_l_per_100km: float = Form(...),
    annual_km: float = Form(...),
    fuel_type: str = Form("PB95"),
    ha_solar_entity: str = Form(None),
    ha_grid_consumed_entity: str = Form(None),
    ha_grid_returned_entity: str = Form(None),
    net_metering_ratio: float = Form(0.80),
):
    db = await get_db()
    try:
        await db.execute(
            """UPDATE app_settings SET efficiency_kwh_per_100km=?, fuel_consumption_l_per_100km=?,
               annual_km=?, fuel_type=?, ha_solar_entity=?,
               ha_grid_consumed_entity=?, ha_grid_returned_entity=?,
               net_metering_ratio=? WHERE id=1""",
            (efficiency_kwh_per_100km, fuel_consumption_l_per_100km, annual_km,
             fuel_type, ha_solar_entity, ha_grid_consumed_entity, ha_grid_returned_entity,
             net_metering_ratio),
        )
        await db.commit()
    finally:
        await db.close()
    rp = request.scope.get("root_path", "")
    return RedirectResponse(f"{rp}/import?saved=1", status_code=303)


@app.post("/ev/pojazdy/{vehicle_id}/monthly/{period}/edytuj")
async def edit_vehicle_monthly(
    request: Request,
    vehicle_id: int,
    period: str,
    kwh: float = Form(...),
    km: str = Form(None),
    odometer_km: str = Form(None),
):
    km_val = float(km.replace(",", ".")) if km and km.strip() else None
    odometer_val = float(odometer_km.replace(",", ".")) if odometer_km and odometer_km.strip() else None
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO ev_monthly (period, vehicle_id, kwh, km, odometer_km) VALUES (?,?,?,?,?) "
            "ON CONFLICT(period, vehicle_id) DO UPDATE SET kwh=excluded.kwh, km=excluded.km, odometer_km=excluded.odometer_km",
            (period, vehicle_id, kwh, km_val, odometer_val),
        )
        await db.commit()
    finally:
        await db.close()
    rp = request.scope.get("root_path", "")
    return RedirectResponse(f"{rp}/ev/pojazdy/{vehicle_id}", status_code=303)


@app.post("/ev/pojazdy/nowy")
async def create_vehicle(
    request: Request,
    name: str = Form(...),
    efficiency_kwh_per_100km: float = Form(...),
    fuel_consumption_l_per_100km: float = Form(...),
    fuel_type: str = Form("PB95"),
    notes: str = Form(None),
    date_from: str = Form(None),
    date_to: str = Form(None),
    przebieg_km: float = Form(None),
):
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO vehicles (name, efficiency_kwh_per_100km, fuel_consumption_l_per_100km, fuel_type, notes, date_from, date_to, przebieg_km) VALUES (?,?,?,?,?,?,?,?)",
            (name, efficiency_kwh_per_100km, fuel_consumption_l_per_100km, fuel_type,
             notes or None, date_from.strip() or None if date_from else None, date_to.strip() or None if date_to else None, przebieg_km),
        )
        await db.commit()
    finally:
        await db.close()
    rp = request.scope.get("root_path", "")
    return RedirectResponse(f"{rp}/ev", status_code=303)


@app.post("/ev/pojazdy/{vid}/usun")
async def delete_vehicle(request: Request, vid: int):
    db = await get_db()
    try:
        await db.execute("DELETE FROM ev_monthly WHERE vehicle_id=?", (vid,))
        await db.execute("DELETE FROM vehicles WHERE id=?", (vid,))
        await db.commit()
    finally:
        await db.close()
    rp = request.scope.get("root_path", "")
    return RedirectResponse(f"{rp}/ev", status_code=303)


@app.post("/ev/pojazdy/{vid}/edytuj")
async def update_vehicle(
    request: Request,
    vid: int,
    name: str = Form(...),
    efficiency_kwh_per_100km: float = Form(...),
    fuel_consumption_l_per_100km: float = Form(...),
    fuel_type: str = Form("PB95"),
    notes: str = Form(None),
    date_from: str = Form(None),
    date_to: str = Form(None),
    przebieg_km: float = Form(None),
):
    db = await get_db()
    try:
        await db.execute(
            "UPDATE vehicles SET name=?, efficiency_kwh_per_100km=?, fuel_consumption_l_per_100km=?, fuel_type=?, notes=?, date_from=?, date_to=?, przebieg_km=? WHERE id=?",
            (name, efficiency_kwh_per_100km, fuel_consumption_l_per_100km, fuel_type,
             notes or None, date_from.strip() or None if date_from else None, date_to.strip() or None if date_to else None, przebieg_km, vid),
        )
        await db.commit()
    finally:
        await db.close()
    rp = request.scope.get("root_path", "")
    return RedirectResponse(f"{rp}/ev", status_code=303)


@app.post("/ev/monthly/{period}/edytuj")
async def edit_ev_monthly(request: Request, period: str):
    """Update ev_monthly entries for a given period. Expects form fields v_{vehicle_id}=kwh, km_v_{vehicle_id}=km, odometer_v_{vehicle_id}=odometer_km."""
    form = await request.form()
    rp = request.scope.get("root_path", "")
    db = await get_db()
    try:
        await db.execute("DELETE FROM ev_monthly WHERE period=?", (period,))
        for key, val in form.items():
            if key.startswith("v_") and str(val).strip():
                try:
                    vid = int(key[2:])
                    kwh = float(str(val).replace(",", "."))
                    if kwh > 0:
                        km_raw = form.get(f"km_v_{vid}")
                        km = float(str(km_raw).replace(",", ".")) if km_raw and str(km_raw).strip() else None
                        odometer_raw = form.get(f"odometer_v_{vid}")
                        odometer = float(str(odometer_raw).replace(",", ".")) if odometer_raw and str(odometer_raw).strip() else None
                        await db.execute(
                            "INSERT INTO ev_monthly (period, vehicle_id, kwh, km, odometer_km) VALUES (?,?,?,?,?)",
                            (period, vid, kwh, km, odometer),
                        )
                except (ValueError, TypeError):
                    pass
        await db.commit()
    finally:
        await db.close()
    return RedirectResponse(f"{rp}/ev", status_code=303)


@app.post("/ev/fuel-price")
async def add_fuel_price(
    request: Request,
    date: str = Form(...),
    price_per_liter: float = Form(...),
    fuel_type: str = Form("PB95"),
    source: str = Form(None),
):
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO fuel_prices (date, price_per_liter, fuel_type, source) VALUES (?,?,?,?)",
            (date, price_per_liter, fuel_type, source),
        )
        await db.commit()
    finally:
        await db.close()
    rp = request.scope.get("root_path", "")
    return RedirectResponse(f"{rp}/ev", status_code=303)


@app.post("/ev/fuel-price/{price_id}/usun")
async def delete_fuel_price(request: Request, price_id: int):
    db = await get_db()
    try:
        await db.execute("DELETE FROM fuel_prices WHERE id=?", (price_id,))
        await db.commit()
    finally:
        await db.close()
    rp = request.scope.get("root_path", "")
    return RedirectResponse(f"{rp}/ev", status_code=303)



# ── PV Settings ──────────────────────────────────────────────────────────────

@app.get("/pv", response_class=HTMLResponse)
async def pv_page(request: Request):
    db = await get_db()
    try:
        billing_periods = await _get_billing_periods(db)
        rce_prices_all = await db.execute("SELECT * FROM rce_prices ORDER BY date DESC LIMIT 24")
        rce_prices = [dict(r) for r in await rce_prices_all.fetchall()]
        settings = await _get_ev_settings(db)
        readings = await _get_readings(db)
        fuel_prices = await _get_fuel_prices(db)
        vehicles = await _get_vehicles(db)
        ev_monthly = await _get_ev_monthly_all(db)
        rce_prices_all2 = await _get_rce_prices(db)
    finally:
        await db.close()

    ev_monthly = _inject_odometer_km(ev_monthly)
    readings = _ev_enrich(readings, settings, fuel_prices, vehicles, ev_monthly)
    nm_ratio = settings.get("net_metering_ratio") or 0.80
    default_price = _default_price()
    enriched = enrich_readings_sequence(readings, nm_ratio, default_price, billing_periods, rce_prices_all2)
    last12 = enriched[-12:]

    pv_stats = None
    if last12:
        pv_production_12m = sum(r["production_kwh"] for r in last12)
        pv_auto_12m = sum(r.get("auto_consumption") or 0 for r in last12)
        pv_sent_12m = sum(r["sent_to_grid_kwh"] for r in last12)
        pv_taken_12m = sum(r["taken_from_grid_kwh"] for r in last12)
        pv_savings_12m = sum(r.get("savings_pln") or 0 for r in last12)
        pv_auto_pct = round(pv_auto_12m / pv_production_12m * 100, 1) if pv_production_12m > 0 else None
        pv_stats = {
            "production_12m": round(pv_production_12m, 1),
            "auto_12m": round(pv_auto_12m, 1),
            "auto_pct": pv_auto_pct,
            "sent_12m": round(pv_sent_12m, 1),
            "taken_12m": round(pv_taken_12m, 1),
            "savings_12m": round(pv_savings_12m, 2),
            "avg_monthly_prod": round(pv_production_12m / len(last12), 1),
            "n_months": len(last12),
        }

    return _t(request, "pv.html", {
        "billing_periods": billing_periods,
        "rce_prices": rce_prices,
        "settings": settings,
        "pv_stats": pv_stats,
    })


@app.post("/pv/billing-period")
async def add_billing_period(
    request: Request,
    start_date: str = Form(...),
    end_date: str = Form(None),
    model: str = Form(...),
    description: str = Form(None),
):
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO billing_periods (start_date, end_date, model, description) VALUES (?,?,?,?)",
            (start_date, end_date or None, model, description or None),
        )
        await db.commit()
    finally:
        await db.close()
    rp = request.scope.get("root_path", "")
    return RedirectResponse(f"{rp}/pv", status_code=303)


@app.post("/pv/billing-period/{bp_id}/usun")
async def delete_billing_period(request: Request, bp_id: int):
    db = await get_db()
    try:
        await db.execute("DELETE FROM billing_periods WHERE id=?", (bp_id,))
        await db.commit()
    finally:
        await db.close()
    rp = request.scope.get("root_path", "")
    return RedirectResponse(f"{rp}/pv", status_code=303)


@app.post("/pv/rce-price")
async def add_rce_price(
    request: Request,
    date: str = Form(...),
    price_per_kwh: float = Form(...),
    source: str = Form(None),
):
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO rce_prices (date, price_per_kwh, source) VALUES (?,?,?)",
            (date, price_per_kwh, source or None),
        )
        await db.commit()
    finally:
        await db.close()
    rp = request.scope.get("root_path", "")
    return RedirectResponse(f"{rp}/pv", status_code=303)


@app.post("/pv/rce-price/{price_id}/usun")
async def delete_rce_price(request: Request, price_id: int):
    db = await get_db()
    try:
        await db.execute("DELETE FROM rce_prices WHERE id=?", (price_id,))
        await db.commit()
    finally:
        await db.close()
    rp = request.scope.get("root_path", "")
    return RedirectResponse(f"{rp}/pv", status_code=303)


@app.post("/pv/settings")
async def save_pv_settings(
    request: Request,
    panel_degradation_rate_pct: float = Form(0.6),
):
    db = await get_db()
    try:
        await db.execute(
            "UPDATE app_settings SET panel_degradation_rate=? WHERE id=1",
            (panel_degradation_rate_pct / 100,),
        )
        await db.commit()
    finally:
        await db.close()
    rp = request.scope.get("root_path", "")
    return RedirectResponse(f"{rp}/pv", status_code=303)


# ── Coming Soon ───────────────────────────────────────────────────────────────

@app.get("/bateria", response_class=HTMLResponse)
async def battery_page(request: Request):
    return _t(request, "coming_soon.html", {
        "icon": "🔋",
        "title": "Magazyn energii",
        "description": (
            "Śledzenie efektywności baterii domowej, analiza cykli ładowania/rozładowania "
            "i optymalizacja autokonsumpcji. Ta funkcja jest w planach dla przyszłej wersji."
        ),
        "planned": [
            "Śledzenie stanu naładowania baterii (SOC) przez dzień",
            "Analiza ile % autokonsumpcji pochodzi z baterii vs PV vs sieci",
            "Optymalizacja: kiedy ładować baterię (taryfa nocna vs dzienna)",
            "ROI dla baterii oddzielnie od ROI instalacji PV",
        ],
        "external_url": None,
    })


@app.get("/ogrzewanie", response_class=HTMLResponse)
async def heating_page(request: Request):
    return _t(request, "coming_soon.html", {
        "icon": "🔥",
        "title": "Ogrzewanie elektryczne",
        "description": (
            "Monitorowanie kosztów ogrzewania pompą ciepła lub innym urządzeniem elektrycznym "
            "i obliczanie oszczędności vs ogrzewanie gazem. Ta funkcja jest w planach."
        ),
        "planned": [
            "Wpis miesięcznego zużycia energii na ogrzewanie [kWh]",
            "Porównanie kosztu: prąd (z kWh ogrzewania) vs gaz (cena za m³ × zużycie)",
            "Udział energii PV w pokryciu kosztów ogrzewania",
            "Breakeven dla pompy ciepła vs kotła gazowego",
        ],
        "external_url": None,
    })




@app.get("/metodologia", response_class=HTMLResponse)
async def metodologia_page(request: Request):
    return _t(request, "metodologia.html", {})


@app.get("/api/ha-test")
async def ha_test():
    """Test HA connection and return last monthly value for solar entity."""
    import httpx
    from datetime import date
    db = await get_db()
    try:
        settings = await _get_ev_settings(db)
    finally:
        await db.close()

    ha_url, ha_token = _ha_conn()
    headers = {"Authorization": f"Bearer {ha_token}"}
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            ping = await client.get(f"{ha_url}/", headers=headers)
        if ping.status_code == 401:
            return JSONResponse({"error": "Brak autoryzacji (401) — dodaj homeassistant_api: true do config.yaml"})
        if ping.status_code != 200:
            return JSONResponse({"error": f"HA odpowiedział {ping.status_code} — {ping.text[:100]}"})
    except Exception as e:
        return JSONResponse({"error": f"Błąd połączenia: {e}"})

    ha_solar = settings.get("ha_solar_entity") or ""
    if not ha_solar:
        return JSONResponse({"ok": True, "message": "Połączenie OK — brak skonfigurowanej encji solarnej"})

    today = date.today()
    delta = await ha_stats.get_monthly_energy(ha_solar, today.year, today.month)
    period_label = f"{today.year}-{today.month:02d}"
    if delta is None:
        prev_month = today.month - 1 or 12
        prev_year = today.year if today.month > 1 else today.year - 1
        delta = await ha_stats.get_monthly_energy(ha_solar, prev_year, prev_month)
        period_label = f"{prev_year}-{prev_month:02d}"

    if delta is None:
        return JSONResponse({"error": f"Brak danych statystycznych dla {ha_solar}"})

    return JSONResponse({
        "ok": True,
        "entity": ha_solar,
        "last_period_start": period_label,
        "production_kwh": round(delta, 2),
        "message": f"OK — {period_label}: {round(delta, 2)} kWh",
    })


@app.get("/api/ha-grid-fetch")
async def ha_grid_fetch(period: str, direction: str = "consumed"):
    """Fetch monthly grid energy from HA Statistics API. direction: consumed|returned."""
    db = await get_db()
    try:
        settings = await _get_ev_settings(db)
    finally:
        await db.close()

    entity = settings.get(f"ha_grid_{direction}_entity") or ""
    if not entity:
        return JSONResponse({"error": f"Skonfiguruj encję grid_{direction} w ustawieniach HA"}, status_code=400)

    try:
        year, month = int(period.split(".")[0]), int(period.split(".")[1])
    except Exception:
        return JSONResponse({"error": "Nieprawidłowy format okresu"}, status_code=400)

    delta = await ha_stats.get_monthly_energy(entity, year, month)
    if delta is None:
        return JSONResponse({"error": f"Brak danych dla {entity} za {year}-{month:02d}"}, status_code=502)
    return JSONResponse({"kwh": round(delta, 3), "entity": entity})


@app.get("/api/ha-solar-fetch")
async def ha_solar_fetch(period: str):
    """Fetch monthly solar production from HA Statistics API."""
    db = await get_db()
    try:
        settings = await _get_ev_settings(db)
    finally:
        await db.close()

    ha_solar = settings.get("ha_solar_entity") or ""
    if not ha_solar:
        return JSONResponse({"error": "Skonfiguruj encję Solar w ustawieniach HA"}, status_code=400)

    try:
        year, month = int(period.split(".")[0]), int(period.split(".")[1])
    except Exception:
        return JSONResponse({"error": "Nieprawidłowy format okresu"}, status_code=400)

    delta = await ha_stats.get_monthly_energy(ha_solar, year, month)
    if delta is None:
        return JSONResponse({"error": f"Brak danych dla {ha_solar} za {year}-{month:02d}"}, status_code=502)
    return JSONResponse({"production_kwh": round(delta, 3), "entity": ha_solar, "period": period})


# ── ROI preview ───────────────────────────────────────────────────────────────

@app.post("/api/roi-preview")
async def roi_preview(data: dict):
    """Calculate ROI before/after for edit confirmation modal."""
    db = await get_db()
    try:
        readings = await _get_readings(db)
        investments = await _get_investments(db)
        ev_settings = await _get_ev_settings(db)
        fuel_prices = await _get_fuel_prices(db)
        vehicles = await _get_vehicles(db)
        ev_monthly = await _get_ev_monthly_all(db)
    finally:
        await db.close()

    ev_monthly = _inject_odometer_km(ev_monthly)
    readings = _ev_enrich(readings, ev_settings, fuel_prices, vehicles, ev_monthly)
    total = sum(i["cost_pln"] for i in investments)
    roi_before = calc_roi(readings, total) if readings and total > 0 else {}

    # Apply hypothetical edit
    reading_id = data.get("id")
    patched = _ev_enrich(
        [{**r, **data} if r["id"] == reading_id else r for r in readings],
        ev_settings, fuel_prices, vehicles, ev_monthly,
    )
    roi_after = calc_roi(patched, total) if patched and total > 0 else {}
    return JSONResponse({
        "before": {
            "total_savings_pln": roi_before.get("total_savings_pln", 0),
            "remaining_to_roi": roi_before.get("remaining_to_roi", 0),
            "months_to_roi": roi_before.get("months_to_roi", 0),
            "roi_achieved": roi_before.get("roi_achieved", False),
        },
        "after": {
            "total_savings_pln": roi_after.get("total_savings_pln", 0),
            "remaining_to_roi": roi_after.get("remaining_to_roi", 0),
            "months_to_roi": roi_after.get("months_to_roi", 0),
            "roi_achieved": roi_after.get("roi_achieved", False),
        },
    })


# ── API ───────────────────────────────────────────────────────────────────────

@app.get("/api/summary")
async def api_summary():
    """JSON endpoint for Home Assistant sensors."""
    db = await get_db()
    try:
        readings = await _get_readings(db)
        investments = await _get_investments(db)
    finally:
        await db.close()

    total = sum(i["cost_pln"] for i in investments)
    roi = calc_roi(readings, total) if readings and total > 0 else {}
    last = readings[-1] if readings else {}
    return JSONResponse({**roi, "last_period": last.get("period"), "last_production_kwh": last.get("production_kwh")})


