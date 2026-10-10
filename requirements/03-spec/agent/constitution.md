<!-- GENEROWANE z PRD.md 2026-10-08 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Constitution - FV Manager

Niezmienne zasady dla agenta budującego. Źródło prawdy: `03-spec/PRD.md` - generowane tylko z wymagań zatwierdzonych (20). Nie buduj wymagań roboczych: -.

## Aktor
Jedyna rola: **Właściciel instalacji** - wpisuje odczyty, etapy inwestycji, pojazdy, ceny paliwa i RCE, ustawia okresy rozliczeniowe, importuje/eksportuje dane, sprawdza ROI i oszczędności. Jedyny użytkownik aplikacji - brak innych ról i uprawnień (02-domain/ACTORS.md, Q-058).

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
| Odczyt miesiąca | Miesięczny zapis danych instalacji: okres (RRRR.MM), produkcja, oddane, pobrane, cena kWh, faktura i dane EV dla każdego pojazdu. | odczyt | odczyt za 2026.09 | [App] kod-v3.2.4-2026-09-27.md, Walidacja odczytów; [Biz] session-2026-10-04.md, Q-024 | zatwierdzone |
| Autokonsumpcja | Energia z PV zużyta na miejscu: produkcja − oddane, nie mniej niż 0. | - | produkcja 500 kWh, oddane 300 kWh → 200 kWh | [App] kod-v3.2.4-2026-09-27.md, calculations.py; [Biz] zatwierdzenie słownika 2026-10-04 | zatwierdzone |
| Etap inwestycji | Wydatek na instalację z datą, kosztem i opcjonalnie mocą (kWp); obejmuje każdy wydatek, także serwis; liczy się od miesiąca swojej daty (etap sprzed pierwszego odczytu - od pierwszego miesiąca z odczytem). | inwestycja | instalacja 30 000 zł (2022-06, 6 kWp); serwis 800 zł bez mocy | [Biz] session-2026-10-04.md, Q-019, Q-023, Q-032 (D-015, D-017, D-021) | zatwierdzone |
| Dofinansowanie | Etap inwestycji z ujemnym kosztem; obniża łączną inwestycję. | - | −5 000 zł | [Biz] session-2026-10-04.md, Q-022 (D-016) | zatwierdzone |
| Łączna inwestycja | Suma kosztów etapów inwestycji z datą nie późniejszą niż dany miesiąc. | - | 30 000 zł + 10 000 zł − 5 000 zł = 35 000 zł | [Biz] session-2026-10-04.md, Q-019 (D-015) | zatwierdzone |
| Pozostało do zwrotu | Łączna inwestycja − Σ Oszczędność PV miesiąca − Σ Oszczędność EV z FV. | - | 40 000 − 15 000 − 3 000 = 22 000 zł | [Biz] session-2026-10-04.md, Q-027 (A-007); RULES.md BR-006 | zatwierdzone |
| Oszczędność PV miesiąca | Wartość energii z PV w miesiącu (kWh i zł), liczona według modelu rozliczeń okresu (net-metering albo net-billing). | oszczędność FV | - | [App] kod-v3.2.4-2026-09-27.md, Rozliczenie net-metering; RULES.md BR-004, BR-005; [Biz] zatwierdzenie słownika 2026-10-04 | zatwierdzone |
| Zwrot inwestycji | Stan inwestycji: „w trakcie” albo „zwrot osiągnięty”, gdy pozostało do zwrotu ≤ 0; termin zwrotu pokazuje karta „mies. do ROI”. | ROI | pozostało 22 000 zł, średnio 500 zł/mies. → 44 mies. | [Biz] session-2026-10-04.md, Q-018 (D-018); [App] calculations.py calc_roi | zatwierdzone |
| Degradacja paneli | Roczny spadek produkcji paneli w % (domyślnie 0,6), używany w prognozie. | - | 0,6% rocznie | [App] src/main.py:1888, src/services/forecast.py; [Biz] zatwierdzenie słownika 2026-10-04 | zatwierdzone |
| Przebieg startowy | Stan licznika pojazdu przy jego dodaniu; bez niego nie można dodać pojazdu. Można go później zmienić: aplikacja pyta, czy przesunąć zapisane stany licznika o różnicę (D-027). | - | 12 000 km | [Biz] session-2026-10-04.md, Q-029 (A-009), D-027; RULES.md BR-008, BR-012 | zatwierdzone (właściciel instalacji, 2026-10-04) |
| Ładowanie publiczne | Ładowanie samochodu poza domem (kWh, km, koszt); wchodzi do Oszczędności EV vs paliwo, nie do ROI. | - | - | [Biz] board.json, qq006 (D-008) | zatwierdzone |
| Pojazd | Samochód elektryczny właściciela instalacji zapisany w aplikacji: nazwa, zużycie kWh/100 km, spalanie odpowiednika l/100 km, rodzaj paliwa, przebieg startowy; może być aktywny albo nieaktywny. | samochód, auto, EV | Model Y, 18 kWh/100 km, odpowiednik 7 l/100 km PB95 | [App] src/main.py create_vehicle; [Biz] session-2026-10-04.md, Q-029; ENTITIES.md Pojazd | zatwierdzone (właściciel instalacji, 2026-10-04) |
| Pojazd nieaktywny | Pojazd wyłączony przez właściciela (np. po sprzedaży albo wymianie); nie ma pól EV w formularzu odczytu nowego miesiąca, a jego zapisane dane dalej liczą się do oszczędności i ROI. Auto, które w miesiącu stało, dalej jest aktywne. | - | sprzedane auto z danymi za 2025 | [Biz] board.json, qq041 (D-025), qq045 (D-028) | zatwierdzone (właściciel instalacji, 2026-10-04) |
| Stan licznika | Wskazanie licznika przebiegu pojazdu wpisywane w odczycie miesiąca; km miesiąca = stan licznika − poprzedni stan (poprzedni miesiąc albo przebieg startowy). | przebieg (z licznika) | 14 200 km za 2026.02 | [Biz] board.json, qq042 (D-026); RULES.md BR-011, BR-012 | zatwierdzone (właściciel instalacji, 2026-10-04) |
| Cena kWh | Cena zakupu 1 kWh z sieci, po której liczona jest oszczędność miesiąca; właściciel wpisuje ją w odczycie z faktury na nowy okres, a gdy pole jest puste, obowiązuje cena domyślna kWh z konfiguracji add-onu (BR-014). | cena prądu, cena domyślna (dla wartości z konfiguracji) | faktura: 1,05 zł/kWh; brak w odczycie → domyślna 0,75 zł | [Biz] session-2026-10-07.md, Q-047 (D-031); [App] src/main.py:26 | zatwierdzone (właściciel instalacji, 2026-10-08) |
| Śledzenie cen paliwa | Ustawienie właściciela, czy wpisuje ceny paliwa; włączone pokazuje pozycję „Ceny paliwa” w menu pod EV. Wybór przy pierwszym samochodzie, zmiana w każdej chwili. | - | śledzenie włączone → menu EV › Ceny paliwa | [Biz] board.json, nmuspw64n (D-007), qq040 (D-024) | zatwierdzone (właściciel instalacji, 2026-10-04) |

## Poza zakresem - nie buduj
(rownie wazne jak zakres)
- Strony /bateria i /ogrzewanie - makiety przyszłych funkcji (D-011).
- Uwierzytelnianie ponad istniejący opcjonalny Basic Auth (FV_AUTH_PASSWORD), dopóki tryb standalone nie jest wystawiony poza sieć domową (A-002, potwierdzone, session-2026-10-07.md).
- Automatyczne pobieranie cen RCE i cen paliwa - wpisywane ręcznie (D-004, D-006).
- Wariant procentowy w analizie wrażliwości - 7 stałych cen (D-012).
- Integracja z Tesla Fleet API - wycofana, API nie działało dobrze (D-020).
- Osobna kategoria kosztów eksploatacji - wszystkie wydatki na instalację to etapy inwestycji (D-017).
- Podsumowanie ROI dla Home Assistant (/api/summary) - usuwane, właściciel nie korzysta (D-030).
- Zestawianie kwoty faktury z policzoną oszczędnością - numer i kwota faktury służą tylko do odnalezienia faktury (D-033).

## Reguły biznesowe (globalne)
| ID | Reguła | Źródło | Założenia | Wymagania | Status |
|---|---|---|---|---|---|
| BR-001 | Jeżeli zaczyna się miesiąc startu cyklu rozliczeniowego (ustawienie użytkownika, domyślnie kwiecień) albo zmienia się model rozliczeń, to pula net-meteringu się zeruje; w pozostałych miesiącach niewykorzystana pula przechodzi na kolejny miesiąc. | [Biz] board.json, qq001, qq012 (D-002, D-003); [App] kod-v3.2.4-2026-09-27.md, Rozliczenie net-metering | - | R-002, R-003 | robocze |
| BR-002 | Jeżeli choć jeden wiersz importowanego pliku CSV ma zły format okresu (inny niż RRRR.MM), wartość ujemną albo energię oddaną większą niż produkcja, to żaden wiersz pliku nie jest zapisywany, a użytkownik dostaje raport: numer wiersza i powód. | [Biz] board.json, qq008; czat sesji 2026-10-03 (D-009) | - | R-004 | robocze |
| BR-003 | Jeżeli okres ma format inny niż RRRR.MM, któraś wartość jest ujemna albo energia oddana jest większa niż produkcja, to odczyt nie zostaje zapisany, a formularz pokazuje błąd. | [App] kod-v3.2.4-2026-09-27.md, Walidacja odczytów | A-004 | R-001 | robocze |
| BR-004 | Jeżeli okres jest rozliczany w net-meteringu, to oszczędność miesiąca = autokonsumpcja + część puli (oddane × współczynnik, domyślnie 0,80) zużyta na pobór. | [App] kod-v3.2.4-2026-09-27.md, Rozliczenie net-metering | A-005 | R-002 | robocze |
| BR-005 | Jeżeli okres jest rozliczany w net-billingu, to oszczędność miesiąca = autokonsumpcja × cena zakupu + oddane × cena RCE; cena sprzedaży wpisana w odczycie nadpisuje RCE. | [App] kod-v3.2.4-2026-09-27.md, calculations.py:94-159; [Biz] D-004 | A-006 | R-002, R-017 | robocze |
| BR-006 | Pozostało do zwrotu = suma etapów inwestycji − Σ oszczędności FV − Σ „Oszczędność EV z FV”; miesiące do zwrotu = pozostało / średnia miesięczna oszczędność. Etap inwestycji liczy się od miesiąca swojej daty (D-015). Etap z datą sprzed pierwszego odczytu liczy się od pierwszego miesiąca z odczytem (D-021). | [Dok] README.md, calc_roi; [Biz] D-008; [Biz] D-015; [Biz] D-018 (miesiące do zwrotu); [Biz] D-021 | A-007 | R-006, R-008 | robocze |
| BR-007 | Prognoza obejmuje 36 miesięcy, z degradacją paneli (domyślnie 0,6) i scenariuszami wzrostu cen 0/3/7/12%. Jeżeli zwrot przypada później niż 36 mies., to tabela scenariuszy podaje „zwrot za N mies.” dla każdego scenariusza, a dashboard liczbę miesięcy do zwrotu (D-013, D-019). | [App] src/main.py:995-1008, services/forecast.py; [Biz] D-013; [Biz] D-019 | A-008 | R-007, R-008 | robocze |
| BR-008 | Jeżeli przy dodawaniu pojazdu brak przebiegu startowego, to pojazd nie zostaje dodany. | [App] src/main.py:1573 | A-009 | R-009 | robocze |
| BR-009 | (techniczna) Jeżeli dane pobierane są z Home Assistant, to najpierw ze Statistics API, a gdy ich brak - z History API (ok. 10 dni wstecz); wartości w Wh są zamieniane na kWh. | [Dok] README.md, Home Assistant | A-010 | R-001, R-015 | robocze |
| BR-010 | Jeżeli koszt etapu inwestycji jest ujemny, to etap jest dofinansowaniem i zmniejsza łączną inwestycję; koszt może być zerowy, dodatni albo ujemny. | [Biz] session-2026-10-04.md, Q-021, Q-022 (D-014 zmieniona przez D-016) | - | R-005, R-006 | robocze |
| BR-011 | Jeżeli w odczycie miesiąca dla pojazdu jest stan licznika, to km miesiąca = stan licznika − poprzedni stan (poprzedni miesiąc z odczytem, a w pierwszym miesiącu przebieg startowy); km wpisane ręcznie mają pierwszeństwo. | [Biz] board.json, qq042 (D-026); [App] src/main.py:294-326 _inject_odometer_km | - | R-001, R-010 | robocze |
| BR-012 | Jeżeli właściciel zmienia przebieg startowy pojazdu, to przed zapisem aplikacja pyta, czy przesunąć wszystkie zapisane stany licznika o różnicę (nowa − stara wartość); tak - stany licznika przesunięte, km bez zmian; nie - zmienia się tylko przebieg startowy, a stany licznika niższe niż nowa wartość są usuwane (dane ładowania zostają). | [Biz] session-2026-10-04.md, D-027 | - | R-009 | robocze |
| BR-013 | Jeżeli liczony jest miesiąc, to jego model rozliczeń (net-metering albo net-billing) wynika z okresu rozliczeniowego obowiązującego 1. dnia tego miesiąca (okres startujący w środku miesiąca obowiązuje od następnego miesiąca). Nakładające się okresy - Q-055 (zaparkowane; dziś wygrywa późniejszy start). | [Biz] session-2026-10-07.md, Q-048 (D-032); [App] src/services/calculations.py:57 _get_billing_model | - | R-017, R-002 | robocze |
| BR-014 | Jeżeli odczyt miesiąca nie ma ceny kWh, to oszczędność liczona jest po cenie domyślnej kWh z konfiguracji add-onu (ustawia właściciel); cena z faktury wpisana w odczycie ma pierwszeństwo. | [Biz] session-2026-10-07.md, Q-047 (D-031); [App] src/main.py:26 _default_price | - | R-001, R-002, R-006 | robocze |

## Zasady pracy
- Każda zmiana kodu wskazuje R-xxx i AC-xxx-n, które realizuje; test nazywa się od AC (np. `test_AC_006_3_...`).
- TDD: test z AC napisany przed kodem; nie mockuj realnych API (HA).
- Rozjazd kodu ze specyfikacją = zmiana PRD (przez człowieka) albo kodu - nigdy cicha zmiana zachowania.
- Punkt odniesienia: v3.4.0 (UAT zaliczony 2026-10-04). Zadania typu Z/B zmieniają działanie v3.4.0; typ W opisuje działanie obecne (testy regresji z AC).
- Dane wpisywane ręcznie mają źródła poza aplikacją (02-domain/SYSTEMS.md S-003..S-009); aplikacja nie pobiera ich automatycznie.
