<!-- GENEROWANE z PRD.md 2026-10-08 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Plan - Rozliczenia i ustawienia

## Kolejność
1. R-017 Okresy rozliczeniowe i ceny RCE - weryfikacja (działanie obecne - testy regresji z AC, poprawka różnic); zależy od: -
2. R-002 Oszczędność PV miesiąca - weryfikacja (działanie obecne - testy regresji z AC, poprawka różnic); zależy od: R-017 (T-01)
3. R-003 Ustawienie miesiąca startu cyklu rozliczeniowego - weryfikacja (działanie obecne - testy regresji z AC, poprawka różnic); zależy od: R-002 (T-02)

## Encje do odczytu (02-domain/ENTITIES.md)
## Okres rozliczeniowy
Pola: data startu, model rozliczeń (net-metering / net-billing)
Stany: ustawiony
Przejscia: [*] -> ustawiony (Właściciel instalacji, D-004)
Zrodlo: [App] kod-v3.2.4-2026-09-27.md, Net-billing i RCE; [Biz] D-004; miesiąc liczony wg okresu obowiązującego 1. dnia miesiąca (D-032, BR-013)
Zakwestionowane:
## Odczyt miesiąca
Pola: okres (RRRR.MM), produkcja, oddane, pobrane (S-002), cena kWh (S-003, BR-014), faktura - numer i kwota brutto, pomocnicze do odnalezienia faktury, poza obliczeniami (S-003, D-033); dane EV per pojazd (kWh domowe - S-009, km i stan licznika - S-007, ładowanie publiczne kWh i koszt - S-008)
Stany: zapisany (z danymi EV), usunięty
Przejscia: [*] -> zapisany (Właściciel instalacji, po walidacji); zapisany -> zapisany (edycja, Właściciel instalacji); zapisany -> usunięty (Właściciel instalacji)
Zrodlo: [App] kod-v3.2.4-2026-09-27.md, Walidacja odczytów, main.py /odczyty/nowy; [Dok] README.md, /odczyty/{id}/usun
Zakwestionowane:
