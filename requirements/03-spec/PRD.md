# PRD - FV Manager

## 1. Cel
Właściciel instalacji raz w miesiącu wpisuje odczyty za miniony miesiąc i sprawdza, ile instalacja już się zwróciła i ile oszczędza na samochodach. Efekt: zawsze aktualny ROI i oszczędności bez ręcznych obliczeń.
Źródło: [Biz] QUESTIONS.md, Q-015; A-003 (potwierdzone, session-2026-10-07.md).

## 2. Aktorzy
Właściciel instalacji - zob. 02-domain/ACTORS.md.

## 3. Zakres
- Miesięczny odczyt (ręcznie, z HA, import CSV).
- Rozliczenie miesiąca: net-metering i net-billing.
- Inwestycje i ROI (z prognozą).
- Pojazdy EV i ceny paliwa.
- Ustawienia rozliczeń.
- Import, eksport, kopia danych.
- Integracja z Home Assistant.

## 4. Poza zakresem
(rownie wazne jak zakres)
- Strony /bateria i /ogrzewanie - makiety przyszłych funkcji (D-011).
- Uwierzytelnianie ponad istniejący opcjonalny Basic Auth (FV_AUTH_PASSWORD), dopóki tryb standalone nie jest wystawiony poza sieć domową (A-002, potwierdzone, session-2026-10-07.md).
- Automatyczne pobieranie cen RCE i cen paliwa - wpisywane ręcznie (D-004, D-006).
- Wariant procentowy w analizie wrażliwości - 7 stałych cen (D-012).
- Integracja z Tesla Fleet API - wycofana, API nie działało dobrze (D-020).
- Osobna kategoria kosztów eksploatacji - wszystkie wydatki na instalację to etapy inwestycji (D-017).
- Podsumowanie ROI dla Home Assistant (/api/summary) - usuwane, właściciel nie korzysta (D-030).
- Zestawianie kwoty faktury z policzoną oszczędnością - numer i kwota faktury służą tylko do odnalezienia faktury (D-033).

## 5. Wymagania

### R-001 Wpisanie odczytu miesiąca
Opis:              Właściciel instalacji wpisuje odczyt miesiąca (produkcja, oddane, pobrane, cena kWh, faktura, dane EV per pojazd) ręcznie albo pobiera produkcję i dane sieci z Home Assistant za wybrany miesiąc. Błędny odczyt nie zostaje zapisany. Integracja z Tesla Fleet API wycofana (D-020, R-018). Cenę kWh właściciel wpisuje z faktury na nowy okres; puste pole = cena domyślna kWh z konfiguracji add-onu (D-031, BR-014). Numer i kwota brutto faktury służą do odnalezienia faktury i nie wchodzą do obliczeń (D-033). Przejechane km właściciel przepisuje z aplikacji Tesla (S-007), kWh ładowania domowego - z domowych liczników energii (S-009), kWh i koszt ładowania publicznego - z aplikacji operatora ładowarki (S-008); brakujące dane ładowania publicznego uzupełnia później edycją odczytu.
Zrodlo:            [App] kod-v3.2.4-2026-09-27.md, Walidacja odczytów; [Biz] session-2026-10-04.md, Q-024, Q-030; [Biz] board.json, qq042 (D-026); [Biz] session-2026-10-07.md, Q-047, Q-049, Q-052, Q-053; [Biz] session-2026-10-08.md, Q-056, Q-057
Zalozenia:         A-004, A-010
Reguly:            BR-003, BR-009, BR-011, BR-014
Status:            zatwierdzone (właściciel instalacji, 2026-10-08)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-001-1: Given poprawne dane za 2026.09 (produkcja ≥ oddane, wszystkie wartości ≥ 0), When właściciel zapisuje odczyt, Then odczyt jest na liście odczytów.
- AC-001-2: Given okres „2026-9”, When właściciel zapisuje odczyt, Then odczyt nie zostaje zapisany, a formularz pokazuje błąd okresu.
- AC-001-3: Given oddane 500 kWh i produkcja 400 kWh, When właściciel zapisuje odczyt, Then odczyt nie zostaje zapisany, a formularz pokazuje błąd.
- AC-001-4: Given skonfigurowane encje HA, When właściciel wybiera miesiąc i klika „pobierz z HA”, Then pola produkcja, oddane i pobrane wypełniają się bez ręcznego wpisywania.
- AC-001-5: Given pojazd z przebiegiem startowym 12 000 km, When właściciel wpisuje stan licznika 13 000 za pierwszy miesiąc i 14 200 za kolejny, Then km miesięcy wynoszą 1 000 i 1 200 (BR-011).
- AC-001-6: Given zapisany odczyt z numerem faktury i kwotą brutto 350 zł, When właściciel zmienia kwotę faktury na 400 zł, Then oszczędność PV miesiąca i pozostało do zwrotu się nie zmieniają (D-033).

### R-002 Oszczędność PV miesiąca
Opis:              Dla każdego odczytu aplikacja liczy oszczędność PV miesiąca (kWh i zł) według modelu rozliczeń okresu rozliczeniowego: w net-meteringu z autokonsumpcji i puli net-meteringu (kumulowanej w cyklu rozliczeniowym), w net-billingu z autokonsumpcji i energii oddanej wycenionej po cenie RCE.
Zrodlo:            [App] kod-v3.2.4-2026-09-27.md, Rozliczenie net-metering, calculations.py:94-159; [Biz] board.json, qq001 (D-002); [Biz] session-2026-10-04.md, Q-025; [Biz] session-2026-10-07.md, Q-047, Q-048
Zalozenia:         A-005, A-006 (niepotwierdzone; Q-026 zaparkowane)
Reguly:            BR-001, BR-004, BR-005, BR-013, BR-014
Status:            zatwierdzone (właściciel instalacji, 2026-10-08)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-002-1: Given okres w net-meteringu, współczynnik 0,80, pula 0, produkcja 500, oddane 300, pobrane 200 kWh, When liczona jest oszczędność, Then autokonsumpcja = 200 kWh, do puli wpada 240 kWh, z puli zużyte 200 kWh, na kolejny miesiąc przechodzi 40 kWh.
- AC-002-2: Given miesiąc startu cyklu = kwiecień i pula 40 kWh z marca, When liczony jest kwiecień, Then pula startuje od 0.
- AC-002-3: Given okres w net-billingu, autokonsumpcja 200 kWh, cena zakupu 1,00 zł, oddane 300 kWh, RCE 0,40 zł, When liczona jest oszczędność, Then oszczędność = 320 zł.
- AC-002-4: Given net-billing i odczyt z ceną sprzedaży 0,50 zł, When liczona jest oszczędność, Then energia oddana jest wyceniona po 0,50 zł zamiast po RCE.
- AC-002-5: Given okres w net-meteringu, pula 0, produkcja 200 kWh, oddane 0, odczyt bez ceny kWh i cena domyślna kWh 0,75 zł w konfiguracji, When liczona jest oszczędność, Then oszczędność PV miesiąca = 200 × 0,75 = 150 zł (BR-014).

### R-003 Ustawienie miesiąca startu cyklu rozliczeniowego
Opis:              Właściciel instalacji ustawia miesiąc startu cyklu rozliczeniowego (domyślnie kwiecień); w tym miesiącu pula net-meteringu się zeruje. Działa od v3.3.0 (src/main.py:2028).
Zrodlo:            [Biz] board.json, qq012 (D-003)
Zalozenia:         -
Reguly:            BR-001
Status:            zatwierdzone (właściciel instalacji, 2026-10-04)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-003-1: Given brak ustawienia, When liczone są oszczędności, Then cykl rozliczeniowy startuje w kwietniu.
- AC-003-2: Given właściciel ustawił czerwiec, When liczony jest czerwiec, Then pula net-meteringu zeruje się w czerwcu, a nie w kwietniu.

### R-004 Import odczytów z CSV - cały plik albo nic
Opis:              Właściciel instalacji importuje odczyty z pliku CSV (separator „;”, polskie nagłówki). Jeśli choć jeden wiersz jest błędny, nie zostaje zapisany żaden, a raport podaje numer wiersza i powód (działa w v3.4.0, src/main.py:1191). Okres, który już istnieje, import pomija - Q-017 (zaparkowane).
Zrodlo:            [Biz] board.json, qq008 (D-009)
Zalozenia:         -
Reguly:            BR-002
Rodzaj:            kontrakt - wejscie
System:            S-006 (Plik CSV)
Status:            zatwierdzone (właściciel instalacji, 2026-10-04)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-004-1: Given plik z 10 poprawnymi wierszami, When właściciel importuje plik, Then zapisanych zostaje 10 odczytów.
- AC-004-2: Given plik, w którym wiersz 4 ma wartość ujemną, When właściciel importuje plik, Then nie zostaje zapisany żaden wiersz, a raport pokazuje „wiersz 4” i powód.

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
Opis:              Aplikacja liczy, ile zostało do zwrotu inwestycji: łączna inwestycja − Σ oszczędności PV − Σ Oszczędność EV z FV. Oszczędność z ładowania publicznego nie wchodzi do ROI. Etap inwestycji liczy się od miesiąca swojej daty (D-015). Etap sprzed pierwszego odczytu liczy się od pierwszego miesiąca z odczytem (D-021). Termin zwrotu = karta „mies. do ROI”: pozostało do zwrotu / średnia miesięczna oszczędność z historii (D-018).
Zrodlo:            [Biz] session-2026-10-04.md, Q-027; [Biz] board.json, qq006 (D-008); [Dok] README.md, calc_roi
Zalozenia:         A-007
Reguly:            BR-006, BR-010, BR-014
Status:            zatwierdzone (właściciel instalacji, 2026-10-08)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-006-1: Given inwestycja 40 000 zł, Σ oszczędności PV 15 000 zł, Σ Oszczędność EV z FV 3 000 zł, ładowanie publiczne z oszczędnością 2 000 zł, When liczony jest ROI, Then pozostało do zwrotu = 22 000 zł.
- AC-006-2: Given Σ oszczędności ≥ łączna inwestycja, When liczony jest ROI, Then Zwrot inwestycji ma stan „zwrot osiągnięty”.
- AC-006-3: Given etapy 30 000 zł (2022-06) i 10 000 zł (2025-03), When wykres /roi pokazuje 2024-12, Then inwestycja = 30 000 zł; dla 2025-03 inwestycja = 40 000 zł.
- AC-006-4: Given pozostało do zwrotu 22 000 zł i średnia miesięczna oszczędność 500 zł, When właściciel otwiera /roi, Then karta „mies. do ROI” pokazuje 44 mies.
- AC-006-5: Given etap z datą 2021-09 i pierwszy odczyt za 2021.10, When wykres /roi pokazuje 2021.10, Then inwestycja obejmuje ten etap.

### R-007 Prognoza zwrotu
Opis:              Aplikacja prognozuje 36 miesięcy z degradacją paneli (ustawienie, domyślnie 0,6% rocznie) i scenariuszami wzrostu ceny prądu kupowanego z sieci 0/3/7/12% rocznie. Gdy zwrot przypada po 36 miesiącach, wykres kończy się na 36. miesiącu, a tabela scenariuszy podaje „zwrot za N mies.” dla każdego scenariusza (D-013, D-019; działa w v3.4.0, templates/roi.html:179).
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
Zrodlo:            [App] src/services/calculations.py:275, calc_ev_savings; [Dok] README.md, EV (/ev); [Biz] board.json, qq006 (D-008); [Biz] board.json, qq038, qq039 (D-023); [Biz] session-2026-10-04.md, Q-044 (D-029)
Zalozenia:         -
Reguly:            BR-011
Status:            zatwierdzone (właściciel instalacji, 2026-10-04)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-010-1: Given w miesiącu 1 000 km, spalanie odpowiednika 7 l/100 km, paliwo 6,00 zł/l, ładowanie domowe 180 kWh, cena prądu 1,00 zł/kWh, When liczona jest oszczędność, Then Oszczędność EV z FV = 420 − 180 = 240 zł.
- AC-010-2: Given w tym samym miesiącu także ładowanie publiczne, When właściciel otwiera /ev, Then karty pokazują Oszczędność EV vs paliwo (domowe + publiczne), a do ROI (R-006) trafia tylko Oszczędność EV z FV.
- AC-010-3: Given pojazd na PB95 i ceny PB95 6,00 zł (2026-03-10) i 6,50 zł (2026-05-20) oraz cena ON 7,00 zł (2026-04-05), When liczona jest oszczędność za 2026.03, 2026.04 i 2026.05, Then marzec i kwiecień liczą się po 6,00 zł, maj po 6,50 zł - tak samo na kartach /ev i w ROI (D-023).
- AC-010-4: Given pojazd na PB95 z danymi EV od 2025.11, pierwsza cena PB95 6,00 zł wpisana 2026-02-10 i druga 6,50 zł wpisana 2026-05-20, When liczona jest oszczędność za 2025.11-2026.05, Then miesiące 2025.11-2026.04 liczą się po 6,00 zł, a 2026.05 po 6,50 zł - tak samo na kartach /ev i w ROI (D-029).

### R-011 Śledzenie cen paliwa
Opis:              Przy dodawaniu pierwszego samochodu właściciel instalacji decyduje, czy śledzi ceny paliwa. Jeśli tak - w menu pod EV jest pozycja „Ceny paliwa” (wpis ręczny: data, cena, typ, źródło); jeśli nie - pozycji nie ma.
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

### R-012 Lista i edycja odczytów
Opis:              Lista odczytów pokazuje dla każdego miesiąca produkcję, autokonsumpcję, oddane, pobrane, zużycie i oszczędność. Przy edycji odczytu właściciel instalacji widzi ROI przed i po zmianie.
Zrodlo:            [Dok] README.md, Odczyty (/odczyty), /api/roi-preview
Zalozenia:         A-012
Reguly:            -
Status:            zatwierdzone (właściciel instalacji, 2026-10-04)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-012-1: Given 3 zapisane odczyty, When właściciel otwiera /odczyty, Then każdy wiersz pokazuje produkcję, autokonsumpcję, oddane, pobrane, zużycie i oszczędność.
- AC-012-2: Given zapisany odczyt, When właściciel zmienia produkcję w formularzu edycji, Then przed zapisem widzi ROI przed i po zmianie.

### R-013 Eksport i kopia danych
Opis:              Właściciel instalacji eksportuje odczyty do CSV, pobiera pełną kopię danych (JSON) i przywraca dane z kopii. Przywrócenie nadpisuje dane, ustawienia zostają.
Zrodlo:            [Dok] README.md, /odczyty/export.csv; [App] src/main.py:1161; [App] kod-v3.2.4-2026-09-27.md, Czyszczenie bazy
Zalozenia:         -
Reguly:            -
Rodzaj:            kontrakt - wyjscie
System:            S-006 (Plik CSV)
Status:            zatwierdzone (właściciel instalacji, 2026-10-04)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-013-1: Given 12 odczytów, When właściciel eksportuje odczyty do CSV, Then plik ma 12 wierszy danych.
- AC-013-2: Given dane w aplikacji, When właściciel pobiera pełną kopię, Then dostaje plik JSON.
- AC-013-3: Given kopia JSON z 5 odczytami, aplikacja z 12 odczytami i degradacja ustawiona na 0,8, When właściciel przywraca dane z kopii, Then aplikacja ma 5 odczytów, a degradacja nadal wynosi 0,8.

### R-014 Wyczyść bazę
Opis:              „Wyczyść bazę” usuwa wszystkie dane (odczyty, etapy inwestycji, pojazdy i dane EV, ceny paliwa, okresy rozliczeniowe, ceny RCE); ustawienia zostają. Tekst przed potwierdzeniem wymienia wszystko, co znika, i zaleca kopię (działa w v3.4.0, src/main.py:1230).
Zrodlo:            [Biz] board.json, qq010 (D-010)
Zalozenia:         -
Reguly:            -
Status:            zatwierdzone (właściciel instalacji, 2026-10-04)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-014-1: Given odczyty, etapy inwestycji, pojazdy, ceny paliwa, okresy rozliczeniowe i ceny RCE, When właściciel potwierdza „Wyczyść bazę”, Then wszystkie te dane znikają, a ustawienia zostają.
- AC-014-2: Given ekran przed potwierdzeniem, When właściciel go czyta, Then tekst wymienia wszystkie usuwane rodzaje danych i zaleca pobranie kopii (/backup/full).

### R-015 Integracja z Home Assistant
Opis:              Właściciel instalacji wpisuje encje HA (produkcja PV, pobór z sieci, oddanie do sieci) i testuje połączenie. Podsumowanie ROI dla HA (/api/summary) jest usuwane - właściciel z niego nie korzysta (D-030).
Zrodlo:            [Dok] README.md, Home Assistant, /api/ha-test, API JSON; [Biz] session-2026-10-04.md, Q-030; [Biz] session-2026-10-05.md, propozycja C (D-030)
Zalozenia:         A-010, A-013
Reguly:            BR-009
Status:            zatwierdzone (właściciel instalacji, 2026-10-08)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-015-1: Given wpisane encje produkcji, poboru i oddania, When właściciel klika „Testuj połączenie”, Then widzi „OK — RRRR-MM: N kWh (okres: RRRR-MM)” dla bieżącego miesiąca albo komunikat błędu.
- AC-015-2: Given aplikacja po zmianie, When HA odpytuje /api/summary, Then aplikacja odpowiada „nie znaleziono” (404), a test połączenia i pobieranie liczników działają bez zmian (D-030).

### R-016 Poprawki tekstów
Opis:              Teksty metodologia.html, README i podtytuł tabeli wrażliwości na /roi zgodne z decyzjami: pula kumulowana w cyklu, RCE i ceny paliwa wpisywane ręcznie, bez dat ustawowych net-billingu (model z okresów rozliczeniowych, daty z umowy - D-022), 7 stałych cen, CSV z separatorem „;” i polskimi nagłówkami.
Zrodlo:            [Biz] board.json, qq001, qq002, qq003, qq004, qq005, qq008 (D-002, D-004, D-005, D-006, D-012, D-009); [Biz] session-2026-10-04.md, Q-037 (D-022)
Zalozenia:         -
Reguly:            -
Status:            zatwierdzone (właściciel instalacji, 2026-10-04)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-016-1: Given metodologia.html, When właściciel czyta opis cen RCE i cen paliwa, Then tekst mówi, że wpisuje się je ręcznie.
- AC-016-2: Given metodologia.html i README, When właściciel czyta opis puli, Then tekst mówi, że pula przechodzi z miesiąca na miesiąc i zeruje się w miesiącu startu cyklu.
- AC-016-3: Given /roi i metodologia.html, When właściciel czyta opis analizy wrażliwości, Then podtytuł na /roi pokazuje współczynnik z ustawień zamiast „×0.8”, a metodologia opisuje 7 stałych cen zamiast „wzrost o 20%”.
- AC-016-4: Given README, When właściciel czyta przykład CSV, Then przykład ma separator „;” i polskie nagłówki.
- AC-016-5: Given metodologia.html, When właściciel czyta opis net-billingu, Then tekst nie podaje dat ustawowych i mówi, że model rozliczeń wynika z okresów rozliczeniowych ustawionych przez użytkownika, a daty zależą od umowy z operatorem.

### R-017 Okresy rozliczeniowe i ceny RCE
Opis:              Właściciel instalacji na /pv ustawia okresy rozliczeniowe (data startu, opcjonalnie data końca, model: net-metering albo net-billing) i wpisuje ceny RCE (data, cena, źródło); może je usuwać. Model rozliczeń miesiąca wynika z okresu rozliczeniowego obowiązującego 1. dnia tego miesiąca (D-032); bez okresu obowiązuje net-metering. Brak ceny RCE w miesiącu net-billingu - Q-033, Q-051 (zaparkowane); nakładające się okresy - Q-055 (zaparkowane, dziś wygrywa późniejszy start).
Zrodlo:            [Biz] board.json, qq002 (D-004); [App] src/main.py:1838-1900; [App] src/services/calculations.py:57-91; [Biz] session-2026-10-07.md, Q-048 (D-032)
Zalozenia:         -
Reguly:            BR-005, BR-013
Status:            zatwierdzone (właściciel instalacji, 2026-10-08)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-017-1: Given brak okresów rozliczeniowych, When liczony jest miesiąc 2023.05, Then miesiąc jest rozliczany w net-meteringu.
- AC-017-2: Given okres net-billing od 2024-07-01 bez daty końca, When liczone są 2024.06 i 2024.08, Then 2024.06 jest w net-meteringu, a 2024.08 w net-billingu.
- AC-017-3: Given ceny RCE 0,40 zł od 2024-07-01 i 0,30 zł od 2024-08-15, When liczony jest 2024.08 w net-billingu, Then energia oddana jest wyceniona po 0,30 zł (ostatnia cena z datą nie późniejszą niż koniec miesiąca).
- AC-017-4: Given usunięta cena RCE 0,30 zł, When ponownie liczony jest 2024.08, Then energia oddana jest wyceniona po 0,40 zł.
- AC-017-5: Given okres net-billing od 2024-07-15 bez daty końca, When liczone są 2024.07 i 2024.08, Then 2024.07 jest w net-meteringu, a 2024.08 w net-billingu (BR-013).

### R-018 Wycofanie integracji z Tesla Fleet API
Opis:              Integracja z Tesla Fleet API zostaje wycofana: pozostałości (kolumny tesla_* w bazie, wzmianki w ev.html, opis w README) są usuwane, a CHANGELOG aplikacji opisuje wycofanie i powód. Dane właściciela zostają nienaruszone.
Zrodlo:            [Biz] board.json, h01 (D-020); [App] src/utils/db.py:200, templates/ev.html; [Dok] README.md, Tesla Fleet API
Zalozenia:         -
Reguly:            -
Status:            zatwierdzone (właściciel instalacji, 2026-10-04)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-018-1: Given kod aplikacji, When ktoś szuka „tesla” w src/ i templates/, Then nie ma odwołań poza migracją usuwającą kolumny.
- AC-018-2: Given README i CHANGELOG, When właściciel czyta opis integracji, Then nie ma w nim Tesla Fleet API, a CHANGELOG opisuje wycofanie i jego powód.
- AC-018-3: Given baza z wypełnionymi polami Tesli, When aplikacja się uruchamia, Then odczyty, pojazdy i pozostałe dane właściciela zostają nienaruszone.

### R-019 Pojazd nieaktywny
Opis:              Właściciel instalacji oznacza pojazd jako nieaktywny (np. po sprzedaży albo wymianie auta). Dane pojazdu nieaktywnego dalej wchodzą do oszczędności EV i ROI. Pojazd nieaktywny nie ma pól EV w formularzu odczytu nowego miesiąca; jego zapisane dane są widoczne i edytowalne. Pojazd aktywny, który w miesiącu stał, ma puste pola (D-028).
Zrodlo:            [Biz] board.json, qq041 (D-025); [Biz] board.json, qq045 (D-028)
Zalozenia:         -
Reguly:            -
Status:            zatwierdzone (właściciel instalacji, 2026-10-04)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-019-1: Given pojazd z odczytami EV za 2025.01-2025.12, When właściciel oznacza go jako nieaktywny, Then Oszczędność EV z FV z tych miesięcy dalej wchodzi do ROI (R-006), a karty /ev dalej liczą jego oszczędność.
- AC-019-2: Given pojazdy A (aktywny) i B (nieaktywny), When właściciel otwiera formularz odczytu 2026.10, Then widzi pola EV tylko dla A, a odczyt z pustymi polami EV pojazdu A zapisuje się.
- AC-019-3: Given pojazd B (nieaktywny) z danymi EV za 2025.06, When właściciel edytuje odczyt 2025.06, Then pola EV pojazdu B są widoczne z zapisanymi wartościami.

### R-020 Kontrakt: liczniki energii z Home Assistant (wejście)
Opis:              Aplikacja przyjmuje z Home Assistant wartości miesiąca dla Odczytu miesiąca: produkcję PV, pobór z sieci i oddanie do sieci, w kWh. Pobranie na żądanie właściciela przy wpisie odczytu za wybrany miesiąc. Gdy HA nie ma danych, właściciel wpisuje wartości ręcznie. Schemat techniczny (encje, API HA) - w budowie, BR-009.
Zrodlo:            [Biz] session-2026-10-04.md, Q-030 (A-010); [Biz] session-2026-10-05.md, propozycja A; [App] src/main.py:2155-2190
Zalozenia:         A-010, A-015, A-016 (potwierdzone)
Reguly:            BR-009
Rodzaj:            kontrakt - wejscie
System:            S-002 (Home Assistant)
Status:            zatwierdzone (właściciel instalacji, 2026-10-08)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-020-1: Given encje produkcji, poboru i oddania są skonfigurowane, a HA ma dane za miesiąc 2026.09, When właściciel w formularzu odczytu za 2026.09 pobiera dane z HA, Then pola produkcja, pobrane i oddane mają wartości za 2026.09 w kWh i przed zapisem można je zmienić.
- AC-020-2: Given zapisany odczyt za 2026.08 i zmienione później dane za 2026.08 w HA, When właściciel otwiera listę odczytów, Then wartości odczytu 2026.08 są takie jak przy zapisie (pobranie tylko na żądanie przy wpisie odczytu).
- AC-020-3: Given HA nie zwraca danych za 2026.09, When właściciel pobiera dane z HA, Then widzi komunikat „Brak danych dla <encja> za 2026-09”, pola zostają puste do wpisania ręcznie, a odczyt z ręcznymi wartościami da się zapisać.

## 5a. Kandydaci na wymagania (robocze, bez numerów R)
Z warsztatu 2026-10-03. Numer R nadaje /sdd:spec po zgodzie właściciela.
- K-1 Ustawienie miesiąca startu cyklu rozliczeniowego (domyślnie kwiecień) - D-003, BR-001 → R-003.
- K-2 Przy dodawaniu pierwszego samochodu pytanie: czy śledzić ceny paliwa - D-007 → R-011.
- K-3 Pozycja menu „Ceny paliwa” pod EV, widoczna tylko gdy śledzenie włączone - D-007 → R-011.
- K-4 Import CSV: cały plik albo nic, raport błędnych wierszy (numer, powód) - D-009, BR-002; tablica: p36 → R-004.
- K-5 „Wyczyść bazę”: tekst wymienia wszystkie usuwane dane + zalecenie kopii /backup/full - D-010 → R-014.
- K-6 Poprawki tekstów: metodologia.html (pula, RCE i ceny paliwa wpisywane ręcznie, daty net-billingu, analiza wrażliwości), podtytuł tabeli na /roi z faktycznym współczynnikiem zamiast „×0.8” - D-002, D-004, D-005, D-006, D-012 → R-016.
- K-7 Poprawki README: logika puli (D-002), przykład CSV z separatorem „;” i polskimi nagłówkami (D-009) → R-016.
- K-8 Prognoza ROI: wykres 36 mies.; gdy zwrot później - liczba miesięcy do zwrotu słownie (np. „zwrot za 53 mies.”) - D-013, BR-007 → R-007.
Z /sdd:board sync 2026-10-04 (as-built, bez potwierdzenia [Biz] - numer R po zgodzie właściciela):
- K-9 Formularz odczytu miesiąca: produkcja, oddane, pobrane, cena kWh, faktura; dane EV per pojazd (kWh domowe, km, stan licznika, ładowanie publiczne); przycisk „pobierz z HA” za okres - BR-003, A-004, A-010; tablica: p02, p03, p05; źródło: [App] kod-v3.2.4-2026-09-27.md, main.py:645, 690-720; templates/reading_form.html:266-280 → R-001.
- K-10 Lista odczytów (produkcja, autokonsumpcja, oddane, pobrane, zużycie, oszczędności) i edycja odczytu z podglądem ROI przed/po zmianie - -; tablica: p07, p08; źródło: [Dok] README.md, Odczyty (/odczyty), /api/roi-preview → R-012.
- K-11 Oszczędność PV miesiąca (kWh i zł) liczona wg modelu rozliczeń okresu - BR-001, BR-004, BR-005; tablica: p14; źródło: [App] kod-v3.2.4-2026-09-27.md, enrich_readings_sequence → R-002.
- K-12 Etapy inwestycji: dodaj, edytuj, usuń (koszt, data, moc) - Q-019, Q-021; tablica: p16, p47; źródło: [Dok] README.md, investments; [App] src/main.py /inwestycje/{id}/edytuj, /usun → R-005.
- K-13 Ekran ROI (karty, wykres skumulowanych oszczędności vs inwestycja, tabela wrażliwości, prognoza break-even) i dashboard (baner ROI + 12 ostatnich miesięcy) - BR-006, BR-007, D-012, D-013, Q-018, Q-028, Q-031; tablica: p21, p22; źródło: [Dok] README.md, ROI (/roi), Dashboard (/) → R-008; część R-006, R-007.
- K-14 Pojazdy: dodanie (nazwa, zużycie kWh/100 km, spalanie odpowiednika, paliwo, przebieg startowy) oraz karty /ev i strona pojazdu - BR-008, D-008; tablica: p23, p30; źródło: [App] src/main.py:1562; [Dok] README.md, EV (/ev) → R-009, R-010.
- K-15 Ustawienie degradacji paneli (% rocznie, domyślnie 0,6) - BR-007, A-008; tablica: p34; źródło: [App] src/main.py:1888 → R-007.
- K-16 Eksport odczytów do CSV; pobranie i przywrócenie pełnej kopii JSON (przywrócenie nadpisuje dane, ustawienia zostają) - D-010; tablica: p38, p39, p40; źródło: [Dok] README.md, /odczyty/export.csv; [App] src/main.py:1161 → R-013.
- K-17 Integracja HA: encje (produkcja PV, pobór, oddanie), test połączenia, sensor podsumowania ROI (/api/summary) - BR-009, A-002; tablica: p42, p43, p45; źródło: [Dok] README.md, Home Assistant, /api/ha-test, API JSON → R-015.
Z /sdd:board sync 2026-10-04, proces „Pojazdy EV i paliwo” (as-built, bez potwierdzenia [Biz]):
- K-18 Edycja i usuwanie pojazdu (okres posiadania od-do, notatki) - D-025, D-027; tablica: p50; źródło: [App] src/main.py:1651, 1664 → R-009 albo R-019.
- K-19 Poprawianie i usuwanie ceny paliwa, ekran „Ceny paliwa” (/ev/ceny-paliwa) - D-023, D-024; tablica: p57, p58; źródło: [App] src/main.py:1778, 1798, 1847 → R-011.

## 6. Do przegladu
(lista R/AC dotknietych zmiana zalozen, decyzji albo zakwestionowaniem elementu modelu,
wypelniana automatycznie)
- 2026-10-03: D-002..D-012, A-001, A-002 - brak R w PRD, nic do przeglądu. Kandydaci w §5a.
- 2026-10-04: D-013 (BR-007), A-004/A-005/A-007/A-009/A-010 potwierdzone - przed powstaniem R, nic do przeglądu; uwzględnione w R-001..R-016 od razu.
- 2026-10-04: D-014 (BR-010) -> R-005: dodane AC-005-4, AC-005-5; przejrzane i zatwierdzone przez właściciela instalacji w tej samej sesji.
- 2026-10-04: D-015 (BR-006) -> R-006: dodane AC-006-3; R-008: wykres inwestycji schodkowo wg dat etapów. Przejrzane i zatwierdzone przez właściciela instalacji w tej samej sesji.
- 2026-10-04: D-016 (zmienia D-014; BR-010) -> R-005: AC-005-5 zmienione (dofinansowanie jako etap ujemny); R-006: dofinansowanie obniża pozostało do zwrotu. Przejrzane i zatwierdzone przez właściciela instalacji w tej samej sesji.
- 2026-10-04: D-017 -> R-005: dodane AC-005-6 (etap bez mocy nie zmienia prognozy). Przejrzane i zatwierdzone przez właściciela instalacji w tej samej sesji.
- 2026-10-04: D-018 (BR-006) -> R-006: dodane AC-006-4 (karta „mies. do ROI”). Przejrzane i zatwierdzone przez właściciela instalacji w tej samej sesji.
- 2026-10-04: D-019 (BR-007, doprecyzowuje D-013) -> R-007: AC-007-3 zmienione (tabela per scenariusz); R-008: dodane AC-008-3 (dashboard N > 36). Przejrzane i zatwierdzone przez właściciela instalacji w tej samej sesji.
- 2026-10-04: walidacja -> R-007 AC-007-1 (tolerancja), R-008 AC-008-1 (konkretne karty) doprecyzowane; zatwierdzone przez właściciela instalacji.
- 2026-10-04: D-020 -> nowe R-018, R-001 (opis), §4; D-021 (BR-006) -> R-005 (opis), R-006 dodane AC-006-5. Zatwierdzone przez właściciela instalacji (odpowiedzi z tablicy h01, h09).
- 2026-10-04: A-013 potwierdzone -> R-015: AC-015-1 doprecyzowane (format wyniku testu), AC-015-2 zostaje jako regresja. Zatwierdzone przez właściciela instalacji.
- 2026-10-04: D-022 (zmienia D-005) -> R-016: bez A-001, dodane AC-016-5. Zatwierdzone przez właściciela instalacji.
- 2026-10-04: D-023 -> R-010: dodane AC-010-3 (jedna reguła ceny paliwa dla /ev i ROI); R-006, R-008: liczby ROI mogą się zmienić. D-024 -> R-011: dodane AC-011-4. D-025 -> nowe R-019 (robocze, czeka na Q-045); R-010 obejmuje pojazdy nieaktywne. D-026 (BR-011) -> R-001, R-010 (Reguly: BR-011). BR-012 (A-014 niepotwierdzone) -> R-009. Zgoda właściciela instalacji („tak”, sync tablicy); kod v3.3.1 nie spełnia AC-010-3, AC-019-1.
- 2026-10-04: D-027 (BR-012 nowe brzmienie, A-014 obalone) -> R-009: opis, dodane AC-009-3, AC-009-4; R-010, R-001: km i oszczędności przeliczane po zmianie przebiegu startowego. D-026 (BR-011) -> R-001: dodane AC-001-5. R-019: AC-019-2 (zaślepka) usunięte, kryterium formularza po Q-045. Zatwierdzone przez właściciela instalacji (/sdd:spec, „tak”); kod v3.3.1 nie spełnia AC-009-3, AC-009-4, AC-019-1.
- 2026-10-04: D-028 -> R-019: opis, dodane AC-019-2, AC-019-3, status zatwierdzone; R-001: formularz odczytu bez pól EV pojazdu nieaktywnego. Zatwierdzone przez właściciela instalacji (sync tablicy, „tak”); kod v3.3.1 nie spełnia AC-019-1..AC-019-3.
- 2026-10-04: D-029 (uzupełnia D-023) -> R-010: dodane AC-010-4 (miesiące przed pierwszą ceną paliwa liczone wg pierwszej ceny); R-006, R-008: liczby ROI. Zatwierdzone przez właściciela instalacji („tak”); kod v3.3.1 nie spełnia AC-010-4 na kartach /ev.
- 2026-10-05: D-030 (/api/summary do usunięcia) -> R-015: opis i AC-015-2 (regresja /api/summary) do zmiany - kandydat K-20. R-004, R-013: dopisany rodzaj kontrakt (S-006), bez zmiany kryteriów; nowe R-020 (kontrakt HA, robocze; AC-020-2, AC-020-3 na A-016, A-015 niepotwierdzonych, Q-050). Zgoda właściciela instalacji (session-2026-10-05.md).
- 2026-10-08: D-031 (cena kWh: domyślna z konfiguracji add-onu, gdy odczyt jej nie ma; cena z faktury wpisywana w odczycie) -> R-001 (pole ceny kWh), R-002 (wycena oszczędności przy pustej cenie), R-006 (ROI) - do przejrzenia przy /sdd:spec. SYSTEMS.md S-003 „Przy awarii” uzupełnione.
- 2026-10-08: D-032 (model rozliczeń miesiąca wg okresu obowiązującego 1. dnia miesiąca; zgodne z v3.4.0) -> R-017, R-002 - do przejrzenia przy /sdd:spec (kryterium dla okresu startującego w środku miesiąca); kod v3.4.0 już tak liczy. Q-055 (nakładające się okresy) zaparkowane.
- 2026-10-08: D-033 (numer i kwota brutto faktury - pomocnicze, poza obliczeniami; zgodne z v3.4.0) -> R-001 (pola faktury w odczycie) - do przejrzenia przy /sdd:spec.
- 2026-10-08: A-015 potwierdzone (brak danych z HA: komunikat, odczyt nie blokowany, liczby przepisywane ręcznie z aplikacji zewnętrznej) -> R-020 (AC-020-3 przestaje stać na niepotwierdzonym A-015), R-001, R-015 - do przejrzenia przy /sdd:spec. SYSTEMS.md S-002 „Przy awarii” uzupełnione; nowe Q-054 (jaka aplikacja zewnętrzna).
- 2026-10-08: A-002 potwierdzone -> §4 (bez zmiany treści); A-003 potwierdzone -> §1 Cel, §3 Zakres (bez zmiany treści); A-016 potwierdzone -> R-020 (AC-020-2 przestaje stać na niepotwierdzonym A-016; z A-015 - R-020 bez niepotwierdzonych A). SYSTEMS.md S-007, S-008 (ręczne źródła pól EV) -> R-010, R-001 (Q-052, Q-053) - do przejrzenia przy /sdd:spec.
- 2026-10-08: walidacja (WARN 7) -> R-020 AC-020-2 przepisane na konkretne zdarzenie (otwarcie listy odczytów po zmianie danych w HA). Zatwierdzone przez właściciela instalacji („tak”).
- 2026-10-08: porządki po przeglądzie tablicy - z opisów R-003, R-004, R-006, R-007, R-011, R-014 i reguł BR-006, BR-007 usunięte nieaktualne „stan docelowy / dziś…” (zbudowane w v3.3.0-v3.4.0, sprawdzone w kodzie); bez zmiany AC. Nowe Q-060 (usunięcie pojazdu kasuje dane) -> R-009, R-010, R-006, R-019. Zgoda właściciela instalacji („rob”).
- 2026-10-08: nowe BR-013 (D-032) -> R-017, R-002 (pole Reguly); BR-014 (D-031) -> R-001, R-002, R-006 (pole Reguly) - do dopisania przy /sdd:spec.
- 2026-10-08: /sdd:spec - przegląd wykonany: R-001 (opis, BR-014, AC-001-6), R-002 (BR-013, BR-014, AC-002-5), R-006 (BR-014), R-015 (bez /api/summary, AC-015-2 zmienione; K-20 zrealizowany), R-017 (opis, BR-013, AC-017-5), R-020 zatwierdzone; R-010 przejrzane bez zmian; §1, §4 zaktualizowane. Zatwierdzone przez właściciela instalacji („tak”).
- 2026-10-08: /sdd:board sync - Q-056/Q-057 -> R-001 opis źródeł danych EV (km - S-007, kWh domowe - S-009, publiczne - S-008, uzupełnianie później), bez zmiany AC; Q-058 -> ACTORS (jedyny użytkownik), wspiera A-002. Zgoda właściciela instalacji („tak”).
- 2026-10-10: D-034 (usunięcie pojazdu domyślnie zostawia dane miesięczne, liczone jak pojazd nieaktywny; skasowanie danych tylko po wyraźnym potwierdzeniu) -> R-009 (brak AC usuwania), R-010, R-006, R-008 (oszczędności i ROI bez spadku wstecz), R-019 (relacja z pojazdem nieaktywnym) - do przejrzenia przy /sdd:spec; ENTITIES Pojazd: nowy stan usunięty. Kod v3.4.0 nie spełnia (src/main.py:1677 kasuje ev_monthly bez pytania).

## 7. Otwarte pytania blokujace
(Q z etykieta blokujaca)
- 2026-10-04: brak - żadne Q nie ma etykiety „blokuje go-live”; żadne R nie zostało wstrzymane.
