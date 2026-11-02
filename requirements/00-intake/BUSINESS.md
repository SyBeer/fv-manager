# FV Manager v1.x — Opis funkcjonalności biznesowej

Snapshot stanu na wersję 1.12.0. Materiał wyjściowy do planowania v2.0.

---

## 1. Kontekst i cel aplikacji

FV Manager to narzędzie do śledzenia zwrotu z inwestycji w fotowoltaikę. Odpowiada na pytanie: **"Kiedy zwróci się moja instalacja solarna?"**

Użytkownik to prosument — właściciel instalacji PV na dachu domu, który chce wiedzieć ile oszczędza na rachunkach za prąd i kiedy osiągnie break-even. Aplikacja rozszerza tę analizę o oszczędności z pojazdów elektrycznych (EV vs paliwo).

Aplikacja jest jednoosobowa — nie ma kont użytkowników, nie ma logowania. Działa w dwóch trybach:

1. **Standalone** — serwer na porcie 8010, dostęp przez przeglądarkę w sieci domowej
2. **Home Assistant Add-on** — panel boczny w HA, Docker, ingress proxy, 4 architektury (aarch64, amd64, armv7, armhf)

---

## 2. Moduły funkcjonalne

### 2.1 Dashboard

Strona główna aplikacji. Pokazuje:

1. **Banner ROI** — status zwrotu (osiągnięty / w toku), łączne oszczędności (FV + EV osobno), łączna produkcja kWh, szacowane miesiące do break-even
2. **Tabela 12 ostatnich miesięcy** — produkcja, autokonsumpcja, oddane do sieci, pobrane z sieci, zużycie, oszczędności w PLN
3. **Empty state** — gdy brak danych, wyświetla linki do dodania odczytu lub importu

**Ograniczenia:**
- Brak wykresów na dashboardzie (wykres jest tylko na stronie ROI)
- Brak porównań rok do roku
- Brak trendów i prognoz
- Tekst empty state wspomina "Import Excel" — ta funkcja została usunięta w v1.5

### 2.2 Odczyty energii

Rejestr miesięcznych odczytów z licznika dwukierunkowego. To główne źródło danych całej aplikacji.

**Co użytkownik wprowadza:**
1. Okres (format RRRR.MM) + rok + miesiąc + liczba dni
2. Trzy wartości z licznika:
   - Produkcja [kWh] — ile wyprodukował PV
   - Oddane do sieci [kWh] — licznik 2.8.0 (nadwyżka wysłana do operatora)
   - Pobrane z sieci [kWh] — licznik 1.8.0 (prąd kupiony od operatora)
3. Opcjonalnie: cena kWh z faktury, numer faktury, kwota brutto faktury, notatki
4. Opcjonalnie: zużycie EV per pojazd (kWh/miesiąc) lub sumaryczne

**Przyciski integracji** — przy polach produkcji, oddanej i pobranej energii dostępne są przyciski "HA" pobierające wartość z Home Assistant. Przy polach EV — przycisk "Tesla" pobierający dane z Tesla Fleet API.

**Co system oblicza automatycznie (na każdy miesiąc):**
1. Autokonsumpcja = produkcja − oddane do sieci
2. Zużycie całkowite = autokonsumpcja + pobrane z sieci
3. Pula net-meteringu = oddane × 0,80
4. Oszczędności [kWh] = autokonsumpcja + min(pula, pobrane)
5. Oszczędności [PLN] = oszczędności [kWh] × cena za kWh

Gdy brak ceny z faktury, system używa ceny domyślnej (0,75 zł/kWh, konfigurowalna przez zmienną środowiskową).

**Operacje:** dodawanie, edycja, usuwanie odczytów.

**Ograniczenia:**
- Brak walidacji fizycznej spójności — system akceptuje oddane > produkcja, co daje ujemną autokonsumpcję i błędne obliczenia
- Brak walidacji formatu okresu — pole RRRR.MM nie jest sprawdzane server-side
- Net-metering liczony per miesiąc zamiast w cyklu rocznym (szczegóły w sekcji 3)

### 2.3 Inwestycje

Rejestr etapów inwestycji w instalację. Obsługuje wieloetapowe inwestycje (panele → falownik → magazyn energii → ładowarka EV → inne).

**Co użytkownik wprowadza:**
1. Data inwestycji
2. Opis (np. "Panele 10 kWp", "Falownik Fronius")
3. Koszt [PLN] (brutto)
4. Moc [kWp] (opcjonalnie)
5. Notatki

**Łączna inwestycja** = suma kosztów wszystkich etapów. Ta wartość jest używana w całej analizie ROI.

**Operacje:** dodawanie, edycja, usuwanie.

Ten moduł jest prosty i działa poprawnie — brak istotnych ograniczeń.

### 2.4 Analiza ROI

Odpowiada na główne pytanie aplikacji: kiedy inwestycja się zwróci.

**Co system pokazuje:**
1. Łączna inwestycja vs łączne oszczędności (z podziałem na FV i EV)
2. Kwota pozostała do break-even
3. Średnie miesięczne oszczędności
4. Szacowana liczba miesięcy do zwrotu (ekstrapolacja liniowa)
5. Status: "zwrot osiągnięty" lub "w toku"
6. Łączna produkcja [kWh]

**Wykres (Chart.js):**
- Linia kumulatywnych oszczędności (narastająco miesiąc po miesiącu)
- Linia pozioma = łączna inwestycja (próg break-even)
- Oddzielna linia przerywana dla składnika EV

**Analiza wrażliwości:**
Tabela ROI przeliczonego dla 7 scenariuszy cenowych: 0,50 / 0,60 / 0,70 / 0,80 / 0,90 / 1,00 / 1,20 zł/kWh. Pokazuje jak zmiana ceny energii wpływa na tempo zwrotu.

**ROI Preview:**
Przy edycji odczytu dostępny modal pokazujący wpływ zmiany na ROI (before/after).

**Ograniczenia:**
- Ekstrapolacja break-even to prosta średnia arytmetyczna (remaining / avg_monthly_savings). Nie uwzględnia sezonowości — latem oszczędności są dużo wyższe niż zimą. Przy danych z < 12 miesięcy (np. tylko lato) prognoza jest nierealistycznie optymistyczna. Brak ostrzeżenia dla użytkownika.
- Analiza wrażliwości dziedziczy ten sam defekt — wszystkie 7 scenariuszy używa błędnej formuły per-miesiąc

### 2.5 Pojazdy elektryczne (EV)

Śledzenie oszczędności z ładowania EV w porównaniu z ekwiwalentnym kosztem paliwa.

**Zarządzanie pojazdami:**
1. Nazwa pojazdu
2. Sprawność [kWh/100 km] (domyślnie 16,0)
3. Zużycie paliwa ekwiwalentnego auta spalinowego [l/100 km] (domyślnie 10,0)
4. Typ paliwa (PB95, PB98, ON)

Obsługa wielu pojazdów jednocześnie. Zużycie kWh wprowadzane per pojazd per miesiąc (w formularzu odczytu lub przez Tesla API).

**Historia cen paliw:**
Rejestr cen paliwa z datą, ceną/litr, typem i źródłem (np. Orlen). System używa ceny z najbliższej wcześniejszej daty.

**Co system oblicza (per pojazd per miesiąc):**
1. Przejechane km = (kWh / sprawność) × 100
2. Koszt paliwa ekwiwalentny = (km / 100) × zużycie paliwa × cena paliwa
3. Koszt prądu = kWh × cena kWh
4. Oszczędność netto = koszt paliwa − koszt prądu
5. Zaoszczędzone litry

**Karty podsumowania:** łączne oszczędności EV, łączne km, łączne zaoszczędzone litry, aktualna cena paliwa.

Oszczędności EV wchodzą do kalkulacji ROI (total_savings = FV_savings + EV_savings).

**Tryb legacy:** Jeśli nie zdefiniowano pojazdów, system korzysta z ustawień globalnych EV + pola ev_kwh z odczytu (kompatybilność wsteczna z wersją sprzed multi-vehicle).

**Konfiguracja integracji:**
- Home Assistant: encje sensora (produkcja solarna, pobór z sieci, oddanie do sieci)
- Tesla: access token, site ID (auto-wykrywalny), URL bazy API (region EU/US)
- Przycisk testu połączenia HA

**Ograniczenia:**
- Wyszukiwanie ceny paliwa: jeśli brak ceny przed datą odczytu, system bierze ostatnią dostępną (nawet z przyszłości) — może być mylące
- Brak automatycznej synchronizacji — każde pobranie danych wymaga ręcznego kliknięcia

### 2.6 Import i eksport danych

**Eksport CSV:**
- Separator: średnik (`;`)
- Kodowanie: UTF-8
- Zawiera kolumny obliczane (autokonsumpcja, oszczędności kWh/PLN, wartość produkcji)
- Plik nadaje się do ponownego importu bez modyfikacji

**Import CSV:**
- Upload pliku w formacie szablonu (do pobrania z aplikacji)
- Duplikaty pomijane (INSERT OR IGNORE na unikalnym okresie)
- Wyświetla podsumowanie: zaimportowano / pominięto

**Czyszczenie bazy ("Danger zone"):**
- Przycisk "Wyczyść bazę" — kasuje **tylko odczyty**
- **BUG:** Tekst w interfejsie mówi "Usuwa wszystkie odczyty, inwestycje i ceny paliw" — to nieprawda, kod kasuje wyłącznie tabelę readings. Inwestycje, pojazdy, ceny paliw i ustawienia pozostają nienaruszone.

**Ograniczenia:**
- Import CSV nie waliduje danych (akceptuje oddane > produkcja, ujemne wartości)
- Brak pełnego backup/restore — eksportować można tylko odczyty, nie inwestycje, pojazdy, ceny paliw ani ustawienia
- Martwy kod: plik `services/importer.py` (legacy import Excel) i zależność `openpyxl` w `requirements.txt` — oba nieużywane od v1.5

### 2.7 Integracje zewnętrzne

**Home Assistant:**
- W trybie Add-on: automatyczna autoryzacja przez SUPERVISOR_TOKEN (bez konfiguracji)
- Trzy konfigurowalne encje: produkcja solarna, pobór z sieci (1.8.0), oddanie do sieci (2.8.0)
- Pobieranie danych: Statistics API (preferowane, działa dla dowolnego miesiąca historycznego) z fallbackiem na History API (ostatnie ~10 dni)
- Automatyczna konwersja Wh → kWh
- Endpoint testu połączenia — sprawdza autoryzację i zwraca ostatnią produkcję

**Tesla Fleet API:**
- Pobieranie miesięcznego zużycia energii ładowania (charge_energy_added z telemetry_history)
- Auto-wykrywanie energy sites (przycisk "Wykryj" listuje dostępne instalacje Tesla)
- Konfigurowalne: token, site ID, URL bazy API (region EU: `fleet-api.prd.eu.vn.cloud.tesla.com`)

**API dla sensorów HA:**
- Endpoint `/api/summary` zwraca JSON z danymi ROI — można użyć jako REST sensor w HA

**Ograniczenia:**
- Wszystkie integracje to pull-only, inicjowane przez użytkownika. Brak automatycznego harmonogramu, webhooków, triggerów automatyzacji
- Tokeny (HA i Tesla) przechowywane w plaintext w SQLite. Token HA daje pełny dostęp do instalacji smart home (zamki, alarmy, kamery)

---

## 3. Model rozliczeniowy — net-metering

To sekcja kluczowa, ponieważ model rozliczeniowy jest sercem wszystkich kalkulacji i zawiera najpoważniejszy znany defekt.

### Obecny model

Aplikacja implementuje **stary polski net-metering** (obowiązujący dla umów zawartych przed 1 lipca 2022):
- Prosument oddaje nadwyżkę energii do sieci
- 80% oddanej energii wraca jako "pula rozliczeniowa" do wykorzystania gdy produkcja nie pokrywa zużycia
- Współczynnik 0,80 jest zakodowany na stałe w `calculations.py`

### Formuła

```
autokonsumpcja = produkcja − oddane_do_sieci
pula_net_metering = oddane_do_sieci × 0,80
oszczędności_kwh = autokonsumpcja + min(pula, pobrane_z_sieci)
oszczędności_pln = oszczędności_kwh × cena_za_kwh
```

### Defekt: kalkulacja per-miesiąc zamiast cyklu rocznego

W rzeczywistym modelu polskiego net-meteringu pula 80% **kumuluje się przez 12 miesięcy**. Nadwyżka z lata (wysoka produkcja, niskie zużycie) jest dostępna zimą (niska produkcja, wysokie zużycie).

Obecna implementacja traktuje każdy miesiąc niezależnie:
- **Lato** — pula jest duża (dużo oddanej energii), ale pobór mały → nadwyżka puli przepada
- **Zima** — pula jest mała (mało oddanej energii), ale pobór duży → brakuje zakumulowanej puli z lata

Skutki biznesowe:
1. Oszczędności letnich miesięcy są zaniżane (nadwyżka puli się marnuje)
2. Oszczędności zimowych miesięcy mogą być zawyżane lub zaniżane (zależy od proporcji)
3. W skali roku różnice mogą się częściowo kompensować, ale ekstrapolacja break-even na podstawie średniej miesięcznej jest niewiarygodna — szczególnie gdy dane obejmują < 12 miesięcy
4. Analiza wrażliwości (sekcja 2.4) dziedziczy ten sam błąd

### Brak wsparcia net-billingu

Od 1 lipca 2022 nowe umowy w Polsce rozliczane są w modelu **net-billing** (sprzedaż/zakup energii po cenach rynkowych, nie bilansowanie ilościowe). Aplikacja nie obsługuje tego modelu — ogranicza to bazę użytkowników do prosumentów ze starymi umowami.

### Cena domyślna

Gdy odczyt nie ma ceny z faktury, system używa ceny domyślnej: **0,75 zł/kWh** (konfigurowalna przez zmienną środowiskową `DEFAULT_PRICE_KWH`). Nie ma wizualnego oznaczenia w interfejsie, które odczyty używają ceny z faktury, a które domyślnej.

---

## 4. Deployment i dostępność

### Tryb standalone
- Serwer FastAPI/uvicorn na porcie 8010
- Baza SQLite w lokalnym katalogu `data/fv.db`
- Brak jakiejkolwiek autentykacji — każdy z dostępem do portu widzi i modyfikuje dane

### Tryb HA Add-on
- Kontener Docker z ingress proxy (HA zapewnia autentykację)
- Panel boczny w HA (ikona: solar-power)
- Baza w `/data/fv.db` (wolumen persystentny HA)
- 4 architektury: aarch64, amd64, armv7, armhf

### Interfejs
- Język: wyłącznie polski
- Motyw: ciemny (Tailwind CSS dark)
- Sidebar z nawigacją (zwijany na mobile)
- Zależności CDN: Chart.js i Flatpickr z cdn.jsdelivr.net — bez internetu nie załadują się

---

## 5. Ograniczenia i ryzyka biznesowe

### 5.1 Poprawność kalkulacji

| Problem | Wpływ | Priorytet |
|---------|-------|-----------|
| Net-metering per-miesiąc zamiast cyklu rocznego | Błędne oszczędności sezonowe, niewiarygodna prognoza break-even | Krytyczny |
| Ekstrapolacja liniowa bez sezonowości | Optymistyczna prognoza przy danych < 12 miesięcy | Wysoki |
| Brak ostrzeżenia przy < 12 miesiącach danych | Użytkownik nie wie że prognoza jest niewiarygodna | Średni |
| Brak walidacji oddane ≤ produkcja | Ujemna autokonsumpcja, błędne obliczenia | Średni |

### 5.2 Kompletność danych

| Problem | Wpływ | Priorytet |
|---------|-------|-----------|
| Brak pełnego backup/restore | Utrata inwestycji, pojazdów, cen paliw i ustawień przy awarii | Wysoki |
| Brak automatycznej synchronizacji z HA/Tesla | Użytkownik musi ręcznie klikać przycisk per pole per miesiąc | Średni |
| Tekst "Danger zone" niezgodny z kodem | Użytkownik myśli że kasuje wszystko, a kasuje tylko odczyty | Niski |
| Martwy kod i zależność (importer.py, openpyxl) | Zbędna powierzchnia ataku, dezorientacja | Niski |

### 5.3 Model biznesowy

| Problem | Wpływ | Priorytet |
|---------|-------|-----------|
| Tylko stary net-metering (pre-07.2022) | Kurcząca się baza użytkowników — nowe umowy to net-billing | Wysoki |
| Współczynnik 0,80 na stałe w kodzie | Brak możliwości zmiany bez edycji kodu | Średni |
| Sensitivity analysis zmienia tylko cenę | Nie pokazuje różnicy między net-metering a net-billing | Niski |

### 5.4 Bezpieczeństwo i dostęp

| Problem | Wpływ | Priorytet |
|---------|-------|-----------|
| Brak autentykacji w trybie standalone | Każdy w sieci widzi/modyfikuje dane | Wysoki |
| Token HA w plaintext w SQLite | Wyciek = pełna kontrola smart home | Wysoki |
| Token Tesla w plaintext w SQLite | Wyciek = dostęp do konta Tesla | Wysoki |
| Brak ochrony CSRF na formularzach | Cross-site request forgery na operacjach destrukcyjnych | Średni |
| CDN bez SRI (Subresource Integrity) | Ryzyko podmiany zasobu na CDN | Niski |

### 5.5 UX i użyteczność

| Problem | Wpływ | Priorytet |
|---------|-------|-----------|
| Brak porównań rok do roku | Nie widać jak zmienia się efektywność | Średni |
| Brak trendów na dashboardzie | Dashboard to tylko tabela, brak wizualizacji poza ROI | Średni |
| Dashboard wspomina "Import Excel" (usunięty w v1.5) | Mylący tekst dla użytkownika | Niski |
| config.yaml HA opisuje "import z Excela" | Stały opis w konfiguracji add-on | Niski |
| Brak oznaczenia odczytów z ceną domyślną vs z faktury | Użytkownik nie wie które oszczędności są szacunkowe | Niski |

---

## 6. Słownik pojęć

| Pojęcie | Definicja |
|---------|-----------|
| **Prosument** | Konsument energii, który jednocześnie ją produkuje (instalacja PV na dachu) |
| **Net-metering** | Model rozliczeniowy: prosument "oddaje" nadwyżkę do sieci i odbiera 80% z powrotem (stary polski model, umowy sprzed 07.2022) |
| **Net-billing** | Nowy model (od 07.2022): prosument sprzedaje energię po cenie rynkowej i kupuje po cenie detalicznej — rozliczenie wartościowe, nie ilościowe |
| **Autokonsumpcja** | Energia zużyta bezpośrednio z PV, bez przesyłu przez sieć (produkcja − oddane) |
| **Pula zwrotna 80%** | W net-meteringu: 80% energii oddanej do sieci wraca do prosumenta jako "kredyt" do pobrania w ciągu 12 miesięcy |
| **ROI** | Return on Investment — stosunek oszczędności do kosztu inwestycji |
| **Break-even** | Moment, w którym skumulowane oszczędności pokrywają koszt inwestycji |
| **Licznik 1.8.0** | Rejestr energii pobranej z sieci (forward meter) |
| **Licznik 2.8.0** | Rejestr energii oddanej do sieci (reverse meter) |
| **kWp** | Kilowat peak — moc szczytowa instalacji PV w standardowych warunkach testowych |
| **Ingress** | Mechanizm HA, który proxy-uje ruch HTTP do add-onów z automatyczną autentykacją |
| **Sensitivity analysis** | Analiza "co jeśli" — jak zmiana ceny energii wpływa na ROI |
