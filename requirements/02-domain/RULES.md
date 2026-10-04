# Reguly biznesowe

Forma: "Jezeli <warunek>, to <skutek>". Kazda regula ma zrodlo.
Status: robocze | zakwestionowane (Q-xxx) | zatwierdzone

Kolumna `Wymagania` jest sciezka kaskady: gdy regula zostanie zakwestionowana,
wszystkie wymienione tu `R` ida do sekcji "Do przegladu" w PRD.

| ID | Regula | Zrodlo | Zalozenia | Wymagania | Status |
|----|--------|--------|-----------|-----------|--------|
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
