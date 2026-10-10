<!-- GENEROWANE z PRD.md 2026-10-08 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Rozliczenia i ustawienia

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
