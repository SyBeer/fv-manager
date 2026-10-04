<!-- GENEROWANE z PRD.md 2026-10-04 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Plan - Wycofanie Tesla Fleet API

## Kolejność
1. R-018 Wycofanie integracji z Tesla Fleet API - zmiana (stan docelowy); zależy od: -

## Encje do odczytu (02-domain/ENTITIES.md)
## Pojazd
Pola: nazwa, zużycie kWh/100 km, spalanie odpowiednika l/100 km, rodzaj paliwa, przebieg startowy (wymagany)
Stany: dodany
Przejscia: [*] -> dodany (Właściciel instalacji, tylko z przebiegiem startowym)
Zrodlo: [App] src/main.py create_vehicle (/ev/pojazdy/nowy)
Zakwestionowane:
