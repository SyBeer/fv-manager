# Changelog

## [1.7.0] — 2026-04-19

### Zmieniono
- EV savings (oszczędności vs paliwo) wliczane do ROI — dla każdego miesiąca z ev_kwh aplikacja oblicza ile zaoszczędzono vs odpowiednik benzynowy i dodaje do łącznych oszczędności
- ROI pokazuje breakdown: ☀️ FV + 🚗 EV osobno
- Wykres ROI ma dodatkową linię przerywana "z czego EV" gdy są dane EV

## [1.6.0] — 2026-04-19

### Dodano
- Edycja istniejących inwestycji (przycisk ✏️ w tabeli)
- Flatpickr jako picker daty — dropdown roku/miesiąca, obsługa wpisywania ręcznego

### Naprawiono
- Czyszczenie bazy usuwa tylko odczyty (nie inwestycje ani ceny paliw)

## [1.5.0] — 2026-04-19

### Zmieniono
- Usunięto import z Excela — jedyną metodą importu jest teraz CSV (separator `;`, kodowanie UTF-8)
- Strona importu zawiera opis struktury pliku CSV z przykładem i wymaganymi nagłówkami

## [1.4.0] — 2026-04-19

### Dodano
- Import z CSV — eksportowany plik można wczytać z powrotem bez żadnych modyfikacji
- Pobieranie szablonu CSV z nagłówkami (`/import/template.csv`)
- Przycisk wyczyszczenia całej bazy danych (Niebezpieczna strefa na stronie Import)

## [1.3.3] — 2026-04-19

### Naprawiono
- `sqlite3.OperationalError: table readings has no column named ev_kwh` — dodano migrację ALTER TABLE przy starcie

## [1.3.2] — 2026-04-19

### Naprawiono
- 404 po zapisie/usunięciu — wszystkie RedirectResponse używają teraz ingress root_path

## [1.3.1] — 2026-04-19

### Zmieniono
- Usunięto kolumnę "Wartość produkcji"
- Cena kWh wyświetlana w każdym wierszu — z faktury lub domyślna

## [1.3.0] — 2026-04-19

### Dodano
- Eksport odczytów do CSV (`/odczyty/export.csv`) — separator `;`, wszystkie kolumny z obliczeniami

## [1.2.1] — 2026-04-19

### Naprawiono
- Oszczędności i wartość produkcji puste gdy brak ceny z faktury — teraz używa domyślnej ceny z konfiguracji

## [1.2.0] — 2026-04-19

### Dodano
- Kolumna "Wartość produkcji" w tabeli odczytów — `produkcja × cena_kWh` [zł]

## [1.1.1] — 2026-04-19

### Naprawiono
- TypeError w `_t` helper — `request` przekazywany jako keyword arg do `TemplateResponse`

## [1.1.0] — 2026-04-19

### Naprawiono
- Wszystkie linki i formularze używają teraz `root_path` — poprawne działanie przez HA ingress proxy
- Nawigacja sidebar działa poprawnie w HA (bez błędów 404 przy klikaniu menu)

## [1.0.3] — 2026-04-19

### Naprawiono
- Przeniesienie plików add-ona na root repo — fix COPY paths w Dockerfile
- Dodanie domyślnej wartości BUILD_FROM w Dockerfile
- Dodanie PYTHONPATH=/app/src w run.sh — fix ModuleNotFoundError w kontenerze HA

## [1.0.0] — 2026-04-18

### Dodano
- Dashboard z podsumowaniem ostatnich 12 miesięcy i banerem ROI
- Zarządzanie odczytami miesięcznymi (CRUD) z walidacją
- Moduł ROI: skumulowane oszczędności, analiza wrażliwości na cenę kWh, wykres
- Moduł inwestycji: wiele faz, sumowanie łącznego kosztu
- Moduł EV: oszczędności vs paliwo, historia miesięczna, ceny paliw, ustawienia (Tesla Model Y + BMW i3)
- Import z Excela (arkusz „Moja instalacja") z odrzucaniem błędnych rekordów
- Integracja z Home Assistant (pobieranie kWh EV z encji HA)
- HA Add-on z ingress (panel w sidebarze HA)
- Formatowanie liczb z separatorem tysięcy (spacja nierozdzielająca)
- Monit ROI preview przy edycji historycznych odczytów
