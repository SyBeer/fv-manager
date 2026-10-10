<!-- GENEROWANE z PRD.md 2026-10-08 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Zadania - Rozliczenia i ustawienia

| Zadanie | Tytuł | Typ | Wymaganie | Kryteria | Po | Uwagi |
|---|---|---|---|---|---|---|
| T-01 | Okresy rozliczeniowe i ceny RCE | W | R-017 | AC-017-1, AC-017-2, AC-017-3, AC-017-4, AC-017-5 | - | AC-017-5 (D-032, BR-013): okres od środka miesiąca - działa w v3.4.0 (_get_billing_model), dopisz test. |
| T-02 | Oszczędność PV miesiąca | W | R-002 | AC-002-1, AC-002-2, AC-002-3, AC-002-4, AC-002-5 | T-01 | AC-002-5 (D-031, BR-014): cena domyślna kWh przy pustej cenie w odczycie - działa w v3.4.0 (src/main.py:26), dopisz test. |
| T-03 | Ustawienie miesiąca startu cyklu rozliczeniowego | W | R-003 | AC-003-1, AC-003-2 | T-02 |  |

Typ: W = weryfikacja działania obecnego, Z = zmiana, B = błąd.
