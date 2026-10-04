<!-- GENEROWANE z PRD.md 2026-10-04 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Eksport, kopia, czyszczenie

### R-013 Eksport i kopia danych
Opis:              Właściciel instalacji eksportuje odczyty do CSV, pobiera pełną kopię danych (JSON) i przywraca dane z kopii. Przywrócenie nadpisuje dane, ustawienia zostają.
Zrodlo:            [Dok] README.md, /odczyty/export.csv; [App] src/main.py:1161; [App] kod-v3.2.4-2026-09-27.md, Czyszczenie bazy
Zalozenia:         -
Reguly:            -
Status:            zatwierdzone (właściciel instalacji, 2026-10-04)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-013-1: Given 12 odczytów, When właściciel eksportuje odczyty do CSV, Then plik ma 12 wierszy danych.
- AC-013-2: Given dane w aplikacji, When właściciel pobiera pełną kopię, Then dostaje plik JSON.
- AC-013-3: Given kopia JSON z 5 odczytami, aplikacja z 12 odczytami i degradacja ustawiona na 0,8, When właściciel przywraca dane z kopii, Then aplikacja ma 5 odczytów, a degradacja nadal wynosi 0,8.

### R-014 Wyczyść bazę
Opis:              „Wyczyść bazę” usuwa wszystkie dane (odczyty, etapy inwestycji, pojazdy i dane EV, ceny paliwa, okresy rozliczeniowe, ceny RCE); ustawienia zostają. Tekst przed potwierdzeniem wymienia wszystko, co znika, i zaleca kopię. Stan docelowy - dziś kod usuwa tylko odczyty.
Zrodlo:            [Biz] board.json, qq010 (D-010)
Zalozenia:         -
Reguly:            -
Status:            zatwierdzone (właściciel instalacji, 2026-10-04)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-014-1: Given odczyty, etapy inwestycji, pojazdy, ceny paliwa, okresy rozliczeniowe i ceny RCE, When właściciel potwierdza „Wyczyść bazę”, Then wszystkie te dane znikają, a ustawienia zostają.
- AC-014-2: Given ekran przed potwierdzeniem, When właściciel go czyta, Then tekst wymienia wszystkie usuwane rodzaje danych i zaleca pobranie kopii (/backup/full).
