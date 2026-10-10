<!-- GENEROWANE z PRD.md 2026-10-08 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Zadania - Pojazdy EV i ceny paliwa

| Zadanie | Tytuł | Typ | Wymaganie | Kryteria | Po | Uwagi |
|---|---|---|---|---|---|---|
| T-11 | Dodanie pojazdu | Z | R-009 | AC-009-1, AC-009-2, AC-009-3, AC-009-4 | - | Zmiana: AC-009-3, AC-009-4 (D-027, BR-012) - dziś zmiana przebiegu startowego wyższego niż najniższy stan licznika jest blokowana (src/main.py:1684-1690). Usuwany tylko stan licznika, dane ładowania zostają. |
| T-12 | Oszczędności EV | B | R-010 | AC-010-1, AC-010-2, AC-010-3, AC-010-4 | T-11 | Błąd: AC-010-3, AC-010-4 (D-023, D-029) - karty /ev (src/main.py:369-372) i ROI (_ev_enrich, 437-443) dobierają cenę paliwa różnie; jedna reguła: paliwo pojazdu, ostatnia cena do końca miesiąca. Miesiące przed pierwszą ceną - wg pierwszej ceny (AC-010-4, D-029); dziś ROI bierze najstarszą cenę dowolnego paliwa, /ev najnowszą. |
| T-13 | Śledzenie cen paliwa | W | R-011 | AC-011-1, AC-011-2, AC-011-3, AC-011-4 | T-11 | AC-011-4 (D-024) działa od v3.3.0 (POST /ev/fuel-tracking) - dopisz test, jeśli brak. |

Typ: W = weryfikacja działania obecnego, Z = zmiana, B = błąd.
