<!-- GENEROWANE z PRD.md 2026-10-10 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Plan - Wycofanie Tesla Fleet API

## Kolejność
1. R-018 Wycofanie integracji z Tesla Fleet API - weryfikacja (działanie obecne - testy regresji z AC, poprawka różnic); zależy od: -

## Encje do odczytu (02-domain/ENTITIES.md)
## Pojazd
Pola: nazwa, zużycie kWh/100 km, spalanie odpowiednika l/100 km, rodzaj paliwa, przebieg startowy (wymagany), okres posiadania (od-do), notatki
Stany: dodany, nieaktywny, usunięty
Przejscia: [*] -> dodany (Właściciel instalacji, tylko z przebiegiem startowym); dodany -> nieaktywny (Właściciel instalacji, D-025; dane dalej w oszczędnościach; bez pól EV w formularzu odczytu nowego miesiąca, D-028); dodany / nieaktywny -> usunięty (Właściciel instalacji, D-034; domyślnie dane miesięczne zostają i liczą się jak dane pojazdu nieaktywnego; skasowanie danych miesięcznych tylko po wyraźnym potwierdzeniu)
Zrodlo: [App] src/main.py create_vehicle (/ev/pojazdy/nowy), update_vehicle, delete_vehicle; [Biz] D-025, D-034
Zakwestionowane:
