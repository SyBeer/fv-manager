"""Wirtualny magazyn (pula net-meteringu) — widok zakładki /magazyn (R-022, R-023).

Liczy wyłącznie z wyniku enrich_readings_sequence (R-002) — obliczenia puli się nie
zmieniają. Wszystkie wartości w kWh do odebrania (po współczynniku, D-035, D-036).
"""
from __future__ import annotations

from datetime import date

EPS = 0.001


def _ym(period: str) -> tuple[int, int]:
    y, m = period.split(".")
    return int(y), int(m)


def _period(y: int, m: int) -> str:
    return f"{y}.{m:02d}"


def _prev_period(y: int, m: int) -> str:
    return _period(y - 1, 12) if m == 1 else _period(y, m - 1)


def cycle_of(period: str, cycle_start_month: int) -> str:
    """Cykl rozliczeniowy okresu, np. '2025.04–2026.03' dla startu w kwietniu."""
    y, m = _ym(period)
    start_y = y if m >= cycle_start_month else y - 1
    end_m = cycle_start_month - 1 or 12
    end_y = start_y + 1 if cycle_start_month > 1 else start_y
    return f"{_period(start_y, cycle_start_month)}–{_period(end_y, end_m)}"


def months_to_reset(period: str, cycle_start_month: int) -> int:
    """Ile pełnych miesięcy po okresie zostało, zanim pula się wyzeruje (BR-001)."""
    _, m = _ym(period)
    return (cycle_start_month - m - 1) % 12


def monthly_rows(enriched: list[dict], ratio: float) -> list[dict]:
    """Przepływ magazynu dla każdego odczytu.

    wplynelo     — oddane × współczynnik (do odebrania z tego miesiąca)
    odebrane     — pobór pokryty z puli
    ponad_pule   — pobór niepokryty z puli (kupiony normalnie)
    stan         — do odebrania po miesiącu (carry_over_out)
    przepadlo_przed — stan poprzedniego miesiąca wyzerowany na starcie tego (BR-001)
    """
    rows = []
    prev_stan = 0.0
    for r in enriched:
        nm = r.get("model", "net_metering") == "net_metering"
        if not nm:
            rows.append({"period": r["period"], "model": "net_billing",
                         "oddane": r["sent_to_grid_kwh"], "pobrane": r["taken_from_grid_kwh"],
                         "wplynelo": None, "odebrane": None, "ponad_pule": None, "stan": None,
                         "przepadlo_przed": round(prev_stan, 3) if prev_stan > EPS else 0.0})
            prev_stan = 0.0
            continue
        wplynelo = r["sent_to_grid_kwh"] * ratio
        odebrane = r["pool_drawn_kwh"] * ratio
        stan = r["carry_over_out"]
        carry_in = stan + odebrane - wplynelo          # stan na początku miesiąca po ew. zerowaniu
        przepadlo = prev_stan if prev_stan > EPS and carry_in < prev_stan - EPS else 0.0
        rows.append({"period": r["period"], "model": "net_metering",
                     "oddane": r["sent_to_grid_kwh"], "pobrane": r["taken_from_grid_kwh"],
                     "wplynelo": round(wplynelo, 3), "odebrane": round(odebrane, 3),
                     "ponad_pule": round(r["taken_from_grid_kwh"] - odebrane, 3),
                     "stan": round(stan, 3), "przepadlo_przed": round(przepadlo, 3)})
        prev_stan = stan
    return rows


def cycle_summaries(rows: list[dict], cycle_start_month: int) -> list[dict]:
    """Podsumowanie każdego cyklu (najnowszy pierwszy); przepadło = stan zerowany po cyklu."""
    cycles: dict[str, dict] = {}
    order: list[str] = []
    prev_cycle = None
    for r in rows:
        c = cycle_of(r["period"], cycle_start_month)
        if c not in cycles:
            cycles[c] = {"cykl": c, "oddane": 0.0, "wplynelo": 0.0, "odebrane": 0.0,
                         "ponad_pule": 0.0, "przepadlo": 0.0, "miesiace": 0}
            order.append(c)
        s = cycles[c]
        s["miesiace"] += 1
        s["oddane"] += r["oddane"]
        for k in ("wplynelo", "odebrane", "ponad_pule"):
            s[k] += r[k] or 0.0
        if r["przepadlo_przed"]:
            # zerowanie na starcie cyklu dotyczy poprzedniego cyklu; przy zmianie modelu — bieżącego
            target = prev_cycle if prev_cycle and prev_cycle != c else c
            cycles[target]["przepadlo"] += r["przepadlo_przed"]
        prev_cycle = c
    out = []
    for c in reversed(order):
        s = cycles[c]
        out.append({k: (round(v, 1) if isinstance(v, float) else v) for k, v in s.items()})
    return out


def chart_data(rows: list[dict], cycle_start_month: int) -> dict:
    """Dane wykresów: stan w bieżącym cyklu na tle poprzedniego, przepływ bieżącego cyklu."""
    if not rows:
        return {"stan": {"labels": [], "biezacy": [], "poprzedni": []},
                "przeplyw": {"labels": [], "wplynelo": [], "odebrane": [], "ponad_pule": []}}
    cur = cycle_of(rows[-1]["period"], cycle_start_month)
    cur_rows = [r for r in rows if cycle_of(r["period"], cycle_start_month) == cur]
    start_y = int(cur[:4])
    prev = cycle_of(_period(start_y - 1, cycle_start_month), cycle_start_month)
    prev_by_m = {_ym(r["period"])[1]: r["stan"] for r in rows
                 if cycle_of(r["period"], cycle_start_month) == prev}
    cur_by_m = {_ym(r["period"])[1]: r for r in cur_rows}
    months = [((cycle_start_month - 1 + i) % 12) + 1 for i in range(12)]
    # jedna oś 12 miesięcy cyklu - oba cykle wyrównane po miesiącu kalendarzowym (luki = None)
    used = [months.index(m) for m in list(prev_by_m) + list(cur_by_m)]
    slots = months[:max(used) + 1]

    def _r(v):
        return None if v is None else round(v, 1)

    return {
        "cykl": cur, "poprzedni_cykl": prev,
        "stan": {
            "labels": [cur_by_m[m]["period"] if m in cur_by_m else f"mies. {m:02d}" for m in slots],
            "biezacy": [_r(cur_by_m[m]["stan"]) if m in cur_by_m else None for m in slots],
            "poprzedni": [_r(prev_by_m.get(m)) for m in slots],
        },
        "przeplyw": {
            "labels": [r["period"] for r in cur_rows],
            "wplynelo": [_r(r["wplynelo"]) for r in cur_rows],
            "odebrane": [_r(r["odebrane"]) for r in cur_rows],
            "ponad_pule": [_r(r["ponad_pule"]) for r in cur_rows],
        },
    }


def estimate_plan(rows: list[dict], today: date, cycle_start_month: int,
                  model_today: str) -> dict:
    """Czy i od jakiego stanu liczyć szacunek na dziś (R-023) — bez pytania HA.

    Zwraca {"status": "ok"|"brak_odczytu"|"odczyt_biezacy"|"net_billing"|"brak", ...}.
    """
    if not rows:
        return {"status": "brak"}
    last = rows[-1]
    cur = _period(today.year, today.month)
    if last["period"] >= cur:
        return {"status": "odczyt_biezacy", "period": last["period"]}
    expected_prev = _prev_period(today.year, today.month)
    if last["period"] != expected_prev:
        ly, lm = _ym(last["period"])
        od = _period(ly + 1, 1) if lm == 12 else _period(ly, lm + 1)
        brakuje = (today.year - ly) * 12 + today.month - lm - 1
        return {"status": "brak_odczytu", "period": expected_prev, "od": od, "brakuje": brakuje}
    if last["model"] != "net_metering" or model_today != "net_metering":
        return {"status": "net_billing"}
    reset = today.month == cycle_start_month
    return {"status": "ok", "period": cur, "start": 0.0 if reset else last["stan"], "reset": reset}


def estimate(start: float, sent_kwh: float, taken_kwh: float, ratio: float) -> float:
    """Stan do odebrania na dziś: start + oddane × współczynnik − pobrane (nie mniej niż 0)."""
    available = start + sent_kwh * ratio
    return round(max(0.0, available - min(available, taken_kwh)), 3)
