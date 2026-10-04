# Zalozenia

Statusy: niepotwierdzone | potwierdzone | obalone
Zrodlo wg hierarchii: [Biz] biznes > [App] prototyp/system > [Dok] dokument > [AI] interpretacja
Zapis zrodla: `[Biz]/[App]/[Dok]/[AI] <plik z INDEX.md>[, sekcja/wiersz]`

Zgodnosc dwoch zrodel `[Dok]` nie jest potwierdzeniem - dwa dokumenty spisane z tej samej
aplikacji powtarzaja ten sam blad. Potwierdza tylko `[Biz]`.

| ID | Zalozenie | Status | Zrodlo | Wymagania zalezne |
|----|-----------|--------|--------|-------------------|
| A-001 | Net-billing obejmuje instalacje przyłączone od 1.04.2022; rozliczenia net-billing od 1.07.2022; od 1.07.2024 obowiązują godzinowe ceny RCE (stąd „2024” w review). | niepotwierdzone | [AI] wiedza ogólna; kontekst: metodologia.html, review-2026-05-12.md | tekst metodologii (D-005), R-016 |
| A-002 | Właściciel używa aplikacji wyłącznie jako HA Add-on; trybu standalone nie wystawia poza sieć domową. Istniejący opcjonalny Basic Auth (FV_AUTH_PASSWORD) wystarcza; dalsze uwierzytelnianie poza zakresem, dopóki standalone nie jest wystawiony poza sieć domową. | niepotwierdzone | [AI] interpretacja odpowiedzi „W ogóle - nie wiedziałem że tak mogę” (board.json, qq009, warsztat 2026-10-03) | PRD §4 |
| A-003 | Aplikacja służy do podglądu: raz w miesiącu właściciel wpisuje odczyty za miniony miesiąc i sprawdza ROI oraz oszczędności na samochodach; wynik nie wywołuje dalszych działań. | niepotwierdzone | [AI] interpretacja odpowiedzi na Q-015 (sesja live 2026-10-03: „dodałem zapisy za wrzesień”, „ROI, oszczędności na samochodach”, „nic”) | PRD §1 Cel, §3 Zakres |
| A-004 | BR-003 działa tak, jak w aplikacji v3.2.4: błędny odczyt nie zostaje zapisany, właściciel poprawia dane i zapisuje ponownie. | potwierdzone | [Biz] session-2026-10-04.md, Q-024 (właściciel instalacji; potwierdzenie zasady, błędu dotąd nie widział); [App] kod-v3.2.4-2026-09-27.md, Walidacja odczytów | R-001 |
| A-005 | BR-004 działa tak, jak w aplikacji v3.2.4. Umowa właściciela: energia oddana do sieci wraca do odbioru w ilości 0,8 × oddane kWh, więc domyślny współczynnik 0,80 jest zgodny z umową. | potwierdzone | [Biz] session-2026-10-04.md, Q-025 (właściciel instalacji); [App] kod-v3.2.4-2026-09-27.md, Rozliczenie net-metering | R-002 |
| A-006 | BR-005 działa tak, jak w aplikacji v3.2.4, i właściciel instalacji tego chce. | niepotwierdzone | [App] kod-v3.2.4-2026-09-27.md, calculations.py:94-159 | R-002 |
| A-007 | Pozostało do zwrotu = inwestycje − oszczędności z domu (FV) − oszczędności EV; część EV to wyłącznie ładowanie domowe („Oszczędność EV z FV”, D-008). Część BR-006 o liczbie miesięcy do zwrotu rozstrzygnięta w D-018. | potwierdzone | [Biz] session-2026-10-04.md, Q-027 (właściciel instalacji); [Dok] README.md, calc_roi | R-006 |
| A-008 | BR-007 działa tak, jak w aplikacji v3.2.4, i właściciel instalacji tego chce. | niepotwierdzone | [App] src/main.py:995-1008, services/forecast.py | R-007 |
| A-009 | BR-008 działa tak, jak w aplikacji v3.2.4: bez przebiegu startowego nie można zarejestrować samochodu. Właściciel odczytuje przebieg z licznika w samochodzie. | potwierdzone | [Biz] session-2026-10-04.md, Q-029 (właściciel instalacji); [App] src/main.py:1573 | R-009 |
| A-010 | Po wybraniu miesiąca dane z Home Assistant wczytują się automatycznie, bez ręcznych poprawek. Sposób pobierania z BR-009 (najpierw Statistics, potem History API ok. 10 dni, Wh → kWh) nie jest objęty potwierdzeniem - stoi na [Dok]. | potwierdzone | [Biz] session-2026-10-04.md, Q-030 (właściciel instalacji); [Dok] README.md, Home Assistant | R-001, R-015 |
| A-011 | Ekran /roi i dashboard mają zawartość jak w aplikacji v3.2.4 (karty ROI, wykres skumulowanych oszczędności vs inwestycja, tabela wrażliwości, prognoza; baner ROI + 12 ostatnich miesięcy). | niepotwierdzone | [Dok] README.md, ROI (/roi), Dashboard (/) | R-008 |
| A-012 | Lista odczytów i edycja z podglądem ROI przed/po zmianie działają jak w aplikacji v3.2.4. | niepotwierdzone | [Dok] README.md, Odczyty (/odczyty), /api/roi-preview | R-012 |
| A-013 | Konfiguracja encji HA, test połączenia i sensor podsumowania ROI (/api/summary) działają jak w aplikacji v3.2.4/3.2.5. | niepotwierdzone | [Dok] README.md, Home Assistant, /api/ha-test, API JSON | R-015 |
