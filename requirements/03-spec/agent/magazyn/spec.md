<!-- GENEROWANE z PRD.md 2026-10-12 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Wirtualny magazyn

### R-021 Stan wirtualnego magazynu na dashboardzie
Opis:              Dashboard pokazuje stan wirtualnego magazynu jako „Do odebrania z magazynu: X kWh” - ile energii właściciel może jeszcze odebrać z sieci w bieżącym cyklu rozliczeniowym po ostatnim zapisanym odczycie, już po współczynniku net-meteringu (D-035): stan puli × współczynnik (D-036). Wartość pochodzi z tego samego wyliczenia co oszczędność PV miesiąca (R-002); obliczenia się nie zmieniają. Stan magazynu to kWh do odebrania, a nie oszczędność w zł. Pokazanie stanu w miesiącach net-billingu - Q-066.
Zrodlo:            [Biz] session-2026-10-12.md, pomysł, Q-064, Q-065, Q-067 (D-035, D-036); [App] src/services/calculations.py:43 (carry_over_out liczone, niewyświetlane)
Zalozenia:         A-005
Reguly:            BR-001, BR-004
Status:            zatwierdzone (właściciel instalacji, 2026-10-12)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-021-1: Given okres w net-meteringu, współczynnik 0,80, pula 0 i ostatni odczyt: produkcja 500, oddane 300, pobrane 200 kWh, When właściciel otwiera dashboard, Then widzi „Do odebrania z magazynu: 40 kWh”.
- AC-021-2: Given miesiąc startu cyklu = kwiecień, 40 kWh do odebrania po marcu i ostatni odczyt za kwiecień: oddane 100, pobrane 50 kWh, When właściciel otwiera dashboard, Then widzi „Do odebrania z magazynu: 30 kWh” (pula z marca przepadła, BR-001).
- AC-021-3: Given zapisany odczyt za 2026.08 i na dashboardzie 40 kWh do odebrania z magazynu, When właściciel zapisuje odczyt za 2026.09 z oddane 0 i pobrane 25 kWh, Then dashboard pokazuje 15 kWh.
