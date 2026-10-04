<!-- GENEROWANE z PRD.md 2026-10-04 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Pojazdy EV i ceny paliwa

### R-009 Dodanie pojazdu
Opis:              Właściciel instalacji dodaje pojazd: nazwa, zużycie kWh/100 km, spalanie odpowiednika l/100 km, rodzaj paliwa, przebieg startowy. Bez przebiegu startowego pojazd nie zostaje dodany. Przebieg startowy można później zmienić: aplikacja pyta, czy przesunąć zapisane stany licznika o różnicę (D-027).
Zrodlo:            [App] src/main.py:1562, 1573; [Biz] session-2026-10-04.md, Q-029, D-027
Zalozenia:         A-009
Reguly:            BR-008, BR-012
Status:            zatwierdzone (właściciel instalacji, 2026-10-04)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-009-1: Given formularz z nazwą, zużyciem 18 kWh/100 km, spalaniem odpowiednika 7 l/100 km, benzyną i przebiegiem startowym 12 000 km, When właściciel dodaje pojazd, Then pojazd jest na liście /ev.
- AC-009-2: Given formularz bez przebiegu startowego, When właściciel dodaje pojazd, Then pojazd nie zostaje dodany.
- AC-009-3: Given pojazd z przebiegiem startowym 12 000 km i stanami licznika 13 000 (2026.01) i 14 200 (2026.02), When właściciel zmienia przebieg startowy na 12 500 km i wybiera przesunięcie stanów licznika („Tak”), Then stany licznika wynoszą 13 500 i 14 700, a km za te miesiące nadal 1 000 i 1 200.
- AC-009-4: Given te same dane, When właściciel zmienia przebieg startowy na 13 500 km i wybiera „Nie”, Then stan licznika 13 000 za 2026.01 zostaje usunięty (kWh ładowania z 2026.01 zostają), a km za 2026.02 = 14 200 − 13 500 = 700.

### R-010 Oszczędności EV
Opis:              Aplikacja liczy oszczędność EV miesiąca jako koszt paliwa odpowiednika (km / 100 × spalanie × cena paliwa) minus koszt energii ładowania. Oszczędność EV z FV (ładowanie domowe) wchodzi do ROI; Oszczędność EV vs paliwo (domowe + publiczne) jest na kartach /ev i nie wchodzi do ROI.
Zrodlo:            [App] src/services/calculations.py:275, calc_ev_savings; [Dok] README.md, EV (/ev); [Biz] board.json, qq006 (D-008); [Biz] board.json, qq038, qq039 (D-023)
Zalozenia:         -
Reguly:            BR-011
Status:            zatwierdzone (właściciel instalacji, 2026-10-04)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-010-1: Given w miesiącu 1 000 km, spalanie odpowiednika 7 l/100 km, paliwo 6,00 zł/l, ładowanie domowe 180 kWh, cena prądu 1,00 zł/kWh, When liczona jest oszczędność, Then Oszczędność EV z FV = 420 − 180 = 240 zł.
- AC-010-2: Given w tym samym miesiącu także ładowanie publiczne, When właściciel otwiera /ev, Then karty pokazują Oszczędność EV vs paliwo (domowe + publiczne), a do ROI (R-006) trafia tylko Oszczędność EV z FV.
- AC-010-3: Given pojazd na PB95 i ceny PB95 6,00 zł (2026-03-10) i 6,50 zł (2026-05-20) oraz cena ON 7,00 zł (2026-04-05), When liczona jest oszczędność za 2026.03, 2026.04 i 2026.05, Then marzec i kwiecień liczą się po 6,00 zł, maj po 6,50 zł - tak samo na kartach /ev i w ROI (D-023).

### R-011 Śledzenie cen paliwa
Opis:              Przy dodawaniu pierwszego samochodu właściciel instalacji decyduje, czy śledzi ceny paliwa. Jeśli tak - w menu pod EV jest pozycja „Ceny paliwa” (wpis ręczny: data, cena, typ, źródło); jeśli nie - pozycji nie ma. Stan docelowy.
Zrodlo:            [Biz] board.json, nmuspw64n (D-007); [Biz] board.json, qq005 (D-006); [Biz] board.json, qq040 (D-024)
Zalozenia:         -
Reguly:            -
Status:            zatwierdzone (właściciel instalacji, 2026-10-04)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-011-1: Given brak pojazdów, When właściciel dodaje pierwszy samochód, Then formularz pyta, czy śledzić ceny paliwa.
- AC-011-2: Given śledzenie włączone, When właściciel otwiera menu, Then pod EV jest pozycja „Ceny paliwa”, w której wpisuje datę, cenę, typ i źródło.
- AC-011-3: Given śledzenie wyłączone, When właściciel otwiera menu, Then pozycji „Ceny paliwa” nie ma.
- AC-011-4: Given dodany samochód i śledzenie wyłączone, When właściciel włącza śledzenie na /ev, Then w menu pod EV pojawia się „Ceny paliwa”; wyłączenie ją ukrywa (D-024).
