# Changelog

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
