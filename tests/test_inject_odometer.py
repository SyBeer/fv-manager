"""Testy _inject_odometer_km — anchor przebieg_km dla pierwszego miesiąca pojazdu."""
from main import _inject_odometer_km


def _km(rows, period, vid=1):
    return next(r["km"] for r in rows if r["period"] == period and r["vehicle_id"] == vid)


def test_first_month_anchored_to_przebieg():
    """Pierwszy wpis z odometer + vehicles.przebieg_km → km = odometer - przebieg (bez estymaty)."""
    ev = [{"period": "2025.12", "vehicle_id": 1, "kwh": 90.0, "km": None, "odometer_km": 6000.0}]
    vehicles = [{"id": 1, "przebieg_km": 5000.0}]
    out = _inject_odometer_km(ev, vehicles)
    assert _km(out, "2025.12") == 1000.0


def test_first_month_anchor_then_delta():
    """Pierwszy miesiąc kotwiczony do przebiegu, kolejny liczy deltę względem poprzedniego odometra."""
    ev = [
        {"period": "2025.12", "vehicle_id": 1, "kwh": 90.0, "km": None, "odometer_km": 6000.0},
        {"period": "2026.01", "vehicle_id": 1, "kwh": 120.0, "km": None, "odometer_km": 6500.0},
    ]
    vehicles = [{"id": 1, "przebieg_km": 5000.0}]
    out = _inject_odometer_km(ev, vehicles)
    assert _km(out, "2025.12") == 1000.0
    assert _km(out, "2026.01") == 500.0


def test_first_month_no_odometer_stays_none():
    """Pierwszy wpis bez odometra → km pozostaje None (fallback do estymaty z kWh)."""
    ev = [{"period": "2025.12", "vehicle_id": 1, "kwh": 90.0, "km": None, "odometer_km": None}]
    vehicles = [{"id": 1, "przebieg_km": 5000.0}]
    out = _inject_odometer_km(ev, vehicles)
    assert _km(out, "2025.12") is None


def test_first_month_no_przebieg_stays_none():
    """Pierwszy wpis z odometrem, ale brak przebieg_km → brak kotwicy → km None."""
    ev = [{"period": "2025.12", "vehicle_id": 1, "kwh": 90.0, "km": None, "odometer_km": 6000.0}]
    vehicles = [{"id": 1, "przebieg_km": None}]
    out = _inject_odometer_km(ev, vehicles)
    assert _km(out, "2025.12") is None


def test_manual_km_preserved():
    """Ręczne km ma priorytet — nie nadpisywane anchorem."""
    ev = [{"period": "2025.12", "vehicle_id": 1, "kwh": 90.0, "km": 333.0, "odometer_km": 6000.0}]
    vehicles = [{"id": 1, "przebieg_km": 5000.0}]
    out = _inject_odometer_km(ev, vehicles)
    assert _km(out, "2025.12") == 333.0


def test_anchor_never_negative():
    """Gdy przebieg_km > pierwszy odometer (niespójne dane) → km = 0, nie ujemne."""
    ev = [{"period": "2025.12", "vehicle_id": 1, "kwh": 90.0, "km": None, "odometer_km": 4000.0}]
    vehicles = [{"id": 1, "przebieg_km": 5000.0}]
    out = _inject_odometer_km(ev, vehicles)
    assert _km(out, "2025.12") == 0.0


def test_backward_compat_no_vehicles_arg():
    """Bez argumentu vehicles — zachowanie jak dotychczas: delta tylko między kolejnymi odczytami."""
    ev = [
        {"period": "2025.12", "vehicle_id": 1, "kwh": 90.0, "km": None, "odometer_km": 6000.0},
        {"period": "2026.01", "vehicle_id": 1, "kwh": 120.0, "km": None, "odometer_km": 6500.0},
    ]
    out = _inject_odometer_km(ev)  # brak vehicles
    assert _km(out, "2025.12") is None      # pierwszy bez kotwicy
    assert _km(out, "2026.01") == 500.0     # delta między kolejnymi
