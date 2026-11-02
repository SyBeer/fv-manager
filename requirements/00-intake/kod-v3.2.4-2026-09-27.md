# Odczyt kodu v3.2.4 (analiza statyczna, bez uruchamiania)

Data: 2026-09-27. Wykonal: Claude na prosbe wlasciciela instalacji (sesja wywiadu live).
Zakres: src/services/calculations.py, src/main.py, templates/pv.html, templates/import.html.
Odczyt kodu, nie obserwacja dzialajacej aplikacji.

## Rozliczenie net-metering (Q-001)
- Pula kumuluje sie miedzy miesiacami (carry_over): calculations.py:21-54 (calc_monthly), 120-178 (enrich_readings_sequence).
- Pula zeruje sie w miesiacu `cycle_start_month` (domyslnie 4 = kwiecien) oraz przy zmianie modelu net-metering <-> net-billing: calculations.py:150-153.
- W main.py nie znaleziono ustawienia `cycle_start_month` - zawsze uzywany domyslny kwiecien (grep "cycle_start" w main.py: 0 trafien).
- Wspolczynnik puli konfigurowalny: `ev_settings.net_metering_ratio`, domyslnie 0.80 (main.py:517, 975).
- Autokonsumpcja przycinana do 0, gdy oddane > produkcja: calculations.py:37.

## Net-billing i RCE (Q-002)
- Model rozliczen wybierany per okres z tabeli `billing_periods` (data startu): calculations.py:57 (_get_billing_model); zarzadzanie na /pv (main.py:1824).
- Net-billing: oszczednosc = autokonsumpcja x cena zakupu + oddane x cena RCE: calculations.py:94-116.
- Ceny RCE wpisywane recznie formularzem POST /pv/rce-price (data, cena, zrodlo): main.py:1857. Brak automatycznego pobierania (brak odwolan do PSE/API RCE w kodzie).
- Odczyt moze miec wlasna `sale_price_kwh`, ktora nadpisuje RCE: calculations.py:159.

## Analiza wrazliwosci (Q-004)
- 7 stalych cen: 0.50, 0.60, 0.70, 0.80, 0.90, 1.00, 1.20 zl/kWh (bez 1.10): main.py:978. Brak wariantu procentowego.

## Ceny paliwa (Q-005)
- Wpisywane recznie formularzem POST /ev/fuel-price (data, cena, typ, zrodlo): main.py:1698. Brak automatycznego pobierania.

## Walidacja odczytow (Q-008)
- `_validate_reading` (main.py:477-495): format RRRR.MM, wartosci >= 0, oddane <= produkcja.
- Uzywana w formularzu nowego odczytu (main.py:676), edycji (main.py:792) i imporcie CSV (main.py:1074).
- Import CSV: wiersz z bledem jest pomijany i liczony jako "pominiety"; parametr `rejected=0` zawsze zero (main.py:1103).
- Import CSV oczekuje separatora ";" i naglowkow po polsku ("Okres", "Produkcja [kWh]"...), inaczej niz przyklad w README (przecinek, naglowki angielskie).

## Uwierzytelnianie i tokeny (Q-009)
- Opcjonalny Basic Auth, gdy ustawione `FV_AUTH_PASSWORD`: main.py:105-130.
- Jest middleware CSRF: main.py:133.
- Token HA z env (`SUPERVISOR_TOKEN` w add-onie, `HA_URL`/`HA_TOKEN` standalone): main.py:15-22.

## Czyszczenie bazy (Q-010)
- POST /admin/clear-db usuwa tabele: ev_monthly, readings, investments, fuel_prices, vehicles, billing_periods, rce_prices (zostaja ustawienia): main.py:1111-1123.
- Tekst w UI: "Usuwa wszystkie odczyty, inwestycje i ceny paliw" (templates/import.html:223); potwierdzenie JS: "usuniecie WSZYSTKICH danych".
- Istnieje pelny backup JSON (GET /backup/full) i przywracanie (POST /restore): main.py:1125, 1161.

## Inne moduly, ktorych nie opisuje README
- Strony /pv (okresy rozliczen, ceny RCE, ustawienia), /bateria, /ogrzewanie, /metodologia: main.py:1774-1947.
- Modul prognozy `services/forecast.py` (degradacja roczna, net-billing), `services/ha_stats.py`.
