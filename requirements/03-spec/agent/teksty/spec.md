<!-- GENEROWANE z PRD.md 2026-10-04 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Poprawki tekstów

### R-016 Poprawki tekstów
Opis:              Teksty metodologia.html, README i podtytuł tabeli wrażliwości na /roi zgodne z decyzjami: pula kumulowana w cyklu, RCE i ceny paliwa wpisywane ręcznie, bez dat ustawowych net-billingu (model z okresów rozliczeniowych, daty z umowy - D-022), 7 stałych cen, CSV z separatorem „;” i polskimi nagłówkami.
Zrodlo:            [Biz] board.json, qq001, qq002, qq003, qq004, qq005, qq008 (D-002, D-004, D-005, D-006, D-012, D-009); [Biz] session-2026-10-04.md, Q-037 (D-022)
Zalozenia:         -
Reguly:            -
Status:            zatwierdzone (właściciel instalacji, 2026-10-04)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-016-1: Given metodologia.html, When właściciel czyta opis cen RCE i cen paliwa, Then tekst mówi, że wpisuje się je ręcznie.
- AC-016-2: Given metodologia.html i README, When właściciel czyta opis puli, Then tekst mówi, że pula przechodzi z miesiąca na miesiąc i zeruje się w miesiącu startu cyklu.
- AC-016-3: Given /roi i metodologia.html, When właściciel czyta opis analizy wrażliwości, Then podtytuł na /roi pokazuje współczynnik z ustawień zamiast „×0.8”, a metodologia opisuje 7 stałych cen zamiast „wzrost o 20%”.
- AC-016-4: Given README, When właściciel czyta przykład CSV, Then przykład ma separator „;” i polskie nagłówki.
- AC-016-5: Given metodologia.html, When właściciel czyta opis net-billingu, Then tekst nie podaje dat ustawowych i mówi, że model rozliczeń wynika z okresów rozliczeniowych ustawionych przez użytkownika, a daty zależą od umowy z operatorem.
