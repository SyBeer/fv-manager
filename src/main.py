import os
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

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


# ── Pages ─────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    db = await get_db()
    try:
        readings = await _get_readings(db)
        investments = await _get_investments(db)
    finally:
        await db.close()

    total_investment = sum(i["cost_pln"] for i in investments)
    roi = calc_roi(readings, total_investment) if readings and total_investment > 0 else None

    default_price = float(os.getenv("DEFAULT_PRICE_KWH", 0.75))
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

    default_price = float(os.getenv("DEFAULT_PRICE_KWH", 0.75))
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

    default_price = float(os.getenv("DEFAULT_PRICE_KWH", 0.75))
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
    return _t(request, "reading_form.html")


@app.post("/odczyty/nowy")
async def create_reading(
    request: Request,
    period: str = Form(...),
    year: int = Form(...),
    month: int = Form(...),
    days: int = Form(None),
    production_kwh: float = Form(...),
    sent_to_grid_kwh: float = Form(...),
    taken_from_grid_kwh: float = Form(...),
    ev_kwh: float = Form(None),
    price_per_kwh: float = Form(None),
    invoice_number: str = Form(None),
    invoice_gross: float = Form(None),
    notes: str = Form(None),
):
    db = await get_db()
    try:
        await db.execute(
            """INSERT OR REPLACE INTO readings
               (period, year, month, days, production_kwh, sent_to_grid_kwh,
                taken_from_grid_kwh, ev_kwh, price_per_kwh, invoice_number, invoice_gross, notes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (period, year, month, days, production_kwh, sent_to_grid_kwh,
             taken_from_grid_kwh, ev_kwh, price_per_kwh, invoice_number, invoice_gross, notes),
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
    finally:
        await db.close()
    if not row:
        return HTMLResponse("Nie znaleziono.", status_code=404)
    return _t(request, "reading_form.html", {"reading": dict(row)})


@app.post("/odczyty/{reading_id}/edytuj")
async def update_reading(
    request: Request,
    reading_id: int,
    period: str = Form(...),
    year: int = Form(...),
    month: int = Form(...),
    days: int = Form(None),
    production_kwh: float = Form(...),
    sent_to_grid_kwh: float = Form(...),
    taken_from_grid_kwh: float = Form(...),
    ev_kwh: float = Form(None),
    price_per_kwh: float = Form(None),
    invoice_number: str = Form(None),
    invoice_gross: float = Form(None),
    notes: str = Form(None),
):
    db = await get_db()
    try:
        await db.execute(
            """UPDATE readings SET period=?, year=?, month=?, days=?, production_kwh=?,
               sent_to_grid_kwh=?, taken_from_grid_kwh=?, ev_kwh=?, price_per_kwh=?,
               invoice_number=?, invoice_gross=?, notes=? WHERE id=?""",
            (period, year, month, days, production_kwh, sent_to_grid_kwh,
             taken_from_grid_kwh, ev_kwh, price_per_kwh, invoice_number, invoice_gross, notes, reading_id),
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
    finally:
        await db.close()
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
    finally:
        await db.close()

    total = sum(i["cost_pln"] for i in investments)
    roi = calc_roi(readings, total) if readings and total > 0 else None
    sensitivity = roi_sensitivity(readings, total, [0.50, 0.60, 0.70, 0.80, 0.90, 1.00, 1.20]) if readings and total > 0 else []

    # Monthly savings history for chart
    monthly_savings = []
    cumulative = 0.0
    for r in readings:
        c = calc_monthly(r["production_kwh"], r["sent_to_grid_kwh"], r["taken_from_grid_kwh"], r.get("price_per_kwh") or 0.75)
        cumulative += c["savings_pln"] or 0
        monthly_savings.append({"period": r["period"], "cumulative": round(cumulative, 2)})

    return _t(request, "roi.html", {
        "roi": roi, "sensitivity": sensitivity,
        "monthly_savings": monthly_savings, "total_investment": total, "investments": investments,
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
        fuel_prices = await db.execute("SELECT * FROM fuel_prices ORDER BY date DESC LIMIT 12")
        prices = [dict(r) for r in await fuel_prices.fetchall()]
        latest_fuel = prices[0] if prices else None
    finally:
        await db.close()

    # EV savings per month
    monthly_ev = []
    total_ev_savings = 0.0
    total_km = 0.0
    total_liters_saved = 0.0

    for r in readings:
        if not r.get("ev_kwh"):
            continue
        price = r.get("price_per_kwh") or 0.75
        fuel_price = latest_fuel["price_per_liter"] if latest_fuel else 6.5
        s = calc_ev_savings(
            r["ev_kwh"], price,
            settings.get("efficiency_kwh_per_100km", 16),
            settings.get("fuel_consumption_l_per_100km", 10),
            fuel_price,
        )
        monthly_ev.append({"period": r["period"], "ev_kwh": r["ev_kwh"], **s})
        total_ev_savings += s["ev_net_savings"]
        total_km += s["km_driven"]
        total_liters_saved += s["liters_saved"]

    return _t(request, "ev.html", {
        "settings": settings, "prices": prices, "latest_fuel": latest_fuel,
        "monthly_ev": list(reversed(monthly_ev)),
        "total_ev_savings": round(total_ev_savings, 2),
        "total_km": round(total_km, 1),
        "total_liters_saved": round(total_liters_saved, 2),
        "readings_without_ev": [r for r in readings if not r.get("ev_kwh")],
    })


@app.post("/ev/settings")
async def save_ev_settings(
    request: Request,
    efficiency_kwh_per_100km: float = Form(...),
    fuel_consumption_l_per_100km: float = Form(...),
    annual_km: float = Form(...),
    fuel_type: str = Form("PB95"),
    ha_url: str = Form(None),
    ha_token: str = Form(None),
    ha_entity: str = Form(None),
):
    db = await get_db()
    try:
        await db.execute(
            """UPDATE ev_settings SET efficiency_kwh_per_100km=?, fuel_consumption_l_per_100km=?,
               annual_km=?, fuel_type=?, ha_url=?, ha_token=?, ha_entity=? WHERE id=1""",
            (efficiency_kwh_per_100km, fuel_consumption_l_per_100km, annual_km,
             fuel_type, ha_url, ha_token, ha_entity),
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


@app.get("/ev/ha-fetch")
async def ha_fetch(period: str):
    """Pull EV kWh from Home Assistant entity for given period."""
    import httpx
    db = await get_db()
    try:
        settings = await _get_ev_settings(db)
    finally:
        await db.close()

    ha_url = (settings.get("ha_url") or os.getenv("HA_URL", "")).rstrip("/")
    ha_token = settings.get("ha_token") or os.getenv("HA_TOKEN", "")
    ha_entity = settings.get("ha_entity") or os.getenv("HA_ENTITY", "")

    if not all([ha_url, ha_token, ha_entity]):
        return JSONResponse({"error": "Skonfiguruj HA w ustawieniach EV"}, status_code=400)

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(
                f"{ha_url}/api/states/{ha_entity}",
                headers={"Authorization": f"Bearer {ha_token}"},
            )
        data = r.json()
        return JSONResponse({"state": data.get("state"), "unit": data.get("attributes", {}).get("unit_of_measurement")})
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
    finally:
        await db.close()

    total = sum(i["cost_pln"] for i in investments)
    roi_before = calc_roi(readings, total) if readings and total > 0 else {}

    # Apply hypothetical edit
    reading_id = data.get("id")
    patched = []
    for r in readings:
        if r["id"] == reading_id:
            patched.append({**r, **data})
        else:
            patched.append(r)

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
