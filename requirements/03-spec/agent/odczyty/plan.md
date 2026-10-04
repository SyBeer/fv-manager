<!-- GENEROWANE z PRD.md 2026-10-04 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Plan - Odczyty miesięczne i import

## Kolejność
1. R-001 Wpisanie odczytu miesiąca - weryfikacja (działanie obecne - testy regresji z AC, poprawka różnic); zależy od: -
2. R-004 Import odczytów z CSV - cały plik albo nic - weryfikacja (działanie obecne - testy regresji z AC, poprawka różnic); zależy od: R-001 (T-04)
3. R-012 Lista i edycja odczytów - weryfikacja (działanie obecne - testy regresji z AC, poprawka różnic); zależy od: R-006 (T-08)

## Encje do odczytu (02-domain/ENTITIES.md)
## Odczyt miesiąca
Pola: okres (RRRR.MM), produkcja, oddane, pobrane, cena kWh, faktura; dane EV per pojazd (kWh domowe, km, stan licznika, ładowanie publiczne)
Stany: zapisany (z danymi EV), usunięty
Przejscia: [*] -> zapisany (Właściciel instalacji, po walidacji); zapisany -> zapisany (edycja, Właściciel instalacji); zapisany -> usunięty (Właściciel instalacji)
Zrodlo: [App] kod-v3.2.4-2026-09-27.md, Walidacja odczytów, main.py /odczyty/nowy; [Dok] README.md, /odczyty/{id}/usun
Zakwestionowane:
