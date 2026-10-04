<!-- GENEROWANE z PRD.md 2026-10-04 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Zadania - Inwestycje, ROI i prognoza

| Zadanie | Tytuł | Typ | Wymaganie | Kryteria | Po | Uwagi |
|---|---|---|---|---|---|---|
| T-07 | Etapy inwestycji | W | R-005 | AC-005-1, AC-005-2, AC-005-3, AC-005-4, AC-005-5, AC-005-6 | - | Q-032 (data spoza okresu odczytów) otwarte - bez walidacji daty. |
| T-08 | Pozostało do zwrotu | B | R-006 | AC-006-1, AC-006-2, AC-006-3, AC-006-4 | T-02, T-07, T-12 | AC-006-3 to błąd v3.2.x (D-015): etapy liczone od początku zamiast od swojej daty. |
| T-09 | Prognoza zwrotu | Z | R-007 | AC-007-1, AC-007-2, AC-007-3 | T-08 | AC-007-3: tabela scenariuszy pokazuje N > 36 (D-013, D-019); wykres zostaje 36 mies. |
| T-10 | Ekran ROI i dashboard | W | R-008 | AC-008-1, AC-008-2, AC-008-3 | T-08, T-09 |  |

Typ: W = weryfikacja działania obecnego, Z = zmiana, B = błąd.
