<!-- GENEROWANE z PRD.md 2026-10-13 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Zadania - Wirtualny magazyn

| Zadanie | Tytuł | Typ | Wymaganie | Kryteria | Po | Uwagi |
|---|---|---|---|---|---|---|
| T-22 | Stan wirtualnego magazynu na dashboardzie | Z | R-021 | AC-021-1, AC-021-2, AC-021-3 | T-02, T-03, T-10 | Etykieta „Do odebrania z magazynu: X kWh”; wartość z carry_over_out ostatniego odczytu (D-035, D-036). Net-billing - Q-066 zaparkowane. |
| T-23 | Zakładka „Wirtualny magazyn” | Z | R-022 | AC-022-1, AC-022-2, AC-022-3, AC-022-4 | T-22 | Nowa trasa /magazyn i pozycja w menu; wykresy stanu w cyklu (z poprzednim cyklem) i przepływu miesiąca; podsumowanie cyklu z „przepadło”; obliczenia bez zmian (R-002). |
| T-24 | Szacunek stanu magazynu na dziś | Z | R-023 | AC-023-1, AC-023-2, AC-023-3, AC-023-4, AC-023-5 | T-23, T-20 | Liczniki bieżącego miesiąca z HA (S-002) przy otwarciu zakładki, bez zapisu; BR-001 w miesiącu startu cyklu; brak odczytu za poprzedni miesiąc - komunikat. |

Typ: W = weryfikacja działania obecnego, Z = zmiana, B = błąd.
