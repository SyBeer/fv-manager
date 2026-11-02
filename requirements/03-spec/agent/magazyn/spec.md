<!-- GENEROWANE z PRD.md 2026-10-13 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

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

### R-022 Zakładka „Wirtualny magazyn”
Opis:              Zakładka /magazyn w menu pokazuje stan wirtualnego magazynu (puli net-meteringu) w kWh do odebrania (D-035, D-036): karty - do odebrania po ostatnim odczycie i liczba miesięcy do wyzerowania puli (miesiąc startu cyklu, BR-001); wykres stanu magazynu miesiąc po miesiącu w bieżącym cyklu rozliczeniowym na tle poprzedniego cyklu; wykres przepływu miesiąca - wpłynęło do magazynu (oddane × współczynnik), odebrane z magazynu (pobór pokryty z puli) i pobrane ponad pulę (pobór niepokryty z puli); podsumowanie cyklu (oddane, wpłynęło, odebrane, pobrane ponad pulę, przepadło przy zerowaniu) i tabela miesięcy. Wartości z tego samego wyliczenia co oszczędność PV miesiąca (R-002) - obliczenia się nie zmieniają. Miesiące w net-billingu - Q-066.
Zrodlo:            [Biz] session-2026-10-13.md, pomysł, Q-068, Q-069, Q-070; [Biz] session-2026-10-12.md (D-035, D-036); [App] src/services/calculations.py (carry_over_out, pool_*)
Zalozenia:         A-005
Reguly:            BR-001, BR-004
Status:            zatwierdzone (właściciel instalacji, 2026-10-13)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-022-1: Given miesiąc startu cyklu = kwiecień, współczynnik 0,80 i odczyty 2026.04 (oddane 300, pobrane 200 kWh) i 2026.05 (oddane 100, pobrane 50 kWh), When właściciel otwiera /magazyn, Then wykres stanu magazynu pokazuje 40 kWh za 2026.04 i 70 kWh za 2026.05.
- AC-022-2: Given odczyty z AC-022-1 i odczyt 2026.06 (oddane 0, pobrane 100 kWh), When właściciel otwiera /magazyn, Then za 2026.06 widzi: odebrane z magazynu 70 kWh, pobrane ponad pulę 30 kWh, stan 0 kWh.
- AC-022-3: Given 40 kWh do odebrania po odczycie 2026.03 i odczyt 2026.04 (oddane 0, pobrane 0), When właściciel otwiera /magazyn, Then podsumowanie cyklu 2025.04-2026.03 pokazuje „przepadło 40 kWh”.
- AC-022-4: Given miesiąc startu cyklu = kwiecień i ostatni odczyt 2026.05, When właściciel otwiera /magazyn, Then karta pokazuje „do wyzerowania: 10 mies.”.

### R-023 Szacunek stanu magazynu na dziś
Opis:              Zakładka /magazyn pokazuje „szacunek na dziś”: stan po ostatnim odczycie powiększony o oddane × współczynnik i pomniejszony o pobrane w bieżącym miesiącu do dziś, z liczników Home Assistant (S-002) pobieranych przy otwarciu zakładki. Szacunek niczego nie zapisuje - odczyty i ich wartości zostają bez zmian (R-020). Gdy bieżący miesiąc jest miesiącem startu cyklu, szacunek liczy się od 0 (BR-001). Gdy brakuje odczytu za poprzedni miesiąc, szacunku nie ma - zakładka prosi o uzupełnienie odczytu. Gdy HA nie ma danych - komunikat, reszta zakładki działa.
Zrodlo:            [Biz] session-2026-10-13.md, pomysł („na bieżąco”), Q-068; [App] src/services/ha_stats.py:259 get_current_month_energy
Zalozenia:         A-005
Reguly:            BR-001, BR-004, BR-009
Status:            zatwierdzone (właściciel instalacji, 2026-10-13)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-023-1: Given 40 kWh do odebrania po odczycie 2026.09, dziś 2026-10-13 i w HA za październik do dziś: oddane 50, pobrane 20 kWh, When właściciel otwiera /magazyn, Then widzi „Szacunek na dziś: 60 kWh”.
- AC-023-2: Given miesiąc startu cyklu = kwiecień, 40 kWh po odczycie 2026.03, dziś 2026-04-10 i w HA za kwiecień: oddane 10, pobrane 0 kWh, When właściciel otwiera /magazyn, Then widzi „Szacunek na dziś: 8 kWh” (pula z marca przepadła).
- AC-023-3: Given ostatni odczyt 2026.09, dziś 2026-10-13 i HA bez danych, When właściciel otwiera /magazyn, Then widzi komunikat „Brak danych z Home Assistant”, a karty, wykresy i tabela są pokazane.
- AC-023-4: Given ostatni odczyt 2026.08 i dziś 2026-10-13, When właściciel otwiera /magazyn, Then zamiast szacunku widzi „Uzupełnij odczyt za 2026.09”.
- AC-023-5: Given zapisany odczyt 2026.09 i szacunek z HA na zakładce, When właściciel otwiera listę odczytów, Then wartości odczytu 2026.09 są takie jak przy zapisie.
