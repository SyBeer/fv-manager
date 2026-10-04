<!-- GENEROWANE z PRD.md 2026-10-04 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Zadania - Wycofanie Tesla Fleet API

| Zadanie | Tytuł | Typ | Wymaganie | Kryteria | Po | Uwagi |
|---|---|---|---|---|---|---|
| T-18 | Wycofanie integracji z Tesla Fleet API | Z | R-018 | AC-018-1, AC-018-2, AC-018-3 | - | Usuń kolumny tesla_* (src/utils/db.py:200) migracją, wzmianki w templates/ev.html i README; wpis w CHANGELOG aplikacji (D-020). |

Typ: W = weryfikacja działania obecnego, Z = zmiana, B = błąd.
