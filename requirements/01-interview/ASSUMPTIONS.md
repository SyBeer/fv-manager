# Zalozenia

Statusy: niepotwierdzone | potwierdzone | obalone
Zrodlo wg hierarchii: [Biz] biznes > [App] prototyp/system > [Dok] dokument > [AI] interpretacja
Zapis zrodla: `[Biz]/[App]/[Dok]/[AI] <plik z INDEX.md>[, sekcja/wiersz]`

Zgodnosc dwoch zrodel `[Dok]` nie jest potwierdzeniem - dwa dokumenty spisane z tej samej
aplikacji powtarzaja ten sam blad. Potwierdza tylko `[Biz]`.

| ID | Zalozenie | Status | Zrodlo | Wymagania zalezne |
|----|-----------|--------|--------|-------------------|
| A-001 | Net-billing obejmuje instalacje przyłączone od 1.04.2022; rozliczenia net-billing od 1.07.2022; od 1.07.2024 obowiązują godzinowe ceny RCE (stąd „2024” w review). | niepotwierdzone | [AI] wiedza ogólna; kontekst: metodologia.html, review-2026-05-12.md | tekst metodologii (D-005) |
| A-002 | Właściciel używa aplikacji wyłącznie jako HA Add-on; trybu standalone nie wystawia poza sieć domową. Istniejący opcjonalny Basic Auth (FV_AUTH_PASSWORD) wystarcza; dalsze uwierzytelnianie poza zakresem, dopóki standalone nie jest wystawiony poza sieć domową. | niepotwierdzone | [AI] interpretacja odpowiedzi „W ogóle - nie wiedziałem że tak mogę” (board.json, qq009, warsztat 2026-10-03) | PRD §4 |
| A-003 | Aplikacja służy do podglądu: raz w miesiącu właściciel wpisuje odczyty za miniony miesiąc i sprawdza ROI oraz oszczędności na samochodach; wynik nie wywołuje dalszych działań. | niepotwierdzone | [AI] interpretacja odpowiedzi na Q-015 (sesja live 2026-10-03: „dodałem zapisy za wrzesień”, „ROI, oszczędności na samochodach”, „nic”) | PRD §1 Cel, §3 Zakres |
