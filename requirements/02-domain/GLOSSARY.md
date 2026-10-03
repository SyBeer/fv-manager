# Slownik pojec

Jedno pojecie = jedna definicja. Synonimy uzywane przez biznes wpisuj, nie usuwaj.
Jedno pojecie = jeden zbior rekordow: jesli dwa zrodla nazywaja ta sama nazwa inny zbior
obiektow, to homonim do rozbicia na dwa hasla albo sprzecznosc - nie jedno haslo.
Status: robocze | zakwestionowane (Q-xxx) | zatwierdzone (bramka przed /sdd:spec)

Zrodlo: `[Biz]/[App]/[Dok]/[AI] <plik z INDEX.md>[, sekcja/wiersz]` - nazwa pliku obowiazkowa,
bo na niej stoi kontrola pokrycia zrodel w /sdd:validate.

| Pojecie | Definicja | Synonimy | Przyklad | Zrodlo | Status |
|---------|-----------|----------|----------|--------|--------|
| Pula net-meteringu | Energia oddana do sieci × współczynnik (domyślnie 0,80, ustawienie net_metering_ratio), do odebrania w kolejnych miesiącach; przechodzi z miesiąca na miesiąc i zeruje się w miesiącu startu cyklu rozliczeniowego (BR-001). | pula, carry-over | oddane 100 kWh w maju → 80 kWh do odebrania do końca cyklu | [Biz] board.json, qq001 (D-002); [App] kod-v3.2.4-2026-09-27.md, Rozliczenie net-metering | robocze |
| Cykl rozliczeniowy | Roczny okres, po którym pula net-meteringu się zeruje; miesiąc startu ustawia użytkownik (domyślnie kwiecień). | rok rozliczeniowy | cykl kwiecień–marzec | [Biz] board.json, qq012 (D-003) | robocze |
| Okres rozliczeniowy | Przedział czasu od daty startu, dla którego użytkownik ustawia model rozliczeń (net-metering albo net-billing). | billing period | od 2021-06 net-metering | [Biz] board.json, qq002 (D-004); [App] kod-v3.2.4-2026-09-27.md, Net-billing i RCE | robocze |
| Net-metering | Model rozliczeń, w którym oddana energia trafia do puli net-meteringu i jest odbierana bez opłaty za energię. | stary system opustów | - | [Biz] board.json, qq002 (D-004) | robocze |
| Net-billing | Model rozliczeń, w którym oddana energia jest wyceniana po cenie RCE, a oszczędność = autokonsumpcja × cena zakupu + oddane × cena RCE. Model wynika z okresu rozliczeniowego, nie z daty ustawowej (D-005). | nowy system | - | [Biz] board.json, qq002, qq003 (D-004, D-005); [App] kod-v3.2.4-2026-09-27.md, Net-billing i RCE | robocze |
| Cena RCE | Rynkowa cena energii, po której wyceniana jest energia oddana w net-billingu; wpisywana ręcznie przez użytkownika (data, cena, źródło). Odczyt może mieć własną cenę sprzedaży, która ją nadpisuje. | RCE, RCEm | - | [Biz] board.json, qq002 (D-004); [App] kod-v3.2.4-2026-09-27.md, Net-billing i RCE | robocze |
| Cena paliwa | Cena paliwa wpisywana ręcznie przez użytkownika (data, cena, typ, źródło), używana do porównania kosztu EV z autem spalinowym. | - | - | [Biz] board.json, qq005 (D-006) | robocze |
| Oszczędność EV z FV | Oszczędność z ładowania samochodu w domu energią z instalacji; jedyna część oszczędności EV wchodząca do ROI. | - | - | [Biz] board.json, qq006 (D-008); [Dok] README.md, Ładowanie domowe vs publiczne | robocze |
| Oszczędność EV vs paliwo | Oszczędność z ładowania domowego i publicznego w porównaniu z kosztem paliwa; pokazywana na kartach /ev, nie wchodzi do ROI. | - | - | [Biz] board.json, qq006 (D-008); [Dok] README.md, Widoki /ev | robocze |
