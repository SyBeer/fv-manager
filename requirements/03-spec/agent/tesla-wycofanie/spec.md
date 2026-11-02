<!-- GENEROWANE z PRD.md 2026-10-08 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Wycofanie Tesla Fleet API

### R-018 Wycofanie integracji z Tesla Fleet API
Opis:              Integracja z Tesla Fleet API zostaje wycofana: pozostałości (kolumny tesla_* w bazie, wzmianki w ev.html, opis w README) są usuwane, a CHANGELOG aplikacji opisuje wycofanie i powód. Dane właściciela zostają nienaruszone.
Zrodlo:            [Biz] board.json, h01 (D-020); [App] src/utils/db.py:200, templates/ev.html; [Dok] README.md, Tesla Fleet API
Zalozenia:         -
Reguly:            -
Status:            zatwierdzone (właściciel instalacji, 2026-10-04)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-018-1: Given kod aplikacji, When ktoś szuka „tesla” w src/ i templates/, Then nie ma odwołań poza migracją usuwającą kolumny.
- AC-018-2: Given README i CHANGELOG, When właściciel czyta opis integracji, Then nie ma w nim Tesla Fleet API, a CHANGELOG opisuje wycofanie i jego powód.
- AC-018-3: Given baza z wypełnionymi polami Tesli, When aplikacja się uruchamia, Then odczyty, pojazdy i pozostałe dane właściciela zostają nienaruszone.
