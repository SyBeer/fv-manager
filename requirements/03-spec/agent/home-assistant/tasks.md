<!-- GENEROWANE z PRD.md 2026-10-08 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Zadania - Integracja z Home Assistant

| Zadanie | Tytuł | Typ | Wymaganie | Kryteria | Po | Uwagi |
|---|---|---|---|---|---|---|
| T-20 | Kontrakt: liczniki energii z Home Assistant (wejście) | W | R-020 | AC-020-1, AC-020-2, AC-020-3 | T-04 | Działa w v3.4.0 (src/main.py:2155-2190 ha-grid-fetch, ha-solar-fetch) - dopisz testy kontraktu; bez mockowania realnego HA w teście integracyjnym. |
| T-16 | Integracja z Home Assistant | Z | R-015 | AC-015-1, AC-015-2 | T-20 | Zmiana: AC-015-2 (D-030) - usuń /api/summary (endpoint, opis w README); test połączenia i pobieranie liczników bez zmian. |

Typ: W = weryfikacja działania obecnego, Z = zmiana, B = błąd.
