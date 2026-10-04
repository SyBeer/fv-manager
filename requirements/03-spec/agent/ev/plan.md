<!-- GENEROWANE z PRD.md 2026-10-04 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Plan - Pojazdy EV i ceny paliwa

## Kolejność
1. R-009 Dodanie pojazdu - zmiana (stan docelowy); zależy od: -
2. R-010 Oszczędności EV - błąd (stan docelowy - kod działa inaczej niż decyzja); zależy od: R-009 (T-11)
3. R-011 Śledzenie cen paliwa - weryfikacja (działanie obecne - testy regresji z AC, poprawka różnic); zależy od: R-009 (T-11)

## Encje do odczytu (02-domain/ENTITIES.md)
## Pojazd
Pola: nazwa, zużycie kWh/100 km, spalanie odpowiednika l/100 km, rodzaj paliwa, przebieg startowy (wymagany), okres posiadania (od-do), notatki
Stany: dodany, nieaktywny
Przejscia: [*] -> dodany (Właściciel instalacji, tylko z przebiegiem startowym); dodany -> nieaktywny (Właściciel instalacji, D-025; dane dalej w oszczędnościach; bez pól EV w formularzu odczytu nowego miesiąca, D-028)
Zrodlo: [App] src/main.py create_vehicle (/ev/pojazdy/nowy), update_vehicle; [Biz] D-025
Zakwestionowane:
## Cena paliwa
Pola: data, cena, typ paliwa, źródło
Stany: zapisana
Przejscia: [*] -> zapisana (Właściciel instalacji, wpis ręczny, D-006)
Zrodlo: [App] kod-v3.2.4-2026-09-27.md, Ceny paliwa; [Biz] D-006; obowiązuje od daty wpisu do następnego wpisu (D-023)
Zakwestionowane:
