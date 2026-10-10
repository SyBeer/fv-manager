<!-- GENEROWANE z PRD.md 2026-10-08 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Odczyty miesięczne i import

### R-001 Wpisanie odczytu miesiąca
Opis:              Właściciel instalacji wpisuje odczyt miesiąca (produkcja, oddane, pobrane, cena kWh, faktura, dane EV per pojazd) ręcznie albo pobiera produkcję i dane sieci z Home Assistant za wybrany miesiąc. Błędny odczyt nie zostaje zapisany. Integracja z Tesla Fleet API wycofana (D-020, R-018). Cenę kWh właściciel wpisuje z faktury na nowy okres; puste pole = cena domyślna kWh z konfiguracji add-onu (D-031, BR-014). Numer i kwota brutto faktury służą do odnalezienia faktury i nie wchodzą do obliczeń (D-033). Przejechane km właściciel przepisuje z aplikacji Tesla (S-007), kWh ładowania domowego - z domowych liczników energii (S-009), kWh i koszt ładowania publicznego - z aplikacji operatora ładowarki (S-008); brakujące dane ładowania publicznego uzupełnia później edycją odczytu.
Zrodlo:            [App] kod-v3.2.4-2026-09-27.md, Walidacja odczytów; [Biz] session-2026-10-04.md, Q-024, Q-030; [Biz] board.json, qq042 (D-026); [Biz] session-2026-10-07.md, Q-047, Q-049, Q-052, Q-053; [Biz] session-2026-10-08.md, Q-056, Q-057
Zalozenia:         A-004, A-010
Reguly:            BR-003, BR-009, BR-011, BR-014
Status:            zatwierdzone (właściciel instalacji, 2026-10-08)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-001-1: Given poprawne dane za 2026.09 (produkcja ≥ oddane, wszystkie wartości ≥ 0), When właściciel zapisuje odczyt, Then odczyt jest na liście odczytów.
- AC-001-2: Given okres „2026-9”, When właściciel zapisuje odczyt, Then odczyt nie zostaje zapisany, a formularz pokazuje błąd okresu.
- AC-001-3: Given oddane 500 kWh i produkcja 400 kWh, When właściciel zapisuje odczyt, Then odczyt nie zostaje zapisany, a formularz pokazuje błąd.
- AC-001-4: Given skonfigurowane encje HA, When właściciel wybiera miesiąc i klika „pobierz z HA”, Then pola produkcja, oddane i pobrane wypełniają się bez ręcznego wpisywania.
- AC-001-5: Given pojazd z przebiegiem startowym 12 000 km, When właściciel wpisuje stan licznika 13 000 za pierwszy miesiąc i 14 200 za kolejny, Then km miesięcy wynoszą 1 000 i 1 200 (BR-011).
- AC-001-6: Given zapisany odczyt z numerem faktury i kwotą brutto 350 zł, When właściciel zmienia kwotę faktury na 400 zł, Then oszczędność PV miesiąca i pozostało do zwrotu się nie zmieniają (D-033).

### R-004 Import odczytów z CSV - cały plik albo nic
Opis:              Właściciel instalacji importuje odczyty z pliku CSV (separator „;”, polskie nagłówki). Jeśli choć jeden wiersz jest błędny, nie zostaje zapisany żaden, a raport podaje numer wiersza i powód (działa w v3.4.0, src/main.py:1191). Okres, który już istnieje, import pomija - Q-017 (zaparkowane).
Zrodlo:            [Biz] board.json, qq008 (D-009)
Zalozenia:         -
Reguly:            BR-002
Rodzaj:            kontrakt - wejscie
System:            S-006 (Plik CSV)
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
