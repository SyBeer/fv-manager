<!-- GENEROWANE z PRD.md 2026-10-08 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Plan - Odczyty miesięczne i import

## Kolejność
1. R-001 Wpisanie odczytu miesiąca - weryfikacja (działanie obecne - testy regresji z AC, poprawka różnic); zależy od: -
2. R-004 Import odczytów z CSV - cały plik albo nic - weryfikacja (działanie obecne - testy regresji z AC, poprawka różnic); zależy od: R-001 (T-04)
3. R-012 Lista i edycja odczytów - weryfikacja (działanie obecne - testy regresji z AC, poprawka różnic); zależy od: R-006 (T-08)

## Encje do odczytu (02-domain/ENTITIES.md)
## Odczyt miesiąca
Pola: okres (RRRR.MM), produkcja, oddane, pobrane (S-002), cena kWh (S-003, BR-014), faktura - numer i kwota brutto, pomocnicze do odnalezienia faktury, poza obliczeniami (S-003, D-033); dane EV per pojazd (kWh domowe - S-009, km i stan licznika - S-007, ładowanie publiczne kWh i koszt - S-008)
Stany: zapisany (z danymi EV), usunięty
Przejscia: [*] -> zapisany (Właściciel instalacji, po walidacji); zapisany -> zapisany (edycja, Właściciel instalacji); zapisany -> usunięty (Właściciel instalacji)
Zrodlo: [App] kod-v3.2.4-2026-09-27.md, Walidacja odczytów, main.py /odczyty/nowy; [Dok] README.md, /odczyty/{id}/usun
Zakwestionowane:

## Integracje (02-domain/SYSTEMS.md)
| ID | System | Wymiana | Przy awarii |
|---|---|---|---|
| S-002 | Home Assistant | liczniki -> my na żądanie przy wpisie odczytu | komunikat „Brak danych dla <encja> za RRRR-MM”, odczyt nie blokowany, wpis ręczny |
| S-003 | Faktura operatora sieci | cena kWh, faktura - wpis ręczny raz w miesiącu | brak ceny kWh - cena domyślna z konfiguracji add-onu (D-031) |
| S-006 | Plik CSV | import odczytów (R-004), eksport (R-013) | import: cały plik albo nic (BR-002) |
| S-007 | Aplikacja Tesla (telefon) | km i stan licznika - wpis ręczny | ? (nie wystąpiło) |
| S-008 | Aplikacja operatora ładowarki | kWh i koszt ładowania publicznego - wpis ręczny | pola puste, uzupełnienie później edycją odczytu (R-012) |
| S-009 | Domowe liczniki energii | kWh ładowania domowego - wpis ręczny | dotąd zawsze możliwy; inaczej szacunek kWh |
