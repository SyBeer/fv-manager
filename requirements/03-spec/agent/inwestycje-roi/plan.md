<!-- GENEROWANE z PRD.md 2026-10-04 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Plan - Inwestycje, ROI i prognoza

## Kolejność
1. R-005 Etapy inwestycji - weryfikacja (działanie obecne - testy regresji z AC, poprawka różnic); zależy od: -
2. R-006 Pozostało do zwrotu - błąd (stan docelowy - kod działa inaczej niż decyzja); zależy od: R-002 (T-02), R-005 (T-07), R-010 (T-12)
3. R-007 Prognoza zwrotu - zmiana (stan docelowy); zależy od: R-006 (T-08)
4. R-008 Ekran ROI i dashboard - weryfikacja (działanie obecne - testy regresji z AC, poprawka różnic); zależy od: R-006 (T-08), R-007 (T-09)

## Encje do odczytu (02-domain/ENTITIES.md)
## Etap inwestycji
Pola: data, opis, koszt brutto (zł), moc kWp (opcjonalna), notatki
Stany: zapisany, zmieniony, usunięty
Przejscia: [*] -> zapisany (Właściciel instalacji); zapisany -> zmieniony (Właściciel instalacji); zapisany/zmieniony -> usunięty (Właściciel instalacji)
Zrodlo: [Dok] README.md, investments, /inwestycje/nowa; [App] src/main.py update_investment, delete_investment
Zakwestionowane:
## Zwrot inwestycji
Pola: suma etapów inwestycji, suma oszczędności FV, suma oszczędności EV z FV, pozostało
Stany: w trakcie, zwrot osiągnięty (liczone przy każdym wyświetleniu, nie zapisywane)
Przejscia: w trakcie -> zwrot osiągnięty (gdy pozostało ≤ 0, automatycznie); zwrot osiągnięty -> w trakcie (gdy po nowym etapie inwestycji pozostało > 0)
Zrodlo: [App] src/services/calculations.py calc_roi, roi_achieved; [Dok] README.md, calc_roi
Zakwestionowane:
