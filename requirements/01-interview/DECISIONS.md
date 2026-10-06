# Decyzje

Szablon wpisu:

## D-xxx | YYYY-MM-DD | <tytul>
Pytanie:
Decyzja:
Powod:            (puste = automatycznie nowe Q "dlaczego")
Zdecydowal:       (rola)
Zrodlo:
Wplyw:            (R, AC, A)
Zamyka pytanie:   (Q)
Otwiera pytania:  (Q)

## D-001 | 2026-09-27 | BUSINESS.md i review-2026-05-12.md opisują nieaktualną wersję v1.12.0
Pytanie: Q-007 - czy BUSINESS.md i review-2026-05-12.md opisują obecną aplikację?
Decyzja: Oba dokumenty dostają status `dotyczy innej wersji v1.12.0`. Nie są źródłem stanu obecnego (v3.2.4), zostają jako tło historyczne.
Powod: "nie sięgałem, to stare dokumenty v1.12" (Tomek, sesja 2026-09-27).
Zdecydowal: właściciel instalacji (Tomek)
Zrodlo: [Biz] 01-interview/session-2026-09-27.md, Q-007
Wplyw: brak R/A. Pytania: Q-004 i Q-006 zawężone do README.md vs metodologia.html; Q-003, Q-008, Q-009, Q-010 z `sprzeczne` na `otwarte` (luka: jak jest w v3.2.4).
Zamyka pytanie: Q-007
Otwiera pytania: -

## D-002 | 2026-10-03 | Pula net-meteringu kumuluje się w cyklu rocznym
Pytanie: Q-001 - jak rozliczana jest pula net-meteringu?
Decyzja: Pula przechodzi z miesiąca na miesiąc (carry-over) i zeruje się raz w roku, w miesiącu startu cyklu rozliczeniowego (BR-001). Obecne działanie kodu v3.2.4 jest docelowe. Opis w README („każdy miesiąc osobno”) do poprawy.
Powod: właściciel poprosił o propozycję wyjaśnienia; kod v3.2.4 liczy w ten sposób, właściciel zatwierdził (warsztat 2026-10-03).
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] board.json, qq001 (warsztat 2026-10-03); [App] kod-v3.2.4-2026-09-27.md, Rozliczenie net-metering
Wplyw: BR-001, GLOSSARY: Pula net-meteringu. Brak R w PRD. Kandydat: poprawka README.
Zamyka pytanie: Q-001
Otwiera pytania: -

## D-003 | 2026-10-03 | Miesiąc startu cyklu rozliczeniowego ustawia użytkownik
Pytanie: Q-012 - w którym miesiącu zeruje się pula?
Decyzja: Miesiąc startu rocznego cyklu rozliczeniowego jest ustawieniem użytkownika (domyślnie kwiecień). Dziś kod zawsze używa kwietnia (cycle_start_month=4) bez ustawienia w UI.
Powod: „To powinno być konfigurowane przez użytkownika.” (właściciel instalacji, warsztat 2026-10-03)
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] board.json, qq012 (warsztat 2026-10-03)
Wplyw: BR-001, GLOSSARY: Cykl rozliczeniowy. Kandydat R: ustawienie miesiąca startu cyklu.
Zamyka pytanie: Q-012
Otwiera pytania: -

## D-004 | 2026-10-03 | Aplikacja obsługuje net-metering i net-billing, ceny RCE wpisywane ręcznie
Pytanie: Q-002 - czy aplikacja obsługuje net-billing i skąd ceny RCE?
Decyzja: Model rozliczeń (net-metering / net-billing) jest wybierany per okres rozliczeniowy ustawiany przez użytkownika na /pv. Ceny RCE użytkownik wpisuje ręcznie; aplikacja ich nie pobiera. Tekst metodologia.html o automatycznym pobieraniu do poprawy.
Powod: właściciel poprosił o propozycję wyjaśnienia; zgodne z kodem v3.2.4, zatwierdzone (warsztat 2026-10-03).
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] board.json, qq002 (warsztat 2026-10-03); [App] kod-v3.2.4-2026-09-27.md, Net-billing i RCE
Wplyw: GLOSSARY: Net-metering, Net-billing, Cena RCE, Okres rozliczeniowy. Kandydat: poprawka metodologia.html.
Zamyka pytanie: Q-002
Otwiera pytania: -

## D-005 | 2026-10-03 | Aplikacja nie wyprowadza modelu rozliczeń z daty ustawowej
Pytanie: Q-003 - od kiedy obowiązuje net-billing?
Decyzja: Aplikacja nie koduje daty wejścia net-billingu; model wynika z okresów rozliczeniowych ustawionych przez użytkownika (D-004). Daty ustawowe tylko w tekście metodologii, wg A-001.
Powod: właściciel poprosił o propozycję wyjaśnienia; zatwierdzone (warsztat 2026-10-03).
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] board.json, qq003 (warsztat 2026-10-03)
Wplyw: A-001, GLOSSARY: Net-billing. Kandydat: poprawka metodologia.html.
Zamyka pytanie: Q-003
Otwiera pytania: -
Zmieniona przez: D-022

## D-006 | 2026-10-03 | Ceny paliwa wpisywane ręcznie
Pytanie: Q-005 - skąd pochodzą ceny paliwa?
Decyzja: Ceny paliwa wpisuje użytkownik ręcznie (data, cena, typ, źródło). Aplikacja ich nie pobiera. Tekst metodologia.html o automatycznym pobieraniu do poprawy.
Powod: „ręcznie wpisuje” (właściciel instalacji, warsztat 2026-10-03); zgodne z kodem v3.2.4.
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] board.json, qq005 (warsztat 2026-10-03); [App] kod-v3.2.4-2026-09-27.md, Ceny paliwa
Wplyw: GLOSSARY: Cena paliwa. Kandydat: poprawka metodologia.html.
Zamyka pytanie: Q-005
Otwiera pytania: -

## D-007 | 2026-10-03 | Śledzenie cen paliwa jako opcja wybierana przy pierwszym samochodzie
Pytanie: Q-014 - gdzie wpisać ceny paliwa?
Decyzja: Przy dodawaniu pierwszego samochodu właściciel decyduje, czy śledzi ceny paliwa. Jeśli tak - w menu pod EV jest pozycja „Ceny paliwa”. Jeśli nie - pozycji nie ma.
Powod: „to właściciel powinien decydować czy chce dodawać te informacje (...) podejmuje decyzję w trakcie dodawania pierwszego samochodu” (właściciel instalacji, warsztat 2026-10-03).
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] board.json, nmuspw64n (warsztat 2026-10-03, dopisane w przeglądarce)
Wplyw: Kandydaci R: wybór przy pierwszym samochodzie, warunkowa pozycja menu.
Zamyka pytanie: Q-014
Otwiera pytania: -

## D-008 | 2026-10-03 | Dwa hasła: „Oszczędność EV z FV” i „Oszczędność EV vs paliwo”
Pytanie: Q-006 - jak nazywać dwie liczby oszczędności EV?
Decyzja: „Oszczędność EV z FV” = tylko ładowanie domowe, wchodzi do ROI. „Oszczędność EV vs paliwo” = ładowanie domowe + publiczne, na kartach /ev, nie wchodzi do ROI.
Powod: „Nie wiem, zaproponuj coś” - propozycja zatwierdzona (właściciel instalacji, warsztat 2026-10-03).
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] board.json, qq006 (warsztat 2026-10-03); [Dok] README.md, Ładowanie domowe vs publiczne
Wplyw: GLOSSARY: dwa hasła zamiast jednego.
Zamyka pytanie: Q-006
Otwiera pytania: -

## D-009 | 2026-10-03 | Import CSV: cały plik albo nic, z raportem błędnych wierszy
Pytanie: Q-008 - czy import CSV sprawdza dane?
Decyzja: Jeśli choć jeden wiersz pliku jest błędny (zły format okresu RRRR.MM, wartość ujemna, oddane > produkcja), aplikacja nie zapisuje żadnego wiersza i pokazuje raport: numer wiersza i powód. Zmiana względem v3.2.4, który pomija błędne wiersze bez informacji (rejected=0). Przykład CSV w README do poprawy (separator „;”, polskie nagłówki).
Powod: „system nie powinien załadować takiego pliku i wskazać raport które wiersze są błędne” (właściciel instalacji, sesja 2026-10-03).
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] board.json, qq008; czat sesji 2026-10-03
Wplyw: BR-002. Kandydat R: import all-or-nothing z raportem.
Zamyka pytanie: Q-008
Otwiera pytania: -

## D-010 | 2026-10-03 | „Wyczyść bazę” opisuje dokładnie, co usuwa
Pytanie: Q-010 - co usuwa „Wyczyść bazę”?
Decyzja: Przycisk usuwa wszystkie dane (odczyty, inwestycje, ceny paliwa, pojazdy, dane EV, okresy rozliczeniowe, ceny RCE; ustawienia zostają). Tekst w UI wymienia wszystko, co znika, i zaleca kopię (/backup/full) przed kliknięciem.
Powod: „Nigdy - ale trzeba to uspójnić” (właściciel instalacji, warsztat 2026-10-03); propozycja zatwierdzona.
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] board.json, qq010; [App] kod-v3.2.4-2026-09-27.md, Czyszczenie bazy
Wplyw: Kandydat R: tekst przycisku i ostrzeżenie.
Zamyka pytanie: Q-010
Otwiera pytania: -

## D-011 | 2026-10-03 | /bateria i /ogrzewanie to makiety poza zakresem
Pytanie: Q-013 - czym są strony /bateria i /ogrzewanie?
Decyzja: To makiety przyszłych funkcji. Poza zakresem obecnej wersji (PRD §4).
Powod: „To tylko mockupy aby dorobić taką funkcjonalność w przyszłości” (właściciel instalacji, warsztat 2026-10-03).
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] board.json, qq013
Wplyw: PRD §4.
Zamyka pytanie: Q-013
Otwiera pytania: -

## D-012 | 2026-10-03 | Analiza wrażliwości: 7 stałych cen
Pytanie: Q-004 - układ analizy wrażliwości.
Decyzja: Zostaje 7 stałych cen (0,50; 0,60; 0,70; 0,80; 0,90; 1,00; 1,20 zł/kWh), tylko podgląd. Bez wariantu procentowego. Do poprawy: metodologia.html („wzrost o 20%”) i podtytuł tabeli na /roi („×0.8” zamiast faktycznego współczynnika z ustawień).
Powod: właściciel wybrał wariant (a) po sprawdzeniu kodu (sesja 2026-10-03).
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] board.json, qq004; czat sesji 2026-10-03; [App] kod-v3.2.4-2026-09-27.md, Analiza wrażliwości
Wplyw: Kandydaci: poprawka metodologia.html, podtytuł /roi.
Zamyka pytanie: Q-004
Otwiera pytania: -

## D-013 | 2026-10-04 | Zwrot po horyzoncie prognozy podawany liczbą miesięcy
Pytanie: Q-020 - co pokazuje prognoza, gdy zwrot przypada po 36 miesiącach?
Decyzja: Wykres prognozy obejmuje 36 miesięcy. Gdy zwrot przypada później, aplikacja podaje słownie liczbę miesięcy do zwrotu (np. „zwrot za 53 mies.”). Stan docelowy - dziś v3.2.4 w takim przypadku nie podaje liczby miesięcy.
Powod: wykres na dalszy okres niewiele mówi, ale liczba miesięcy do zwrotu jest potrzebna (propozycja prowadzącego zatwierdzona przez właściciela, sesja 2026-10-04).
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] session-2026-10-04.md, Q-028 (odpowiedź dotyczyła Q-020)
Wplyw: BR-007 (dopisek o zwrocie po 36 mies.), p19, kandydat K-8 w PRD §5a.
Zamyka pytanie: Q-020
Otwiera pytania: Q-031
Doprecyzowana przez: D-019

## D-014 | 2026-10-04 | Koszt etapu inwestycji: zero dozwolone, ujemny nie
Pytanie: Q-021 - etapy z kosztem zerowym lub ujemnym.
Decyzja: Koszt etapu inwestycji może wynosić 0 zł; koszt ujemny jest odrzucany (BR-010). Stan docelowy - dziś formularz przyjmuje też koszt ujemny.
Powod: etap bez kosztu jest możliwy (np. dołożenie czegoś bez wydatku), ujemny koszt nie ma sensu (propozycja prowadzącego zatwierdzona przez właściciela, sesja 2026-10-04).
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] session-2026-10-04.md, Q-021
Wplyw: BR-010; R-005 (AC-005-4, AC-005-5) - PRD §6.
Zamyka pytanie: Q-021
Otwiera pytania: Q-032
Zmieniona przez: D-016

## D-015 | 2026-10-04 | Data etapu inwestycji uwzględniana w ROI
Pytanie: Q-019 - czy data etapu wpływa na ROI?
Decyzja: Etap inwestycji wchodzi do inwestycji od miesiąca swojej daty. Wykres /roi pokazuje inwestycję schodkowo; „pozostało do zwrotu” w danym miesiącu uwzględnia tylko etapy z datą nie późniejszą niż ten miesiąc. Stan docelowy - dziś v3.2.4 sumuje wszystkie etapy od pierwszego odczytu (błąd).
Powod: „data powinna byc uwzgledniana. jezeli nie jest - to blad” (właściciel instalacji, sesja 2026-10-04).
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] session-2026-10-04.md, Q-019
Wplyw: BR-006; R-006 (AC-006-3), R-008 (wykres) - PRD §6. Zadanie w backlogu jako błąd.
Zamyka pytanie: Q-019
Otwiera pytania: -

## D-016 | 2026-10-04 | Dofinansowanie jako etap inwestycji z ujemnym kosztem
Pytanie: Q-022 - jak w aplikacji uwzględnić dofinansowanie?
Decyzja: Dofinansowanie wpisuje się jako etap inwestycji z ujemnym kosztem; zmniejsza łączną inwestycję. Koszt etapu może być zerowy, dodatni albo ujemny. Zmienia D-014 (zakaz kosztu ujemnego). Zgodne z działaniem v3.2.4.
Powod: „dofinansowanie to obnizenie kosztów”; „dofinansowanie wpisalem jako dodatkowe zdarzenie ktore mialo wartosc ujemna”; „zmianiem decyzje. dofinansowanie to etap inwestycji z ujemnym budzetem.” (właściciel instalacji, sesja 2026-10-04).
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] session-2026-10-04.md, Q-022
Wplyw: BR-010 (nowe brzmienie); R-005 (AC-005-5), R-006 - PRD §6. Zmienia D-014.
Zamyka pytanie: Q-022
Otwiera pytania: -

## D-017 | 2026-10-04 | Wszystkie wydatki na instalację jako etapy inwestycji
Pytanie: Q-023 - wydatki po uruchomieniu instalacji.
Decyzja: Każdy wydatek związany z instalacją, także po uruchomieniu (serwis, naprawy itp.), wpisuje się jako etap inwestycji. Aplikacja nie ma osobnej kategorii kosztów eksploatacji. Etap bez mocy nie zmienia prognozy. Zgodne z v3.2.4.
Powod: „wszystko co dotyczy tego temau wpisuje jako inwestycja” (właściciel instalacji, sesja 2026-10-04).
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] session-2026-10-04.md, Q-023; [App] src/services/forecast.py get_capacity_stages
Wplyw: R-005 (AC-005-6) - PRD §6; PRD §4 (osobna kategoria kosztów poza zakresem).
Zamyka pytanie: Q-023
Otwiera pytania: -

## D-018 | 2026-10-04 | Termin zwrotu = karta „mies. do ROI”
Pytanie: Q-018 - która liczba miesięcy do zwrotu jest właściwa?
Decyzja: Termin zwrotu dla właściciela to karta „mies. do ROI”: pozostało do zwrotu / średnia miesięczna oszczędność z historii (z Oszczędnością EV z FV). Tabela scenariuszy jest pomocnicza. Zgodne z v3.2.4.
Powod: z tej karty właściciel korzysta przy sprawdzaniu terminu zwrotu (propozycja prowadzącego zatwierdzona przez właściciela, sesja 2026-10-04).
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] session-2026-10-04.md, Q-018
Wplyw: BR-006 (część o miesiącach - źródło [Biz]); R-006 (AC-006-4) - PRD §6; rozjazd z D-013 (prognoza bez EV) - Q-031.
Zamyka pytanie: Q-018
Otwiera pytania: -

## D-019 | 2026-10-04 | „Zwrot za N mies.” w tabeli scenariuszy i na dashboardzie
Pytanie: Q-031 - gdzie podawać liczbę miesięcy, gdy zwrot przypada po 36 mies. (doprecyzowanie D-013)?
Decyzja: Gdy zwrot przypada po 36 mies., tabela scenariuszy pokazuje „zwrot za N mies.” dla każdego scenariusza (prognoza liczona poza 36 mies.; wykres nadal kończy się na 36). Dashboard pokazuje „Do zwrotu inwestycji N mies.” także przy N > 36 (v3.2.5 już tak robi - dashboard.html:33-36).
Powod: „w tabeli scenariuszy i na dahsboard” - tam właściciel szukał liczby, gdy perspektywa przekraczała 36 mies. (właściciel instalacji, sesja 2026-10-04).
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] session-2026-10-04.md, Q-031; [App] templates/dashboard.html:33-36
Wplyw: doprecyzowuje D-013; BR-007; R-007 (AC-007-3), R-008 (AC-008-3) - PRD §6.
Zamyka pytanie: Q-031
Otwiera pytania: -

## D-020 | 2026-10-04 | Wycofanie integracji z Tesla Fleet API
Pytanie: Q-016 - pobieranie kWh ładowania z Tesla Fleet API (README opisuje, kod v3.2.4 ma tylko pola w bazie).
Decyzja: Integracja z Tesla Fleet API zostaje wycofana. Pozostałości usuwa się z kodu (kolumny tesla_* w bazie, wzmianki w ev.html), z README, a wycofanie z powodem opisuje się w CHANGELOG aplikacji. Dane właściciela zostają nienaruszone.
Powod: „To nie działa dobrze. (...) API tesli nie działało za dobrze” (właściciel instalacji, tablica h01, 2026-10-04).
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] board.json, h01 (2026-10-04); [App] src/utils/db.py:200, templates/ev.html; [Dok] README.md
Wplyw: nowe R-018; R-001 (opis); PRD §4. „wychowanie” w odpowiedzi odczytane jako „wycofanie”.
Zamyka pytanie: Q-016
Otwiera pytania: -

## D-021 | 2026-10-04 | Data etapu może poprzedzać pierwszy odczyt
Pytanie: Q-032 - daty etapów spoza okresu odczytów.
Decyzja: Data etapu inwestycji może być wcześniejsza niż pierwszy odczyt (instalacja powstaje przed uruchomieniem licznika). Aplikacja nie sprawdza daty etapu względem odczytów. Etap sprzed pierwszego odczytu liczy się od pierwszego miesiąca z odczytem. Miesiące z odpowiedzi (wrzesień/październik) to tylko przykład.
Powod: „inwestycja w FV była we wrześniu a odczyty zaczęły pojawiać się w październiku po uruchomieniu licznika. Daty trakuuj jako przykład.” (właściciel instalacji, tablica h09, 2026-10-04).
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] board.json, h09 (2026-10-04)
Wplyw: BR-006; R-005 (opis), R-006 (AC-006-5) - PRD §6.
Zamyka pytanie: Q-032
Otwiera pytania: -

## D-022 | 2026-10-04 | Metodologia bez dat ustawowych net-billingu
Pytanie: Q-037 - czy daty ustawowe net-billingu mają być w tekście metodologii?
Decyzja: Tekst metodologia.html nie podaje dat ustawowych net-billingu. Pisze, że model rozliczeń wynika z okresów rozliczeniowych ustawionych przez użytkownika (D-004, D-005), a daty zależą od umowy z operatorem. Zmienia D-005 („daty ustawowe tylko w tekście metodologii, wg A-001”).
Powod: daty ustawowe są złożone (od 1.07.2024 RCE godzinowe tylko dla przyłączonych od tej daty, wcześniejsi z wyborem RCEm/RCE) i nie dotyczą instalacji właściciela (net-metering); wybór wariantu (b) po sprawdzeniu źródeł zewnętrznych (właściciel instalacji, sesja 2026-10-04).
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] session-2026-10-04.md, Q-037
Wplyw: R-016 (opis, Zalozenia, AC-016-5) - PRD §6; A-001 bez wymagań zależnych; zmienia D-005.
Zamyka pytanie: Q-037
Otwiera pytania: -

## D-023 | 2026-10-04 | Jedna reguła ceny paliwa dla miesiąca
Pytanie: Q-038 - karty /ev i ROI biorą inną cenę paliwa dla tego samego miesiąca; Q-039 - brak ceny paliwa.
Decyzja: Cena paliwa obowiązuje od daty wpisu do następnego wpisu. Miesiąc liczy się wg ostatniej ceny wpisanej do końca tego miesiąca (przy dwóch wpisach w miesiącu - późniejszy); miesiąc bez wpisu - poprzednia cena. Cena dotyczy rodzaju paliwa pojazdu. Ta sama reguła na kartach /ev i w ROI.
Powod: właściciel zakładał, że wpisana w miesiącu cena liczy cały miesiąc, a do nowego wpisu obowiązuje stara; dwie reguły w kodzie dają różne liczby (właściciel instalacji, tablica 2026-10-04).
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] board.json, qq038, qq039
Wplyw: R-010 (nowe AC-010-3); R-006, R-008 (liczby ROI); zmienia zachowanie as-built src/main.py:369-372 i 437-443 - PRD §6.
Zamyka pytanie: Q-038, Q-039
Otwiera pytania: Q-044

## D-024 | 2026-10-04 | Śledzenie cen paliwa zmieniane w każdej chwili
Pytanie: Q-040 - zmiana decyzji o śledzeniu cen paliwa po dodaniu pierwszego samochodu.
Decyzja: Właściciel może włączyć albo wyłączyć śledzenie cen paliwa w każdej chwili, nie tylko przy pierwszym samochodzie. Potwierdza decyzje budowy B-15..B-17; B-18 (wyłączenie nie usuwa cen) pozostaje decyzją budowy.
Powod: „to jest sporadyczne działanie” - zmiana rzadka, ale się zdarza (właściciel instalacji, tablica 2026-10-04).
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] board.json, qq040
Wplyw: R-011 (nowe AC-011-4) - PRD §6; uzupełnia D-007.
Zamyka pytanie: Q-040
Otwiera pytania: -

## D-025 | 2026-10-04 | Pojazd nieaktywny
Pytanie: Q-041 - co dzieje się z danymi auta po zmianie, sprzedaży albo wymianie.
Decyzja: Pojazd można oznaczyć jako nieaktywny. Dane pojazdu nieaktywnego dalej wchodzą do oszczędności (EV z FV, EV vs paliwo, ROI).
Powod: właściciel zostawiał dane auta; trzeba je wyłączyć jako nieaktywne, ale oszczędności mają się dalej liczyć (właściciel instalacji, tablica 2026-10-04).
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] board.json, qq041
Wplyw: nowe R-019 (robocze); R-010 (oszczędności także z pojazdów nieaktywnych); ENTITIES.md Pojazd: stan nieaktywny - PRD §6.
Zamyka pytanie: Q-041
Otwiera pytania: Q-045

## D-026 | 2026-10-04 | Kilometry miesiąca ze stanu licznika
Pytanie: Q-042 - jak właściciel wpisuje przejechane km.
Decyzja: Właściciel wpisuje stan licznika. Km miesiąca = stan licznika - poprzedni stan (poprzedni miesiąc, a w pierwszym miesiącu przebieg startowy). Potwierdza zachowanie as-built (_inject_odometer_km) jako BR-011.
Powod: „stan licznika - tak jest łatwiej” (właściciel instalacji, tablica 2026-10-04).
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] board.json, qq042
Wplyw: BR-011 (nowa); R-001 (stan licznika w odczycie), R-010 (km do obliczeń), BR-008 - PRD §6.
Zamyka pytanie: Q-042
Otwiera pytania: -

## D-027 | 2026-10-04 | Zmiana przebiegu startowego pojazdu
Pytanie: propozycja R-009 w /sdd:spec - reguła z kodu (A-014, BR-012): przebieg startowy nie może być wyższy niż najniższy zapisany stan licznika.
Decyzja: Właściciel może zmienić przebieg startowy pojazdu także przy zapisanych stanach licznika. Przed zapisem aplikacja pyta, czy wszystkie zapisane stany licznika przesunąć o różnicę (nowa − stara wartość). Tak: każdy stan licznika zmienia się o różnicę; km miesięcy i oszczędności bez zmian. Nie: zmienia się tylko przebieg startowy, stany licznika niższe niż nowa wartość są usuwane (tylko stan licznika - kWh ładowania i ładowanie publiczne z tego miesiąca zostają); km i oszczędności liczą się od nowych wartości. Zastępuje blokadę z kodu.
Powod: właściciel chce mieć możliwość zmiany przebiegu startowego zamiast blokady, z ostrzeżeniem o przeliczeniu (właściciel instalacji, sesja 2026-10-04).
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] session-2026-10-04.md, D-027
Wplyw: BR-012 (nowe brzmienie); A-014 obalone; R-009 (AC-009-3, AC-009-4); R-010, R-001 (km i oszczędności przez BR-011) - PRD §6.
Zamyka pytanie: -
Otwiera pytania: -

## D-028 | 2026-10-04 | Pojazd nieaktywny w formularzu odczytu
Pytanie: Q-045 - przy których autach właściciel wpisuje dane EV w odczycie miesiąca.
Decyzja: Pojazd aktywny ma pola EV w formularzu odczytu każdego miesiąca; gdy auto stało, pola zostają puste i odczyt się zapisuje. Pojazd nieaktywny nie ma pól EV w formularzu odczytu nowego miesiąca; jego dane z miesięcy, w których je wpisano, są widoczne i edytowalne. Pole „okres posiadania do” bez zmian, niezwiązane z nieaktywnością.
Powod: właściciel wpisuje dane przy autach, którymi jeździł w danym miesiącu; auto, które stało, dalej jest aktywne (właściciel instalacji, tablica 2026-10-04). Ukrycie pól pojazdu nieaktywnego - wniosek prowadzącego z odpowiedzi, zatwierdzony przez właściciela („tak”).
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] board.json, qq045
Wplyw: R-019 (AC-019-2, AC-019-3, status zatwierdzone); R-001 (formularz odczytu) - PRD §6; ENTITIES.md Pojazd.
Zamyka pytanie: Q-045
Otwiera pytania: -

## D-029 | 2026-10-04 | Miesiące przed pierwszą ceną paliwa
Pytanie: Q-044 - jak liczyć oszczędność EV w miesiącach wcześniejszych niż pierwsza wpisana cena paliwa (dziś /ev bierze najnowszą cenę, ROI najstarszą dowolnego paliwa).
Decyzja: Jeżeli miesiąc z danymi EV jest wcześniejszy niż pierwsza cena paliwa rodzaju używanego przez pojazd, to liczy się wg tej pierwszej ceny (przeliczenie wstecz). Od daty pierwszej ceny obowiązuje D-023 (od wpisu do wpisu). Ta sama reguła na kartach /ev i w ROI.
Powod: właściciel nie zawsze wpisuje cenę paliwa od pierwszego dnia pojazdu; gdy przebieg był wpisany wcześniej, a cena paliwa później, przeliczenie ma iść wstecz do daty wpisania paliwa (właściciel instalacji, sesja 2026-10-04).
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] session-2026-10-04.md, Q-044
Wplyw: R-010 (nowe AC-010-4); R-006, R-008 (liczby ROI); uzupełnia D-023 - PRD §6.
Zamyka pytanie: Q-044
Otwiera pytania: -

## D-030 | 2026-10-05 | Podsumowanie ROI dla Home Assistant (/api/summary) do usunięcia
Pytanie: propozycja C z /sdd:spec (rejestr systemów, S-002) - co z wyjściem /api/summary, z którego właściciel nie korzysta.
Decyzja: Wyjście do Home Assistant (/api/summary - podsumowanie ROI dla sensora HA) jest do usunięcia z aplikacji. Nie powstaje dla niego wymaganie kontraktu.
Powod: właściciel nie korzysta z /api/summary (Q-030, session-2026-10-04.md); AC-015-2 było tylko testem regresji (A-013).
Zdecydowal: właściciel instalacji
Zrodlo: [Biz] session-2026-10-05.md, propozycja C
Wplyw: R-015 (opis i AC-015-2 o /api/summary) - PRD §6; kandydat K-20 w PRD §5a; SYSTEMS.md S-002 (wymiana my -> HA).
Zamyka pytanie: -
Otwiera pytania: -
