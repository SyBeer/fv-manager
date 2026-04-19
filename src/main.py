import os
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def _ha_conn() -> tuple[str, str]:
    """Return (ha_url, ha_token) using Supervisor internals — no config needed."""
    url = "http://supervisor/core"
    token = os.getenv("SUPERVISOR_TOKEN", "")
    return url, token


def _default_price() -> float:
    raw = os.getenv("DEFAULT_PRICE_KWH", "0.75")
    try:
        return float(raw)
    except (ValueError, TypeError):
        return 0.75

import aiosqlite
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from utils.db import init_db, get_db, DB_PATH
from services.calculations import calc_monthly, calc_roi, roi_sensitivity, calc_ev_savings

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR.parent / "templates"
STATIC_DIR = BASE_DIR.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="FV Manager", lifespan=lifespan)
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


async def _get_vehicles(db: aiosqlite.Connection) -> list[dict]:
    cur = await db.execute("SELECT * FROM vehicles ORDER BY id")
    rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def _get_ev_monthly_all(db: aiosqlite.Connection) -> list[dict]:
    cur = await db.execute("SELECT * FROM ev_monthly ORDER BY period, vehicle_id")
    rows = await cur.fetchall()
    return [dict(r) for r in rows]


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
        year, month = period.split(".")
        period_end = f"{year}-{month.zfill(2)}-28"
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
                                fuel_price)["ev_net_savings"]
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
    finally:
        await db.close()

    readings = _ev_enrich(readings, ev_settings, fuel_prices, vehicles, ev_monthly)
    total_investment = sum(i["cost_pln"] for i in investments)
    roi = calc_roi(readings, total_investment) if readings and total_investment > 0 else None

    default_price = _default_price()
    enriched = []
    for r in readings:
        price = r.get("price_per_kwh") or default_price
        c = calc_monthly(r["production_kwh"], r["sent_to_grid_kwh"], r["taken_from_grid_kwh"], price)
        enriched.append({**r, **c})

    return _t(request, "dashboard.html", {
        "readings": enriched[-12:],
        "investments": investments,
        "roi": roi,
        "total_months": len(readings),
    })


@app.get("/odczyty", response_class=HTMLResponse)
async def readings_list(request: Request):
    db = await get_db()
    try:
        readings = await _get_readings(db)
    finally:
        await db.close()

    default_price = _default_price()
    enriched = []
    for r in readings:
        price = r.get("price_per_kwh") or default_price
        c = calc_monthly(r["production_kwh"], r["sent_to_grid_kwh"], r["taken_from_grid_kwh"], price)
        enriched.append({**r, **c, "effective_price": price})

    return _t(request, "readings.html", {"readings": list(reversed(enriched))})


@app.get("/odczyty/export.csv")
async def export_readings_csv():
    import csv, io
    db = await get_db()
    try:
        readings = await _get_readings(db)
    finally:
        await db.close()

    default_price = _default_price()
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
        price = r.get("price_per_kwh") or default_price
        c = calc_monthly(r["production_kwh"], r["sent_to_grid_kwh"], r["taken_from_grid_kwh"], price)
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


@app.get("/odczyty/nowy", response_class=HTMLResponse)
async def new_reading_form(request: Request):
    db = await get_db()
    try:
        vehicles = await _get_vehicles(db)
    finally:
        await db.close()
    return _t(request, "reading_form.html", {"vehicles": vehicles})


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

    ev_entries = [(int(k[5:]), float(v)) for k, v in form.items() if k.startswith("ev_v_") and v]
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
            await db.execute(
                "INSERT OR REPLACE INTO ev_monthly (period, vehicle_id, kwh) VALUES (?,?,?)",
                (period, vid, kwh),
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
        ev_cur = await db.execute("SELECT * FROM ev_monthly WHERE period=(SELECT period FROM readings WHERE id=?)", (reading_id,))
        ev_rows = {r["vehicle_id"]: r["kwh"] for r in [dict(r) for r in await ev_cur.fetchall()]}
    finally:
        await db.close()
    if not row:
        return HTMLResponse("Nie znaleziono.", status_code=404)
    return _t(request, "reading_form.html", {"reading": dict(row), "vehicles": vehicles, "ev_rows": ev_rows})


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

    ev_entries = [(int(k[5:]), float(v)) for k, v in form.items() if k.startswith("ev_v_") and v]
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
            await db.execute(
                "INSERT OR REPLACE INTO ev_monthly (period, vehicle_id, kwh) VALUES (?,?,?)",
                (period, vid, kwh),
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
    finally:
        await db.close()

    readings = _ev_enrich(readings, ev_settings, fuel_prices, vehicles, ev_monthly)
    total = sum(i["cost_pln"] for i in investments)
    roi = calc_roi(readings, total) if readings and total > 0 else None
    sensitivity = roi_sensitivity(readings, total, [0.50, 0.60, 0.70, 0.80, 0.90, 1.00, 1.20]) if readings and total > 0 else []

    # Monthly savings for chart — FV + EV stacked
    monthly_savings = []
    cumulative_fv = 0.0
    cumulative_ev = 0.0
    default_price = _default_price()
    for r in readings:
        c = calc_monthly(r["production_kwh"], r["sent_to_grid_kwh"], r["taken_from_grid_kwh"], r.get("price_per_kwh") or default_price)
        cumulative_fv += c["savings_pln"] or 0
        cumulative_ev += r.get("ev_savings_pln") or 0
        monthly_savings.append({
            "period": r["period"],
            "cumulative": round(cumulative_fv + cumulative_ev, 2),
            "cumulative_fv": round(cumulative_fv, 2),
            "cumulative_ev": round(cumulative_ev, 2),
        })

    return _t(request, "roi.html", {
        "roi": roi, "sensitivity": sensitivity,
        "monthly_savings": monthly_savings, "total_investment": total, "investments": investments,
        "has_ev": any(r.get("ev_savings_pln") for r in readings),
    })


# ── Import ────────────────────────────────────────────────────────────────────

@app.get("/import", response_class=HTMLResponse)
async def import_page(request: Request):
    return _t(request, "import.html")




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
                await db.execute(
                    """INSERT OR IGNORE INTO readings
                       (period, year, month, days, production_kwh, sent_to_grid_kwh,
                        taken_from_grid_kwh, ev_kwh, price_per_kwh, invoice_number, invoice_gross, notes)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        period, year, month,
                        row.get("Dni") or None,
                        float(row["Produkcja [kWh]"]),
                        float(row["Oddane [kWh]"]),
                        float(row["Pobrane [kWh]"]),
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
        await db.execute("DELETE FROM readings")
        await db.commit()
    finally:
        await db.close()
    rp = request.scope.get("root_path", "")
    return RedirectResponse(f"{rp}/import?cleared=1", status_code=303)


# ── EV ───────────────────────────────────────────────────────────────────────

async def _get_ev_settings(db: aiosqlite.Connection) -> dict:
    cur = await db.execute("SELECT * FROM ev_settings WHERE id=1")
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
            s = calc_ev_savings(e["kwh"], price_kwh, eff, fuel_cons, fuel_price)
            period_total_kwh += e["kwh"]
            period_savings += s["ev_net_savings"]
            period_km += s["km_driven"]
            period_liters += s["liters_saved"]
            vehicle_rows.append({
                "name": v["name"] if v else "—",
                "kwh": e["kwh"],
                **s,
            })

        monthly_ev.append({
            "period": r["period"],
            "ev_kwh": period_total_kwh,
            "ev_net_savings": round(period_savings, 2),
            "km_driven": round(period_km, 1),
            "liters_saved": round(period_liters, 2),
            "fuel_cost_equivalent": round(sum(x["fuel_cost_equivalent"] for x in vehicle_rows), 2),
            "electricity_cost": round(sum(x["electricity_cost"] for x in vehicle_rows), 2),
            "vehicles": vehicle_rows,
        })
        total_ev_savings += period_savings
        total_km += period_km
        total_liters_saved += period_liters

    return _t(request, "ev.html", {
        "settings": settings, "prices": prices, "latest_fuel": latest_fuel,
        "vehicles": vehicles,
        "monthly_ev": list(reversed(monthly_ev)),
        "total_ev_savings": round(total_ev_savings, 2),
        "total_km": round(total_km, 1),
        "total_liters_saved": round(total_liters_saved, 2),
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
):
    db = await get_db()
    try:
        await db.execute(
            """UPDATE ev_settings SET efficiency_kwh_per_100km=?, fuel_consumption_l_per_100km=?,
               annual_km=?, fuel_type=?, ha_solar_entity=?,
               ha_grid_consumed_entity=?, ha_grid_returned_entity=? WHERE id=1""",
            (efficiency_kwh_per_100km, fuel_consumption_l_per_100km, annual_km,
             fuel_type, ha_solar_entity, ha_grid_consumed_entity, ha_grid_returned_entity),
        )
        await db.commit()
    finally:
        await db.close()
    rp = request.scope.get("root_path", "")
    return RedirectResponse(f"{rp}/ev", status_code=303)


@app.post("/ev/pojazdy/nowy")
async def create_vehicle(
    request: Request,
    name: str = Form(...),
    efficiency_kwh_per_100km: float = Form(...),
    fuel_consumption_l_per_100km: float = Form(...),
    fuel_type: str = Form("PB95"),
    notes: str = Form(None),
):
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO vehicles (name, efficiency_kwh_per_100km, fuel_consumption_l_per_100km, fuel_type, notes) VALUES (?,?,?,?,?)",
            (name, efficiency_kwh_per_100km, fuel_consumption_l_per_100km, fuel_type, notes or None),
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
):
    db = await get_db()
    try:
        await db.execute(
            "UPDATE vehicles SET name=?, efficiency_kwh_per_100km=?, fuel_consumption_l_per_100km=?, fuel_type=?, notes=? WHERE id=?",
            (name, efficiency_kwh_per_100km, fuel_consumption_l_per_100km, fuel_type, notes or None, vid),
        )
        await db.commit()
    finally:
        await db.close()
    rp = request.scope.get("root_path", "")
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
    ha_solar = settings.get("ha_solar_entity") or ""
    headers = {"Authorization": f"Bearer {ha_token}"}
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            # 1. Test connection
            ping = await client.get(f"{ha_url}/api/", headers=headers)
            if ping.status_code == 401:
                return JSONResponse({"error": "Token nieprawidłowy (401 Unauthorized)"}, status_code=401)
            if ping.status_code != 200:
                return JSONResponse({"error": f"HA odpowiedział {ping.status_code}"}, status_code=502)

            if not ha_solar:
                return JSONResponse({"ok": True, "message": "Połączenie OK — brak skonfigurowanej encji solarnej"})

            # 2. Fetch last 3 months of statistics to find latest non-null value
            today = date.today()
            start = f"{today.year - 1}-{today.month:02d}-01T00:00:00"
            end = f"{today.year}-{today.month:02d}-28T23:59:59"
            r = await client.post(
                f"{ha_url}/api/recorder/statistics_during_period",
                headers={**headers, "Content-Type": "application/json"},
                json={
                    "start_time": start,
                    "end_time": end,
                    "statistic_ids": [ha_solar],
                    "period": "month",
                    "types": ["change"],
                },
            )
            if r.status_code != 200:
                return JSONResponse({"error": f"Statistics API: {r.status_code} — {r.text[:200]}"}, status_code=502)
            try:
                data = r.json()
            except Exception as je:
                return JSONResponse({"error": f"Nieprawidłowa odpowiedź JSON: {je} | Treść: {r.text[:300]}"}, status_code=502)
            entries = data.get(ha_solar, [])
            if not entries:
                return JSONResponse({"ok": True, "message": f"Połączenie OK — brak danych statystyk dla {ha_solar}. Sprawdź nazwę encji."})

            last = entries[-1]
            return JSONResponse({
                "ok": True,
                "entity": ha_solar,
                "last_period_start": last.get("start", "")[:7],
                "production_kwh": round(float(last.get("change") or 0), 2),
                "message": f"OK — ostatni odczyt: {round(float(last.get('change') or 0), 2)} kWh",
            })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/ha-grid-fetch")
async def ha_grid_fetch(period: str, direction: str = "consumed"):
    """Fetch monthly grid energy from HA statistics. direction: consumed|returned."""
    import httpx, calendar
    db = await get_db()
    try:
        settings = await _get_ev_settings(db)
    finally:
        await db.close()

    entity = settings.get(f"ha_grid_{direction}_entity") or ""
    if not entity:
        return JSONResponse({"error": f"Skonfiguruj encję grid_{direction} w ustawieniach HA"}, status_code=400)

    ha_url, ha_token = _ha_conn()
    try:
        year, month = int(period.split(".")[0]), int(period.split(".")[1])
        last_day = calendar.monthrange(year, month)[1]
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                f"{ha_url}/api/recorder/statistics_during_period",
                headers={"Authorization": f"Bearer {ha_token}", "Content-Type": "application/json"},
                json={
                    "start_time": f"{year}-{month:02d}-01T00:00:00",
                    "end_time": f"{year}-{month:02d}-{last_day}T23:59:59",
                    "statistic_ids": [entity],
                    "period": "month",
                    "types": ["change"],
                },
            )
        if r.status_code != 200:
            return JSONResponse({"error": f"Statistics API: {r.status_code} — {r.text[:200]}"}, status_code=502)
        try:
            data = r.json()
        except Exception as je:
            return JSONResponse({"error": f"Nieprawidłowa odpowiedź JSON: {je} | Treść: {r.text[:300]}"}, status_code=502)
        entries = data.get(entity, [])
        if not entries:
            return JSONResponse({"error": f"Brak danych dla {entity} w {period}"}, status_code=404)
        change = entries[0].get("change")
        return JSONResponse({"kwh": round(float(change), 3), "entity": entity})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/ha-solar-fetch")
async def ha_solar_fetch(period: str):
    """Fetch monthly solar production from HA statistics API."""
    import httpx, calendar
    db = await get_db()
    try:
        settings = await _get_ev_settings(db)
    finally:
        await db.close()

    ha_url, ha_token = _ha_conn()
    ha_solar = settings.get("ha_solar_entity") or ""

    if not ha_solar:
        return JSONResponse({"error": "Skonfiguruj encję Solar w ustawieniach HA"}, status_code=400)

    try:
        year, month = int(period.split(".")[0]), int(period.split(".")[1])
        start = f"{year}-{month:02d}-01T00:00:00"
        last_day = calendar.monthrange(year, month)[1]
        end = f"{year}-{month:02d}-{last_day}T23:59:59"

        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                f"{ha_url}/api/recorder/statistics_during_period",
                headers={"Authorization": f"Bearer {ha_token}", "Content-Type": "application/json"},
                json={
                    "start_time": start,
                    "end_time": end,
                    "statistic_ids": [ha_solar],
                    "period": "month",
                    "types": ["change"],
                },
            )
        if r.status_code != 200:
            return JSONResponse({"error": f"Statistics API: {r.status_code} — {r.text[:200]}"}, status_code=502)
        try:
            data = r.json()
        except Exception as je:
            return JSONResponse({"error": f"Nieprawidłowa odpowiedź JSON: {je} | Treść: {r.text[:300]}"}, status_code=502)
        entries = data.get(ha_solar, [])
        if not entries:
            return JSONResponse({"error": f"Brak danych statystyk dla {ha_solar} w okresie {period}"}, status_code=404)
        change = entries[0].get("change")
        if change is None:
            return JSONResponse({"error": "Brak wartości 'change' w odpowiedzi HA"}, status_code=500)
        return JSONResponse({"production_kwh": round(float(change), 3), "entity": ha_solar, "period": period})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


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
