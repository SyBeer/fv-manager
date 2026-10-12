<!-- GENEROWANE z PRD.md 2026-10-12 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Plan - Wirtualny magazyn

## Kolejność
1. R-021 Stan wirtualnego magazynu na dashboardzie - zmiana (nowy element dashboardu); zależy od: R-002 (T-02), R-003 (T-03), R-008 (T-10)

## Uwagi do budowy
- Liczba do pokazania = kWh do odebrania po ostatnim odczycie (stan puli × współczynnik, D-036). Kod v3.5.0 przechowuje pulę już po współczynniku (src/services/calculations.py:39-43, carry_over_out) - ta wartość jest liczbą do odebrania; zmiana sposobu przechowywania puli nie jest wymagana.
- Ostatni odczyt w okresie net-billingu - zachowanie nieustalone (Q-066, zaparkowane); nie wymyślaj go.

## Encje do odczytu (02-domain/ENTITIES.md)
## Odczyt miesiąca
Pola: okres (RRRR.MM), produkcja, oddane, pobrane (S-002), cena kWh (S-003, BR-014), faktura - numer i kwota brutto, pomocnicze do odnalezienia faktury, poza obliczeniami (S-003, D-033); dane EV per pojazd (kWh domowe - S-009, km i stan licznika - S-007, ładowanie publiczne kWh i koszt - S-008)
Stany: zapisany (z danymi EV), usunięty
Przejscia: [*] -> zapisany (Właściciel instalacji, po walidacji); zapisany -> zapisany (edycja, Właściciel instalacji); zapisany -> usunięty (Właściciel instalacji)
Zrodlo: [App] kod-v3.2.4-2026-09-27.md, Walidacja odczytów, main.py /odczyty/nowy; [Dok] README.md, /odczyty/{id}/usun
Zakwestionowane:

## Integracje
Brak - wartość liczona z zapisanych odczytów.
