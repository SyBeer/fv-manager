<!-- GENEROWANE z PRD.md 2026-10-08 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Integracja z Home Assistant

### R-015 Integracja z Home Assistant
Opis:              Właściciel instalacji wpisuje encje HA (produkcja PV, pobór z sieci, oddanie do sieci) i testuje połączenie. Podsumowanie ROI dla HA (/api/summary) jest usuwane - właściciel z niego nie korzysta (D-030).
Zrodlo:            [Dok] README.md, Home Assistant, /api/ha-test, API JSON; [Biz] session-2026-10-04.md, Q-030; [Biz] session-2026-10-05.md, propozycja C (D-030)
Zalozenia:         A-010, A-013
Reguly:            BR-009
Status:            zatwierdzone (właściciel instalacji, 2026-10-08)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-015-1: Given wpisane encje produkcji, poboru i oddania, When właściciel klika „Testuj połączenie”, Then widzi „OK — RRRR-MM: N kWh (okres: RRRR-MM)” dla bieżącego miesiąca albo komunikat błędu.
- AC-015-2: Given aplikacja po zmianie, When HA odpytuje /api/summary, Then aplikacja odpowiada „nie znaleziono” (404), a test połączenia i pobieranie liczników działają bez zmian (D-030).

### R-020 Kontrakt: liczniki energii z Home Assistant (wejście)
Opis:              Aplikacja przyjmuje z Home Assistant wartości miesiąca dla Odczytu miesiąca: produkcję PV, pobór z sieci i oddanie do sieci, w kWh. Pobranie na żądanie właściciela przy wpisie odczytu za wybrany miesiąc. Gdy HA nie ma danych, właściciel wpisuje wartości ręcznie. Schemat techniczny (encje, API HA) - w budowie, BR-009.
Zrodlo:            [Biz] session-2026-10-04.md, Q-030 (A-010); [Biz] session-2026-10-05.md, propozycja A; [App] src/main.py:2155-2190
Zalozenia:         A-010, A-015, A-016 (potwierdzone)
Reguly:            BR-009
Rodzaj:            kontrakt - wejscie
System:            S-002 (Home Assistant)
Status:            zatwierdzone (właściciel instalacji, 2026-10-08)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-020-1: Given encje produkcji, poboru i oddania są skonfigurowane, a HA ma dane za miesiąc 2026.09, When właściciel w formularzu odczytu za 2026.09 pobiera dane z HA, Then pola produkcja, pobrane i oddane mają wartości za 2026.09 w kWh i przed zapisem można je zmienić.
- AC-020-2: Given zapisany odczyt za 2026.08 i zmienione później dane za 2026.08 w HA, When właściciel otwiera listę odczytów, Then wartości odczytu 2026.08 są takie jak przy zapisie (pobranie tylko na żądanie przy wpisie odczytu).
- AC-020-3: Given HA nie zwraca danych za 2026.09, When właściciel pobiera dane z HA, Then widzi komunikat „Brak danych dla <encja> za 2026-09”, pola zostają puste do wpisania ręcznie, a odczyt z ręcznymi wartościami da się zapisać.
