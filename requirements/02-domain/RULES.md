# Reguly biznesowe

Forma: "Jezeli <warunek>, to <skutek>". Kazda regula ma zrodlo.
Status: robocze | zakwestionowane (Q-xxx) | zatwierdzone

Kolumna `Wymagania` jest sciezka kaskady: gdy regula zostanie zakwestionowana,
wszystkie wymienione tu `R` ida do sekcji "Do przegladu" w PRD.

| ID | Regula | Zrodlo | Zalozenia | Wymagania | Status |
|----|--------|--------|-----------|-----------|--------|
| BR-001 | Jeżeli zaczyna się miesiąc startu cyklu rozliczeniowego (ustawienie użytkownika, domyślnie kwiecień) albo zmienia się model rozliczeń, to pula net-meteringu się zeruje; w pozostałych miesiącach niewykorzystana pula przechodzi na kolejny miesiąc. | [Biz] board.json, qq001, qq012 (D-002, D-003); [App] kod-v3.2.4-2026-09-27.md, Rozliczenie net-metering | - | (kandydat: ustawienie miesiąca startu cyklu) | robocze |
| BR-002 | Jeżeli choć jeden wiersz importowanego pliku CSV ma zły format okresu (inny niż RRRR.MM), wartość ujemną albo energię oddaną większą niż produkcja, to żaden wiersz pliku nie jest zapisywany, a użytkownik dostaje raport: numer wiersza i powód. | [Biz] board.json, qq008; czat sesji 2026-10-03 (D-009) | - | (kandydat: import all-or-nothing z raportem) | robocze |
| BR-003 | Jeżeli okres ma format inny niż RRRR.MM, któraś wartość jest ujemna albo energia oddana jest większa niż produkcja, to odczyt nie zostaje zapisany, a formularz pokazuje błąd. | [App] kod-v3.2.4-2026-09-27.md, Walidacja odczytów | A-004 | (kandydat: formularz odczytu) | robocze |
| BR-004 | Jeżeli okres jest rozliczany w net-meteringu, to oszczędność miesiąca = autokonsumpcja + część puli (oddane × współczynnik, domyślnie 0,80) zużyta na pobór. | [App] kod-v3.2.4-2026-09-27.md, Rozliczenie net-metering | A-005 | (kandydat: rozliczenie miesiąca) | robocze |
| BR-005 | Jeżeli okres jest rozliczany w net-billingu, to oszczędność miesiąca = autokonsumpcja × cena zakupu + oddane × cena RCE; cena sprzedaży wpisana w odczycie nadpisuje RCE. | [App] kod-v3.2.4-2026-09-27.md, calculations.py:94-159; [Biz] D-004 | A-006 | (kandydat: rozliczenie miesiąca) | robocze |
| BR-006 | Pozostało do zwrotu = suma etapów inwestycji − Σ oszczędności FV − Σ „Oszczędność EV z FV”; miesiące do zwrotu = pozostało / średnia miesięczna oszczędność. | [Dok] README.md, calc_roi; [Biz] D-008 | A-007 | (kandydat: ROI) | robocze |
| BR-007 | Prognoza obejmuje 36 miesięcy, z degradacją paneli (domyślnie 0,6) i scenariuszami wzrostu cen 0/3/7/12%. Jeżeli zwrot przypada później niż 36 mies., to aplikacja podaje liczbę miesięcy do zwrotu słownie (D-013, docelowo; dziś nie podaje). | [App] src/main.py:995-1008, services/forecast.py; [Biz] D-013 | A-008 | (kandydat: prognoza ROI) | robocze |
| BR-008 | Jeżeli przy dodawaniu pojazdu brak przebiegu startowego, to pojazd nie zostaje dodany. | [App] src/main.py:1573 | A-009 | (kandydat: dodanie pojazdu) | robocze |
| BR-009 | (techniczna) Jeżeli dane pobierane są z Home Assistant, to najpierw ze Statistics API, a gdy ich brak - z History API (ok. 10 dni wstecz); wartości w Wh są zamieniane na kWh. | [Dok] README.md, Home Assistant | A-010 | (kandydat: import z HA) | robocze |
