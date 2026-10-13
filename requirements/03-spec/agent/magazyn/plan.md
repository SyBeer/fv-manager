<!-- GENEROWANE z PRD.md 2026-10-13 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Plan - Wirtualny magazyn

## Kolejność
1. R-021 Stan wirtualnego magazynu na dashboardzie - zmiana (nowy element dashboardu); zależy od: R-002 (T-02), R-003 (T-03), R-008 (T-10)
2. R-022 Zakładka „Wirtualny magazyn” - zmiana (nowa zakładka); zależy od: R-021 (T-22), R-002 (T-02), R-003 (T-03)
3. R-023 Szacunek stanu magazynu na dziś - zmiana (nowe użycie HA); zależy od: R-022 (T-23), R-020 (T-20)

## Uwagi do budowy
- Liczba do pokazania = kWh do odebrania (stan puli × współczynnik, D-036). Kod przechowuje pulę po współczynniku (carry_over_out); przepływ puli w kWh oddanych: pool_in_kwh, pool_drawn_kwh, pool_out_kwh (v3.6.0).
- Odebrane z magazynu = pobór pokryty z puli; pobrane ponad pulę = pobrane − odebrane; przepadło = stan do odebrania na koniec cyklu, zerowany w miesiącu startu cyklu albo przy zmianie modelu (BR-001).
- Szacunek na dziś (R-023) nie zapisuje niczego do bazy (AC-020-2, AC-023-5).
- Ostatni odczyt w okresie net-billingu - zachowanie nieustalone (Q-066, zaparkowane); nie wymyślaj go.

## Encje do odczytu (02-domain/ENTITIES.md)
## Odczyt miesiąca
Pola: okres (RRRR.MM), produkcja, oddane, pobrane (S-002), cena kWh (S-003, BR-014), faktura - numer i kwota brutto, pomocnicze do odnalezienia faktury, poza obliczeniami (S-003, D-033); dane EV per pojazd (kWh domowe - S-009, km i stan licznika - S-007, ładowanie publiczne kWh i koszt - S-008)
Stany: zapisany (z danymi EV), usunięty
Przejscia: [*] -> zapisany (Właściciel instalacji, po walidacji); zapisany -> zapisany (edycja, Właściciel instalacji); zapisany -> usunięty (Właściciel instalacji)
Zrodlo: [App] kod-v3.2.4-2026-09-27.md, Walidacja odczytów, main.py /odczyty/nowy; [Dok] README.md, /odczyty/{id}/usun
Zakwestionowane:

## Integracje
- S-002 Home Assistant (R-023): liczniki bieżącego miesiąca do dziś (oddane, pobrane) przy otwarciu /magazyn; przy braku danych - komunikat „Brak danych z Home Assistant”, reszta zakładki działa. Adapter: src/services/ha_stats.py get_current_month_energy (BR-009).
