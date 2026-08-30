"""Testy rozdzielenia ładowania domowego od publicznego.

Model:
- Opłacalność FV/PV (readings.ev_savings_pln via _ev_enrich) — TYLKO ładowanie domowe.
- Opłacalność auta vs paliwo (agregat pojazdu) — domowe + publiczne, rozbite na dwie pozycje:
  savings_home (FV), savings_public (unikniete_paliwo(public_km) - public_cost_pln), oraz suma.
Kolumny `kwh`/`km` znaczą "domowe".
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


def _full_entry():
    return {
        "period": "2025.01", "vehicle_id": 1,
        "kwh": 100.0, "km": 500.0,
        "public_kwh": 50.0, "public_km": 200.0, "public_cost_pln": 180.0,
    }


def test_fv_savings_home_component():
    """savings_home = oszczędność FV z ładowania domowego (500 km, 100 kWh)."""
    v = _agg_vehicles_ev([_vehicle()], [_full_entry()], {"2025.01": 0.8}, FUEL, 0.8)[0]
    # fuel 500/100*8*6 = 240 ; elec 100*0.8 = 80 ; net 160
    assert v["total_savings_home"] == 160.0
    assert v["total_kwh"] == 100.0     # tylko home
    assert v["total_km"] == 500.0      # tylko home (FV)


def test_public_savings_component():
    """savings_public = uniknięte_paliwo(public_km) - public_cost_pln (może być ujemne)."""
    v = _agg_vehicles_ev([_vehicle()], [_full_entry()], {"2025.01": 0.8}, FUEL, 0.8)[0]
    # fuel avoided 200/100*8*6 = 96 ; koszt public 180 ; net = -84
    assert v["total_savings_public"] == -84.0


def test_car_total_savings_is_home_plus_public():
    """'vs paliwo' = savings_home + savings_public."""
    v = _agg_vehicles_ev([_vehicle()], [_full_entry()], {"2025.01": 0.8}, FUEL, 0.8)[0]
    assert v["total_savings"] == 76.0   # 160 + (-84)


def test_public_charging_reported_separately():
    """Publiczne kWh/km/koszt zwracane osobno."""
    v = _agg_vehicles_ev([_vehicle()], [_full_entry()], {"2025.01": 0.8}, FUEL, 0.8)[0]
    assert v["total_public_kwh"] == 50.0
    assert v["total_public_km"] == 200.0
    assert v["total_public_cost"] == 180.0


def test_total_mileage_includes_public():
    """Całkowity przebieg = home_km + public_km."""
    v = _agg_vehicles_ev([_vehicle()], [_full_entry()], {"2025.01": 0.8}, FUEL, 0.8)[0]
    assert v["total_km_all"] == 700.0


def test_public_only_month_still_aggregated():
    """Miesiąc bez ładowania domowego (tylko public) — pojazd raportowany, savings_public liczone."""
    ev = [{
        "period": "2025.01", "vehicle_id": 1,
        "kwh": None, "km": None,
        "public_kwh": 30.0, "public_km": 120.0, "public_cost_pln": 100.0,
    }]
    out = _agg_vehicles_ev([_vehicle()], ev, {"2025.01": 0.8}, FUEL, 0.8)
    assert len(out) == 1
    v = out[0]
    assert v["total_savings_home"] == 0.0
    # fuel avoided 120/100*8*6 = 57.6 ; koszt 100 ; net = -42.4
    assert v["total_savings_public"] == -42.4
    assert v["total_savings"] == -42.4
    assert v["total_km_all"] == 120.0


def test_legacy_entry_without_public_fields():
    """Stare wpisy bez pól public działają jak dziś (public = 0, savings = home)."""
    ev = [{"period": "2025.01", "vehicle_id": 1, "kwh": 100.0, "km": 500.0}]
    v = _agg_vehicles_ev([_vehicle()], ev, {"2025.01": 0.8}, FUEL, 0.8)[0]
    assert v["total_savings_home"] == 160.0
    assert v["total_savings_public"] == 0.0
    assert v["total_savings"] == 160.0
    assert v["total_public_kwh"] == 0.0
    assert v["total_km_all"] == 500.0


def test_ev_enrich_ignores_public_fields():
    """Opłacalność FV (_ev_enrich) liczy savings TYLKO z home kwh/km — public nie wpływa."""
    readings = [{"period": "2025.01", "production_kwh": 300.0, "sent_to_grid_kwh": 100.0,
                 "taken_from_grid_kwh": 50.0, "price_per_kwh": 0.8}]
    ev = [{"period": "2025.01", "vehicle_id": 1, "kwh": 100.0, "km": 500.0,
           "public_kwh": 999.0, "public_km": 999.0, "public_cost_pln": 999.0}]
    out = _ev_enrich(readings, {}, FUEL, [_vehicle()], ev)
    assert out[0]["ev_savings_pln"] == 160.0   # tylko home
