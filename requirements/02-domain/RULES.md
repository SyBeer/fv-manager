# Reguly biznesowe

Forma: "Jezeli <warunek>, to <skutek>". Kazda regula ma zrodlo.
Status: robocze | zakwestionowane (Q-xxx) | zatwierdzone

Kolumna `Wymagania` jest sciezka kaskady: gdy regula zostanie zakwestionowana,
wszystkie wymienione tu `R` ida do sekcji "Do przegladu" w PRD.

| ID | Regula | Zrodlo | Zalozenia | Wymagania | Status |
|----|--------|--------|-----------|-----------|--------|
| BR-001 | Jeżeli zaczyna się miesiąc startu cyklu rozliczeniowego (ustawienie użytkownika, domyślnie kwiecień) albo zmienia się model rozliczeń, to pula net-meteringu się zeruje; w pozostałych miesiącach niewykorzystana pula przechodzi na kolejny miesiąc. | [Biz] board.json, qq001, qq012 (D-002, D-003); [App] kod-v3.2.4-2026-09-27.md, Rozliczenie net-metering | - | (kandydat: ustawienie miesiąca startu cyklu) | robocze |
| BR-002 | Jeżeli choć jeden wiersz importowanego pliku CSV ma zły format okresu (inny niż RRRR.MM), wartość ujemną albo energię oddaną większą niż produkcja, to żaden wiersz pliku nie jest zapisywany, a użytkownik dostaje raport: numer wiersza i powód. | [Biz] board.json, qq008; czat sesji 2026-10-03 (D-009) | - | (kandydat: import all-or-nothing z raportem) | robocze |
