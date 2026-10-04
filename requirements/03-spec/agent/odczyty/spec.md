<!-- GENEROWANE z PRD.md 2026-10-04 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Odczyty miesięczne i import

### R-001 Wpisanie odczytu miesiąca
Opis:              Właściciel instalacji wpisuje odczyt miesiąca (produkcja, oddane, pobrane, cena kWh, faktura, dane EV per pojazd) ręcznie albo pobiera produkcję i dane sieci z Home Assistant za wybrany miesiąc. Błędny odczyt nie zostaje zapisany. Dane EV z Tesla Fleet API poza tym R (Q-016).
Zrodlo:            [App] kod-v3.2.4-2026-09-27.md, Walidacja odczytów; [Biz] session-2026-10-04.md, Q-024, Q-030
Zalozenia:         A-004, A-010
Reguly:            BR-003, BR-009
Status:            zatwierdzone (właściciel instalacji, 2026-10-04)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-001-1: Given poprawne dane za 2026.09 (produkcja ≥ oddane, wszystkie wartości ≥ 0), When właściciel zapisuje odczyt, Then odczyt jest na liście odczytów.
- AC-001-2: Given okres „2026-9”, When właściciel zapisuje odczyt, Then odczyt nie zostaje zapisany, a formularz pokazuje błąd okresu.
- AC-001-3: Given oddane 500 kWh i produkcja 400 kWh, When właściciel zapisuje odczyt, Then odczyt nie zostaje zapisany, a formularz pokazuje błąd.
- AC-001-4: Given skonfigurowane encje HA, When właściciel wybiera miesiąc i klika „pobierz z HA”, Then pola produkcja, oddane i pobrane wypełniają się bez ręcznego wpisywania.

### R-004 Import odczytów z CSV - cały plik albo nic
Opis:              Właściciel instalacji importuje odczyty z pliku CSV (separator „;”, polskie nagłówki). Jeśli choć jeden wiersz jest błędny, nie zostaje zapisany żaden, a raport podaje numer wiersza i powód. Stan docelowy. Postępowanie z okresem, który już istnieje - Q-017.
Zrodlo:            [Biz] board.json, qq008 (D-009)
Zalozenia:         -
Reguly:            BR-002
Status:            zatwierdzone (właściciel instalacji, 2026-10-04)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-004-1: Given plik z 10 poprawnymi wierszami, When właściciel importuje plik, Then zapisanych zostaje 10 odczytów.
- AC-004-2: Given plik, w którym wiersz 4 ma wartość ujemną, When właściciel importuje plik, Then nie zostaje zapisany żaden wiersz, a raport pokazuje „wiersz 4” i powód.

### R-012 Lista i edycja odczytów
Opis:              Lista odczytów pokazuje dla każdego miesiąca produkcję, autokonsumpcję, oddane, pobrane, zużycie i oszczędność. Przy edycji odczytu właściciel instalacji widzi ROI przed i po zmianie.
Zrodlo:            [Dok] README.md, Odczyty (/odczyty), /api/roi-preview
Zalozenia:         A-012
Reguly:            -
Status:            zatwierdzone (właściciel instalacji, 2026-10-04)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-012-1: Given 3 zapisane odczyty, When właściciel otwiera /odczyty, Then każdy wiersz pokazuje produkcję, autokonsumpcję, oddane, pobrane, zużycie i oszczędność.
- AC-012-2: Given zapisany odczyt, When właściciel zmienia produkcję w formularzu edycji, Then przed zapisem widzi ROI przed i po zmianie.
