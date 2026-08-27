"""Testy rozdzielenia ładowania domowego (liczone do FV) od publicznego (poza FV).

Spec: publiczne kWh/km/koszt są zapisywane i raportowane osobno, ale NIE wpływają
na wynik opłacalności FV. Kolumny `kwh`/`km` znaczą "domowe".
"""
from main import _agg_vehicles_ev, _ev_enrich


def _vehicle(vid=1):
    return {
        "id": vid,
        "name": "Auto",
        "fuel_type": "petrol",
        "efficiency_kwh_per_100km": 16.0,
        "fuel_consumption_l_per_100km": 8.0,
    }


FUEL = [{"fuel_type": "petrol", "date": "2025-01-31", "price_per_liter": 6.0}]


def test_public_charging_excluded_from_fv_savings():
    """AC1/AC2: do oszczędności FV wchodzą tylko domowe kWh i km; public pomijane."""
    ev = [{
        "period": "2025.01", "vehicle_id": 1,
        "kwh": 100.0, "km": 500.0,
        "public_kwh": 50.0, "public_km": 200.0, "public_cost_pln": 180.0,
    }]
    out = _agg_vehicles_ev([_vehicle()], ev, {"2025.01": 0.8}, FUEL, 0.8)
    v = out[0]
    # oszczędność FV liczona z home: km=500, kwh=100
    expected_fuel = 500 / 100 * 8.0 * 6.0        # 240
    expected_elec = 100.0 * 0.8                    # 80
    assert v["total_savings"] == round(expected_fuel - expected_elec, 2)  # 160.0
    assert v["total_kwh"] == 100.0                 # tylko home
    assert v["total_km"] == 500.0                  # tylko home (FV)


def test_public_charging_reported_separately():
    """AC3: publiczne kWh/km/koszt zwracane osobno w agregacie pojazdu."""
    ev = [{
        "period": "2025.01", "vehicle_id": 1,
        "kwh": 100.0, "km": 500.0,
        "public_kwh": 50.0, "public_km": 200.0, "public_cost_pln": 180.0,
    }]
    v = _agg_vehicles_ev([_vehicle()], ev, {"2025.01": 0.8}, FUEL, 0.8)[0]
    assert v["total_public_kwh"] == 50.0
    assert v["total_public_km"] == 200.0
    assert v["total_public_cost"] == 180.0


def test_total_mileage_includes_public():
    """AC4: całkowity przebieg = home_km + public_km."""
    ev = [{
        "period": "2025.01", "vehicle_id": 1,
        "kwh": 100.0, "km": 500.0,
        "public_kwh": 50.0, "public_km": 200.0, "public_cost_pln": 180.0,
    }]
    v = _agg_vehicles_ev([_vehicle()], ev, {"2025.01": 0.8}, FUEL, 0.8)[0]
    assert v["total_km_all"] == 700.0


def test_public_only_month_still_aggregated():
    """Miesiąc bez ładowania domowego (tylko public) — pojazd nadal raportowany."""
    ev = [{
        "period": "2025.01", "vehicle_id": 1,
        "kwh": None, "km": None,
        "public_kwh": 30.0, "public_km": 120.0, "public_cost_pln": 100.0,
    }]
    out = _agg_vehicles_ev([_vehicle()], ev, {"2025.01": 0.8}, FUEL, 0.8)
    assert len(out) == 1
    v = out[0]
    assert v["total_kwh"] == 0.0
    assert v["total_savings"] == 0.0
    assert v["total_public_kwh"] == 30.0
    assert v["total_public_km"] == 120.0
    assert v["total_public_cost"] == 100.0
    assert v["total_km_all"] == 120.0


def test_legacy_entry_without_public_fields():
    """AC6: stare wpisy bez pól public działają jak dziś (public = 0)."""
    ev = [{"period": "2025.01", "vehicle_id": 1, "kwh": 100.0, "km": 500.0}]
    v = _agg_vehicles_ev([_vehicle()], ev, {"2025.01": 0.8}, FUEL, 0.8)[0]
    assert v["total_public_kwh"] == 0.0
    assert v["total_public_km"] == 0.0
    assert v["total_public_cost"] == 0.0
    assert v["total_km_all"] == 500.0
    assert v["total_savings"] == 160.0


def test_ev_enrich_ignores_public_fields():
    """AC1: _ev_enrich liczy savings tylko z home kwh/km, nawet gdy entry ma public_*."""
    readings = [{"period": "2025.01", "production_kwh": 300.0, "sent_to_grid_kwh": 100.0,
                 "taken_from_grid_kwh": 50.0, "price_per_kwh": 0.8}]
    ev = [{"period": "2025.01", "vehicle_id": 1, "kwh": 100.0, "km": 500.0,
           "public_kwh": 999.0, "public_km": 999.0, "public_cost_pln": 999.0}]
    out = _ev_enrich(readings, {}, FUEL, [_vehicle()], ev)
    # savings identyczne jak bez pól public (240 - 80 = 160)
    assert out[0]["ev_savings_pln"] == 160.0
