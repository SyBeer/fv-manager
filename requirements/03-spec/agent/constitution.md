<!-- GENEROWANE z PRD.md 2026-10-04 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Constitution - FV Manager

Niezmienne zasady dla agenta budującego. Źródło prawdy: `03-spec/PRD.md` (R-001..R-017, wszystkie zatwierdzone).

## Aktor
Jedyna rola: **Właściciel instalacji** - wpisuje odczyty, etapy inwestycji, pojazdy, ceny paliwa i RCE, ustawia okresy rozliczeniowe, importuje/eksportuje dane, sprawdza ROI i oszczędności (02-domain/ACTORS.md).

## Słownik (zatwierdzony) - używaj tych nazw w kodzie, UI i testach
| Pojęcie | Definicja | Synonimy | Przykład | Źródło | Status |
|---|---|---|---|---|---|
| Pula net-meteringu | Energia oddana do sieci × współczynnik (domyślnie 0,80, ustawienie net_metering_ratio), do odebrania w kolejnych miesiącach; przechodzi z miesiąca na miesiąc i zeruje się w miesiącu startu cyklu rozliczeniowego (BR-001). | pula, carry-over | oddane 100 kWh w maju → 80 kWh do odebrania do końca cyklu | [Biz] board.json, qq001 (D-002); [App] kod-v3.2.4-2026-09-27.md, Rozliczenie net-metering | zatwierdzone |
| Cykl rozliczeniowy | Roczny okres, po którym pula net-meteringu się zeruje; miesiąc startu ustawia użytkownik (domyślnie kwiecień). | rok rozliczeniowy | cykl kwiecień–marzec | [Biz] board.json, qq012 (D-003) | zatwierdzone |
| Okres rozliczeniowy | Przedział czasu od daty startu, dla którego użytkownik ustawia model rozliczeń (net-metering albo net-billing). | billing period | od 2021-06 net-metering | [Biz] board.json, qq002 (D-004); [App] kod-v3.2.4-2026-09-27.md, Net-billing i RCE | zatwierdzone |
| Net-metering | Model rozliczeń, w którym oddana energia trafia do puli net-meteringu i jest odbierana bez opłaty za energię. | stary system opustów | - | [Biz] board.json, qq002 (D-004) | zatwierdzone |
| Net-billing | Model rozliczeń, w którym oddana energia jest wyceniana po cenie RCE, a oszczędność = autokonsumpcja × cena zakupu + oddane × cena RCE. Model wynika z okresu rozliczeniowego, nie z daty ustawowej (D-005). | nowy system | - | [Biz] board.json, qq002, qq003 (D-004, D-005); [App] kod-v3.2.4-2026-09-27.md, Net-billing i RCE | zatwierdzone |
| Cena RCE | Rynkowa cena energii, po której wyceniana jest energia oddana w net-billingu; wpisywana ręcznie przez użytkownika (data, cena, źródło). Odczyt może mieć własną cenę sprzedaży, która ją nadpisuje. | RCE, RCEm | - | [Biz] board.json, qq002 (D-004); [App] kod-v3.2.4-2026-09-27.md, Net-billing i RCE | zatwierdzone |
| Cena paliwa | Cena paliwa wpisywana ręcznie przez użytkownika (data, cena, typ, źródło), używana do porównania kosztu EV z autem spalinowym. | - | - | [Biz] board.json, qq005 (D-006) | zatwierdzone |
| Oszczędność EV z FV | Oszczędność z ładowania samochodu w domu energią z instalacji; jedyna część oszczędności EV wchodząca do ROI. | - | - | [Biz] board.json, qq006 (D-008); [Dok] README.md, Ładowanie domowe vs publiczne | zatwierdzone |
| Oszczędność EV vs paliwo | Oszczędność z ładowania domowego i publicznego w porównaniu z kosztem paliwa; pokazywana na kartach /ev, nie wchodzi do ROI. | - | - | [Biz] board.json, qq006 (D-008); [Dok] README.md, Widoki /ev | zatwierdzone |

## Poza zakresem - nie buduj
(rownie wazne jak zakres)
- Strony /bateria i /ogrzewanie - makiety przyszłych funkcji (D-011).
- Uwierzytelnianie ponad istniejący opcjonalny Basic Auth (FV_AUTH_PASSWORD), dopóki tryb standalone nie jest wystawiony poza sieć domową (A-002, niepotwierdzone).
- Automatyczne pobieranie cen RCE i cen paliwa - wpisywane ręcznie (D-004, D-006).
- Wariant procentowy w analizie wrażliwości - 7 stałych cen (D-012).
- Osobna kategoria kosztów eksploatacji - wszystkie wydatki na instalację to etapy inwestycji (D-017).

## Reguły biznesowe (globalne)
| ID | Reguła | Źródło | Założenia | Wymagania | Status |
|---|---|---|---|---|---|
| BR-001 | Jeżeli zaczyna się miesiąc startu cyklu rozliczeniowego (ustawienie użytkownika, domyślnie kwiecień) albo zmienia się model rozliczeń, to pula net-meteringu się zeruje; w pozostałych miesiącach niewykorzystana pula przechodzi na kolejny miesiąc. | [Biz] board.json, qq001, qq012 (D-002, D-003); [App] kod-v3.2.4-2026-09-27.md, Rozliczenie net-metering | - | R-002, R-003 | robocze |
| BR-002 | Jeżeli choć jeden wiersz importowanego pliku CSV ma zły format okresu (inny niż RRRR.MM), wartość ujemną albo energię oddaną większą niż produkcja, to żaden wiersz pliku nie jest zapisywany, a użytkownik dostaje raport: numer wiersza i powód. | [Biz] board.json, qq008; czat sesji 2026-10-03 (D-009) | - | R-004 | robocze |
| BR-003 | Jeżeli okres ma format inny niż RRRR.MM, któraś wartość jest ujemna albo energia oddana jest większa niż produkcja, to odczyt nie zostaje zapisany, a formularz pokazuje błąd. | [App] kod-v3.2.4-2026-09-27.md, Walidacja odczytów | A-004 | R-001 | robocze |
| BR-004 | Jeżeli okres jest rozliczany w net-meteringu, to oszczędność miesiąca = autokonsumpcja + część puli (oddane × współczynnik, domyślnie 0,80) zużyta na pobór. | [App] kod-v3.2.4-2026-09-27.md, Rozliczenie net-metering | A-005 | R-002 | robocze |
| BR-005 | Jeżeli okres jest rozliczany w net-billingu, to oszczędność miesiąca = autokonsumpcja × cena zakupu + oddane × cena RCE; cena sprzedaży wpisana w odczycie nadpisuje RCE. | [App] kod-v3.2.4-2026-09-27.md, calculations.py:94-159; [Biz] D-004 | A-006 | R-002, R-017 | robocze |
| BR-006 | Pozostało do zwrotu = suma etapów inwestycji − Σ oszczędności FV − Σ „Oszczędność EV z FV”; miesiące do zwrotu = pozostało / średnia miesięczna oszczędność. Etap inwestycji liczy się od miesiąca swojej daty (D-015, docelowo; dziś wszystkie etapy od początku). | [Dok] README.md, calc_roi; [Biz] D-008; [Biz] D-015; [Biz] D-018 (miesiące do zwrotu) | A-007 | R-006, R-008 | robocze |
| BR-007 | Prognoza obejmuje 36 miesięcy, z degradacją paneli (domyślnie 0,6) i scenariuszami wzrostu cen 0/3/7/12%. Jeżeli zwrot przypada później niż 36 mies., to tabela scenariuszy podaje „zwrot za N mies.” dla każdego scenariusza, a dashboard liczbę miesięcy do zwrotu (D-013, D-019; docelowo - dziś tabela nie podaje). | [App] src/main.py:995-1008, services/forecast.py; [Biz] D-013; [Biz] D-019 | A-008 | R-007, R-008 | robocze |
| BR-008 | Jeżeli przy dodawaniu pojazdu brak przebiegu startowego, to pojazd nie zostaje dodany. | [App] src/main.py:1573 | A-009 | R-009 | robocze |
| BR-009 | (techniczna) Jeżeli dane pobierane są z Home Assistant, to najpierw ze Statistics API, a gdy ich brak - z History API (ok. 10 dni wstecz); wartości w Wh są zamieniane na kWh. | [Dok] README.md, Home Assistant | A-010 | R-001, R-015 | robocze |
| BR-010 | Jeżeli koszt etapu inwestycji jest ujemny, to etap jest dofinansowaniem i zmniejsza łączną inwestycję; koszt może być zerowy, dodatni albo ujemny. | [Biz] session-2026-10-04.md, Q-021, Q-022 (D-014 zmieniona przez D-016) | - | R-005, R-006 | robocze |

## Zasady pracy
- Każda zmiana kodu wskazuje R-xxx i AC-xxx-n, które realizuje; test nazywa się od AC (np. `test_AC_006_3_...`).
- TDD: test z AC napisany przed kodem; nie mockuj realnych API (HA).
- Rozjazd kodu ze specyfikacją = zmiana PRD (przez człowieka) albo kodu - nigdy cicha zmiana zachowania.
- Kryteria opisane jako „stan docelowy” zmieniają działanie v3.2.x; pozostałe opisują działanie obecne (testy regresji).
