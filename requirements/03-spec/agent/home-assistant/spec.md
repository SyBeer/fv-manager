<!-- GENEROWANE z PRD.md 2026-10-04 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Integracja z Home Assistant

### R-015 Integracja z Home Assistant
Opis:              Właściciel instalacji wpisuje encje HA (produkcja PV, pobór z sieci, oddanie do sieci) i testuje połączenie. HA odczytuje podsumowanie ROI z /api/summary, liczone tak samo jak na /roi.
Zrodlo:            [Dok] README.md, Home Assistant, /api/ha-test, API JSON; [Biz] session-2026-10-04.md, Q-030
Zalozenia:         A-010, A-013
Reguly:            BR-009
Status:            zatwierdzone (właściciel instalacji, 2026-10-04)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-015-1: Given wpisane encje produkcji, poboru i oddania, When właściciel klika „Testuj połączenie”, Then widzi wynik testu (sukces albo błąd).
- AC-015-2: Given dane ROI, When HA odpytuje /api/summary, Then „pozostało do zwrotu” jest równe wartości na /roi.
