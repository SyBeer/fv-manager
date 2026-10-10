<!-- GENEROWANE z PRD.md 2026-10-08 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Zadania - Odczyty miesięczne i import

| Zadanie | Tytuł | Typ | Wymaganie | Kryteria | Po | Uwagi |
|---|---|---|---|---|---|---|
| T-04 | Wpisanie odczytu miesiąca | W | R-001 | AC-001-1, AC-001-2, AC-001-3, AC-001-4, AC-001-5, AC-001-6 | - | AC-001-5: km ze stanu licznika (BR-011, D-026) - działa (_inject_odometer_km), dopisz test. AC-001-6 (D-033): kwota faktury poza obliczeniami - działa w v3.4.0 (src/main.py:734), dopisz test. |
| T-05 | Import odczytów z CSV - cały plik albo nic | W | R-004 | AC-004-1, AC-004-2 | T-04 |  |
| T-06 | Lista i edycja odczytów | W | R-012 | AC-012-1, AC-012-2 | T-08 |  |

Typ: W = weryfikacja działania obecnego, Z = zmiana, B = błąd.
