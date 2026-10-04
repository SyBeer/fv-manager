<!-- GENEROWANE z PRD.md 2026-10-04 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Inwestycje, ROI i prognoza

### R-005 Etapy inwestycji
Opis:              Właściciel instalacji dodaje, edytuje i usuwa etapy inwestycji (koszt, data, moc). Łączna inwestycja = suma kosztów etapów. Etap liczy się od miesiąca swojej daty (D-015); koszt może być zerowy, dodatni albo ujemny - ujemny to dofinansowanie (D-016, zmienia D-014); data etapu dowolna, także sprzed pierwszego odczytu (D-021).
Zrodlo:            [Dok] README.md, investments; [App] src/main.py /inwestycje/{id}/edytuj, /inwestycje/{id}/usun
Zalozenia:         -
Reguly:            BR-010
Status:            zatwierdzone (właściciel instalacji, 2026-10-04)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-005-1: Given brak etapów, When właściciel dodaje etap (koszt 30 000 zł, data 2022-06, moc 6 kWp), Then etap jest na liście, a łączna inwestycja = 30 000 zł.
- AC-005-2: Given dwa etapy (30 000 zł i 10 000 zł), When właściciel usuwa drugi, Then łączna inwestycja = 30 000 zł.
- AC-005-3: Given etap 30 000 zł, When właściciel zmienia koszt na 32 000 zł, Then łączna inwestycja = 32 000 zł.
- AC-005-4: Given formularz etapu z kosztem 0 zł, When właściciel zapisuje etap, Then etap jest na liście, a łączna inwestycja się nie zmienia.
- AC-005-5: Given etapy 30 000 zł i −5 000 zł (dofinansowanie), When liczona jest łączna inwestycja, Then łączna inwestycja = 25 000 zł.
- AC-005-6: Given etap serwisowy z kosztem 800 zł bez mocy, When liczona jest prognoza, Then prognoza się nie zmienia, a łączna inwestycja rośnie o 800 zł.

### R-006 Pozostało do zwrotu
Opis:              Aplikacja liczy, ile zostało do zwrotu inwestycji: łączna inwestycja − Σ oszczędności PV − Σ Oszczędność EV z FV. Oszczędność z ładowania publicznego nie wchodzi do ROI. Etap inwestycji liczy się od miesiąca swojej daty (D-015; dziś błąd - wszystkie etapy od początku). Etap sprzed pierwszego odczytu liczy się od pierwszego miesiąca z odczytem (D-021). Termin zwrotu = karta „mies. do ROI”: pozostało do zwrotu / średnia miesięczna oszczędność z historii (D-018).
Zrodlo:            [Biz] session-2026-10-04.md, Q-027; [Biz] board.json, qq006 (D-008); [Dok] README.md, calc_roi
Zalozenia:         A-007
Reguly:            BR-006, BR-010
Status:            zatwierdzone (właściciel instalacji, 2026-10-04)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-006-1: Given inwestycja 40 000 zł, Σ oszczędności PV 15 000 zł, Σ Oszczędność EV z FV 3 000 zł, ładowanie publiczne z oszczędnością 2 000 zł, When liczony jest ROI, Then pozostało do zwrotu = 22 000 zł.
- AC-006-2: Given Σ oszczędności ≥ łączna inwestycja, When liczony jest ROI, Then Zwrot inwestycji ma stan „zwrot osiągnięty”.
- AC-006-3: Given etapy 30 000 zł (2022-06) i 10 000 zł (2025-03), When wykres /roi pokazuje 2024-12, Then inwestycja = 30 000 zł; dla 2025-03 inwestycja = 40 000 zł.
- AC-006-4: Given pozostało do zwrotu 22 000 zł i średnia miesięczna oszczędność 500 zł, When właściciel otwiera /roi, Then karta „mies. do ROI” pokazuje 44 mies.
- AC-006-5: Given etap z datą 2021-09 i pierwszy odczyt za 2021.10, When wykres /roi pokazuje 2021.10, Then inwestycja obejmuje ten etap.

### R-007 Prognoza zwrotu
Opis:              Aplikacja prognozuje 36 miesięcy z degradacją paneli (ustawienie, domyślnie 0,6% rocznie) i scenariuszami wzrostu ceny prądu kupowanego z sieci 0/3/7/12% rocznie. Gdy zwrot przypada po 36 miesiącach, wykres kończy się na 36. miesiącu, a tabela scenariuszy podaje „zwrot za N mies.” dla każdego scenariusza (D-013, D-019; stan docelowy).
Zrodlo:            [App] src/main.py:995-1008, src/services/forecast.py; [App] src/main.py:1888; [Biz] session-2026-10-04.md, Q-028 (D-013)
Zalozenia:         A-008 (niepotwierdzone; Q-028 zaparkowane)
Reguly:            BR-007
Status:            zatwierdzone (właściciel instalacji, 2026-10-04)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-007-1: Given degradacja 0,6% rocznie, instalacja 2022.06, bazowa produkcja czerwca 500 kWh, When prognozowany jest czerwiec 2026, Then prognozowana produkcja = 488,1 kWh (zaokrąglenie do 0,1 kWh).
- AC-007-2: Given ustawienia bez wpisanej degradacji, When właściciel otwiera ustawienia, Then pole degradacji pokazuje 0,6.
- AC-007-3: Given zwrot przypada po 36 miesiącach, When właściciel otwiera /roi, Then wykres kończy się na 36. miesiącu, a tabela scenariuszy pokazuje dla każdego scenariusza „zwrot za N mies.” z N > 36.

### R-008 Ekran ROI i dashboard
Opis:              Ekran /roi pokazuje karty ROI, wykres skumulowanych oszczędności na tle inwestycji, tabelę wrażliwości (7 stałych cen, D-012) i prognozę (R-007). Dashboard pokazuje baner ROI i 12 ostatnich miesięcy.
Zrodlo:            [Dok] README.md, ROI (/roi), Dashboard (/); [Biz] board.json, qq004 (D-012)
Zalozenia:         A-011
Reguly:            BR-006, BR-007
Status:            zatwierdzone (właściciel instalacji, 2026-10-04)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-008-1: Given co najmniej jeden odczyt i jeden etap inwestycji, When właściciel otwiera /roi, Then widzi karty: łączna inwestycja, łączne oszczędności, pozostało do zwrotu i mies. do ROI, z wartościami wyliczonymi z danych testowych, oraz wykres skumulowanych oszczędności na tle inwestycji i tabelę wrażliwości z 7 cenami (0,50; 0,60; 0,70; 0,80; 0,90; 1,00; 1,20 zł/kWh).
- AC-008-2: Given 15 odczytów, When właściciel otwiera dashboard, Then widzi baner ROI i 12 ostatnich miesięcy.
- AC-008-3: Given zwrot przypada po 48 miesiącach, When właściciel otwiera dashboard, Then widzi „Do zwrotu inwestycji 48 mies.”.
