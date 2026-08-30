# Changelog

## [3.2.3] — 2026-08-30

### Dodano
- **Trwały przełącznik motywu jasny/ciemny w menu bocznym** — dostępny na każdej stronie (wcześniej tylko w Ustawieniach). Wybór motywu jest zapisywany w `localStorage` jako nadrzędny: nie resetuje się przy restarcie serwera ani gdy zapis do bazy zawiedzie; serwer nadal zapisuje motyw w `app_settings` (dla świeżej przeglądarki), ale nie nadpisuje już lokalnego wyboru. `base.html` udostępnia wspólne `fvApplyTheme/fvSetTheme/fvToggleTheme`, `import.html` z nich korzysta (koniec duplikacji)

### Zmieniono
- **Jednostki przeniesione z komórek tabel do nagłówków kolumn** we wszystkich tabelach danych (dashboard, odczyty, ROI + prognoza, EV: historia/pojazdy/ceny paliw, pojazd: dane miesięczne, inwestycje, ceny prądu). Wiersze pokazują same liczby, nagłówki niosą jednostkę (`[kWh]`, `[zł]`, `[L]`, `[zł/kWh]`, `[zł/L]`, `[km]`). Tabela dokumentacyjna importu CSV bez zmian (jednostki są tam częścią nazw kolumn)

## [3.2.2] — 2026-08-30

### Poprawiono
- **Edycja miesięcznego wpisu w panelu per samochód kasowała dane ładowania publicznego.** Modal edycji na stronie pojazdu (`/ev/pojazdy/{id}`) miał tylko pola domowe (kWh/km/licznik), a handler `edit_vehicle_monthly` nadpisywał kolumny `public_*` pustymi wartościami → zapis przez ten modal wymazywał wcześniej wprowadzone ładowanie publiczne (regresja z 3.2.1). Modal ma teraz sekcję „Ładowanie publiczne (poza FV)" z polami kWh/km/koszt, z poprawnym prefillem

### Zmieniono
- `ev.html`: reorganizacja strony EV — przyciski „Dodaj pojazd" i „Dodaj cenę paliwa" przeniesione na samą górę (kotwice do formularzy); sekcja „Ceny paliw" przeniesiona pod konfigurację pojazdów (układ pionowy zamiast dwóch kolumn)
- `metodologia.html` („Jak liczymy"): opis oszczędności EV rozbity na ładowanie domowe (opłacalność FV + vs paliwo) i publiczne (poza FV, tylko vs paliwo) ze wzorem i wyjaśnieniem ujemnej oszczędności publicznej; blok ROI i lista danych wejściowych zaktualizowane
- `README.md`: udokumentowany pełny schemat `ev_monthly` (km, odometer_km, public_*), nowa sekcja o dwóch miarach oszczędności, założenia i logika kalkulacji

## [3.2.1] — 2026-08-30

### Poprawiono
- **Edycja odczytu gubiła dane ładowania publicznego.** `edit_reading_form` nie prefillował pól `public_kwh/public_km/public_cost_pln`, a `update_reading` ich nie parsował ani nie zapisywał (kasował `ev_monthly` i wstawiał bez kolumn publicznych) — edycja wpisu wymazywała wprowadzone wcześniej wartości publiczne. Teraz ścieżka edycji odzwierciedla `create_reading`

### Zmieniono
- **Opłacalność auta vs paliwo uwzględnia teraz ładowanie publiczne.** Wcześniej wynik pojazdu liczył wyłącznie ładowanie domowe. Ładowanie publiczne pozostaje poza opłacalnością FV/ROI (prąd nie z licznika/PV), ale wchodzi do porównania auta z benzyną: `oszczędność_publiczna = uniknięte_paliwo(public_km) − public_cost_pln`
  - `main.py` (`_agg_vehicles_ev`, `vehicle_detail`): oszczędności rozbite na `savings_home` (FV) i `savings_public`, suma = „vs paliwo"
  - `vehicle_detail.html`: karta „Oszczędności vs paliwo" pokazuje rozbicie domowe/publiczne; przy ujemnej wartości publicznej — podpowiedź „Ładowanie publiczne droższe niż paliwo na tych kilometrach"
- testy: `test_ev_public_charging.py` rozszerzone o rozbicie oszczędności (home/public/suma), przypadek ujemnej oszczędności publicznej i miesiąc tylko-publiczny

## [3.2.0] — 2026-08-27

### Dodano
- **Rozdzielenie ładowania EV domowego (liczone do opłacalności FV) od publicznego (poza FV).** Ładowanie na ładowarkach publicznych nie pochodzi z licznika/PV, więc nie powinno wpływać na wynik opłacalności instalacji — teraz jest odnotowywane osobno (kWh, km, koszt) i wyłączone z kalkulacji FV, ale wliczane do pełnego TCO i przebiegu pojazdu.
  - `db.py`: `ev_monthly` + kolumny `public_kwh`, `public_km`, `public_cost_pln` (migracja `ALTER TABLE`, idempotentna)
  - `main.py`: `create_reading`, `edit_vehicle_monthly`, `edit_ev_monthly` zapisują pola publiczne (obsługa wpisu tylko-publicznego); `_agg_vehicles_ev` i `vehicle_detail` raportują dane publiczne osobno oraz `total_km_all` (domowe + publiczne). Logika `calc_ev_savings` / `_ev_enrich` (opłacalność FV) bez zmian — otrzymuje wyłącznie wartości domowe
  - `reading_form.html`, `ev.html`: sekcje „Domowe — liczone do FV" / „Publiczne — poza FV" w formularzu dodawania i edycji
  - `vehicle_detail.html`: karta kosztu ładowania publicznego + przebieg łączny (z publicznym)
  - testy: `test_ev_public_charging.py` (6 przypadków — wykluczenie z FV, raportowanie osobne, przebieg łączny, wpis tylko-publiczny, wsteczna zgodność)
- `base.html`: pozycja menu „Nowy wpis" z ikoną (skrót do `/odczyty/nowy`)

### Zmieniono
- `reading_form.html`: nagłówek sekcji faktury „Faktura (opcjonalnie)" → „Faktura za energię elektryczną (opcjonalnie)"
- `base.html`: podświetlenie „Odczyty" w menu nie obejmuje już strony „Nowy wpis"

## [3.1.1] — 2026-06-21

### Dodano
- `main.py`, `ev.html`, `vehicle_detail.html`: kolumna „kWh/100km" (efektywność rzeczywista = `kWh / km × 100`) w danych miesięcznych EV — w „Historia miesięczna" (`/ev`) oraz na stronie pojazdu. Dla km estymowanego z kWh wartość oznaczona „(est.)"; brak km → „—"

### Poprawiono
- `vehicle_detail.html`: badge „Źródło km" obejmuje teraz wartość „licznik (od startu)" (pierwszy miesiąc kotwiczony do `przebieg_km`) — wcześniej wpadała do „(est.)"

## [3.1.0] — 2026-06-21

### Dodano
- `main.py`, `ev.html`: edycja wpisu ceny paliwa — nowy route `POST /ev/fuel-price/{price_id}/edytuj` (`UPDATE fuel_prices`) oraz inline-formularz edycji (data, cena, rodzaj, źródło) przy każdym wierszu w tabeli „Ceny paliw", uruchamiany ikoną ołówka obok kosza (wykorzystuje istniejący `toggleEvEdit`)

### Zmieniono
- `main.py` (`_inject_odometer_km`): `vehicles.przebieg_km` (stan licznika na starcie trackowania) jest teraz kotwicą „miesiąca zerowego" — pierwszy wpis pojazdu liczy `km = pierwszy.odometer_km − przebieg_km` zamiast estymaty z kWh; gdy każdy miesiąc ma odczyt licznika, „Łącznie km" = `ostatni odometer − przebieg_km`, zgodnie z licznikiem (wcześniej suma zawyżała stan licznika przez estymatę pierwszego miesiąca)
- `main.py`, `ev.html`: pole „Stan licznika przy starcie" wymagane przy rejestracji i edycji pojazdu (było opcjonalne); walidacja `przebieg_km ≥ 0` oraz `≤ MIN(odometer_km)` zapisanych odczytów

### Dodano
- `ev.html`: banner ostrzegawczy nad listą pojazdów dla aut bez `przebieg_km` (pierwszy miesiąc liczony jako estymata) + bannery błędów walidacji formularza pojazdu
- strona pojazdu: pierwszy miesiąc oznaczony źródłem „licznik (od startu)"
- `ev.html`: wyraźny link „Szczegóły →" w prawym dolnym rogu karty pojazdu (prowadzi do `/ev/pojazdy/{id}`); etykieta karty zbiorczej zmieniona z „Łącznie przejechane (z EV kWh)" na „(licznik / est.)" — wartość jest teraz licznikowa

### Poprawiono
- `db.py`, `main.py`, `base.html`, `import.html`: motyw jasny/ciemny zapisywany trwale w `app_settings` (kolumna `theme`) i renderowany server-side na `<html data-theme>` — wcześniej żył tylko w `localStorage`, który w iframe HA ingress / Safari ITP jest czyszczony po kilku dniach, przez co motyw wracał do ciemnego; nowy endpoint `POST /ev/theme` (JSON, omija CSRF), `localStorage` zdegradowany do mirrora
- `pv.html`, `ev.html`: spójny format dat — pola `<input type="date">` (okresy rozliczeniowe, ceny RCE, ceny paliw) zastąpione polami flatpickr `dateFormat: "Y-m-d"`; natywny picker renderował w locale `DD.MM.RRRR` mimo etykiety „RRRR-MM-DD" — teraz wszystkie pola dat wyświetlają RRRR-MM-DD zgodnie z etykietą (jak w `investments`)

## [3.0.8] — 2026-05-25

### Poprawiono
- `main.py`: CSRFMiddleware pomija sprawdzenie tokenów dla żądań `Content-Type: application/json` — JSON POST nie może być wywołany przez cross-site formularz HTML, więc jest bezpieczny bez CSRF; naprawia "The string did not match the expected pattern." w modalu ROI nawet gdy EXEMPT_PATHS nie działa (HA ingress stara wersja)
- `main.py`: CSRF rejection zwraca `JSONResponse` zamiast plain text — frontend zawsze dostanie poprawny JSON nawet przy błędzie 403
- `reading_form.html`: `showRoiPreview()` sprawdza `res.ok` przed `res.json()` — nieoczekiwane kody HTTP (403, 500) pokazują czytelny komunikat zamiast WebKit parse error

## [3.0.7] — 2026-05-25

### Poprawiono
- `main.py`: middleware używa `scope["path"]` zamiast `url.path` — w HA ingress `url.path` zawiera prefix `/api/hassio_ingress/xxx/` co powodowało niedziałanie EXEMPT_PATHS (CSRF i auth sprawdzały błędne ścieżki)
- `main.py`: `_csrf_verify` — guard na pusty token + `except (BadSignature, BadData)` — malformed token dawał nieobsługiwany wyjątek zamiast 403

## [3.0.6] — 2026-05-25

### Poprawiono
- `main.py`: CSRF przepisany na cookie-free — signed token (itsdangerous) generowany server-side i embedowany w HTML, walidacja po samej sygnaturze bez cookies; naprawia CSRF 403 w HA ingress (iframe blokował SameSite cookies)

## [3.0.5] — 2026-05-25

### Poprawiono
- `main.py`, `base.html`: fix CSRF dla Safari/ITP — token renderowany server-side w `<meta name="csrf-token">` zamiast czytany z `document.cookie` (Safari blokował odczyt JS do cookie); `csrf_token_plain` cookie usunięty; `samesite` zmieniony z `strict` na `lax` (działa też w HA ingress iframe)

## [3.0.4] — 2026-05-25

### Poprawiono
- `main.py`: rozszerzenie fixa Safari/przecinek na wszystkie pozostałe formularze — `_ff()` zamiast `float = Form(...)` w endpointach: `/inwestycje/nowa`, `/inwestycje/{id}/edytuj`, `/ev/pojazdy/nowy`, `/ev/pojazdy/{id}/edytuj`, `/ev/pojazdy/{id}/monthly/{period}/edytuj`, `/ev/fuel-price`, `/ev/settings`, `/pv/rce-price`, `/pv/settings`

## [3.0.3] — 2026-05-25

### Poprawiono
- `main.py`: helper `_ff()` — parsowanie floatów z formularza toleruje przecinek jako separator dziesiętny (Safari/macOS z polską lokalizacją submituje `"965,434"` zamiast `"965.434"`)
- `main.py`: `try/except` w endpointach `POST /odczyty/nowy` i `POST /odczyty/{id}/edytuj` — błąd parsowania zwraca stronę z komunikatem zamiast 500 JSON (który Safari traktował jako plik do pobrania)
- `main.py`: `roi_preview` — dodano `billing_periods`, `rce_prices`, `nm_ratio`, `default_price` + `try/except` z JSON error response
- `reading_form.html`: `invoice_number or ''` — Python `None` nie renderuje się jako string `"None"`
- `reading_form.html`: modal ROI preview — obsługa błędu serwera i ochrona `fmt` przed `null`

## [3.0.2] — 2026-05-24

### Poprawiono
- `ha_stats.py`: fix parsowania odpowiedzi Statistics API — klucz `service_response.statistics` zamiast `response` (bug powodował "Empty statistics" i brak danych z HA)

## [3.0.1] — 2026-05-24

### Poprawiono
- `ha_stats.py`: dodano `units: {"energy": "kWh"}` do requestu Statistics API — HA sam konwertuje Wh→kWh, usunięto `_fetch_unit`
- `ha_stats.py`: poprawka obsługi wielu kubełków miesięcznych — filtrowanie po `start` w strefie lokalnej zamiast sumowania wszystkich (fix timezone UTC vs lokalny)
- `ha_stats.py`: `types: ["change"]` zamiast `["change", "state"]` — tylko delta, nie stan licznika
- `investments.html`, `investment_form.html`: pole `power_kwp` przemianowane na "Sumaryczna moc FV" z hintem wyjaśniającym semantykę (łączna moc, nie dokładka)

## [3.0.0] — 2026-05-24

### Dodano
- Dark/light mode: 27 CSS custom properties (`--bg`, `--bg-card`, `--border`, `--accent`, `--c-green` itd.)
- Przełącznik motywu Ciemny/Jasny w Ustawieniach (`/import`), persystencja przez `localStorage`
- Anti-FOUC script w `<head>` — motyw ustawiany przed renderem strony
- Karty PV na stronie `/pv` (produkcja, autokonsumpcja, oddane/pobrane z sieci, oszczędności)
- Karty pojazdów EV na stronie `/ev` i głównym dashboardzie (`/`)
- Karty PV na głównym dashboardzie (`/`)
- Endpoint edycji danych miesięcznych pojazdu: `POST /ev/pojazdy/{id}/monthly/{period}/edytuj`
- Modal edycji danych miesięcznych w `vehicle_detail.html` — draggable, wyśrodkowany, pole kWh/km/licznik

### Zmieniono
- Wszystkie 13 szablonów: hardcoded hex kolory zastąpione przez CSS variables
- Chart.js (roi.html, vehicle_detail.html): siatka i oś czytają kolory przez `getComputedStyle` — reagują na zmianę motywu

## [2.5.0] — 2026-05-24

### Dodano
- Podstrona szczegółów pojazdu EV: `GET /ev/pojazdy/{id}` — dane pojazdu, karty summary (km, kWh, oszczędności PLN, litry), wykres miesięczny kWh+oszczędności (Chart.js), tabela historii per miesiąc z badgem źródła km (ręczne / licznik / est.)
- Nowy szablon `templates/vehicle_detail.html`
- Rzeczywista średnia efektywność (kWh/100km) obliczana z miesięcy z faktycznymi km (nie estymowanymi)
- Link do podstrony pojazdu w tabeli pojazdów na stronie EV (klik w nazwę pojazdu)

## [2.4.2] — 2026-05-23

### Naprawiono
- 500 przy zapisie odczytu z polem `ev_odometer_v_<N>` — błędny slice `k[13:]` zamiast `k[14:]` dla prefiksu `"ev_odometer_v_"` (len=14); zamieniono wszystkie parsery kluczy formularza na `k.removeprefix(...)` (create_reading i update_reading)

## [2.4.1] — 2026-05-23

### Naprawiono
- Inline edit EV: pola kWh / km / stan licznika wyrównane siatką grid (4 kolumny, etykieta 200px stała)

## [2.4.0] — 2026-05-23

### Dodano
- Pole "Stan licznika [km]" w formularzu odczytu i inline edit EV — wpisujesz odczyt z licznika auta
- Kolumna `odometer_km` w tabeli `ev_monthly` (nullable, backward compat)
- Helper `_inject_odometer_km()` — oblicza miesięczne km z delty licznika w runtime (nie zapisuje do DB)

### Zmieniono
- Formularz odczytu per pojazd: trzy pola obok siebie — `kWh | km/mc lub stan licznika km (licznik)`
- Inline edit EV na stronie /ev: analogicznie dwa pola km — ręczne lub stan licznika
- Priorytet km: ręczne km > delta z licznika > obliczone z kWh (est.)
- Jeśli wpisano stan licznika (bez ręcznych km) — delta obliczana na bieżąco przy wyświetlaniu, **nie zapisywana** do pola `km` (poprawność przy ładowaniu publicznym)

## [2.3.0] — 2026-05-23

### Dodano
- Pole `przebieg_km` (przebieg licznika) w tabeli `vehicles` — opcjonalne, do wglądu
- Formularz dodawania i edycji pojazdu: nowe pole "Przebieg km"
- Tabela pojazdów: nowa kolumna "Przebieg" (wyświetla km lub "—")
- Kolumny `date_from` i `date_to` (YYYY.MM) w tabeli `vehicles` — zakres posiadania pojazdu
- Formularz dodawania i edycji pojazdu: pola "Od" / "Do" z walidacją formatu
- Tabela pojazdów: kolumny "Od" / "Do" w widoku listy
- Helper `_vehicles_for_period()` — filtruje pojazdy po zakresie dat

### Zmieniono
- Formularz nowego odczytu: pokazuje tylko pojazdy aktywne w danym miesiącu (`date_from`/`date_to`)
- Formularz edycji odczytu: analogiczne filtrowanie
- Strona EV — inline edit miesięczny: pola pojazdu widoczne tylko gdy pojazd był aktywny w danym okresie
- Migracje DB: `ALTER TABLE vehicles ADD COLUMN date_from TEXT|date_to TEXT|przebieg_km REAL`

## [2.2.1] — 2026-05-23

### Zmieniono
- Strona Metodologii: opis EV zaktualizowany — wpisujesz km z licznika zamiast "aplikacja liczy"
- Strona Metodologii: lista danych wejściowych zawiera "km" obok kWh
- Strona Metodologii: dodana nota o znaczeniu oznaczenia `(est.)` gdy km nie wpisane

## [2.2.0] — 2026-05-23

### Dodano
- Pole `km` (faktyczne kilometry) w tabeli `ev_monthly` — obok `kwh` można teraz wpisywać rzeczywiste km z licznika
- Formularz odczytu (`/odczyty/nowy` i edycja): dwa pola na pojazd — `kWh` i `km` obok siebie
- Strona EV: inline edit miesięcznych wpisów obsługuje oba pola (`kWh` + `km`)
- Oznaczenie `(est.)` przy km obliczonych ze wzoru (gdy brak ręcznego wpisu)
- Migracja DB: `ALTER TABLE ev_monthly ADD COLUMN km REAL` (backward compatible, nullable)

### Zmieniono
- `calc_ev_savings()` przyjmuje opcjonalny `km_driven` — gdy podane, używa faktycznych km zamiast obliczonych z efektywności
- Oszczędność EV liczona z faktycznych km jeśli dostępne: `koszt_paliwa(faktyczne_km) - koszt_pradu(faktyczne_kwh)`
- `ev_raw` w endpoincie GET `/ev` zmienione na `{period: {vid: {kwh, km}}}` (było `{vid: kwh}`)

## [2.1.1] — 2026-05-23

### Naprawiono
- Formularz Ustawień po zapisaniu wraca na stronę Ustawień (nie EV) z zielonym komunikatem potwierdzenia
- Napis "ENERGIA [KWH]" w formularzu odczytu wyświetla się poprawnie jako "ENERGIA [kWh]"
- Formularz nowego odczytu podpowiada automatycznie następny miesiąc po ostatnim wpisanym odczycie

## [2.1.0] — 2026-05-23

### Dodano
- Nowy moduł `services/ha_stats.py` z funkcjami `get_monthly_energy` i `get_current_month_energy`
- Pobieranie delty miesięcznej energii z **długoterminowych statystyk HA** (`POST /api/services/recorder/get_statistics?return_response`) — fix: restart kontenera nie resetuje już wartości miesięcznych
- Strefa czasowa HA pobierana z `/api/config` (klucz `time_zone`) — granice miesięcy liczone w czasie lokalnym HA (`Europe/Warsaw`), nie UTC
- Automatyczna konwersja Wh → kWh na podstawie `unit_of_measurement` z atrybutów sensora
- Cache zamkniętych miesięcy do `DATA_PATH/stats_cache.json` (persystentny po restarcie), cache bieżącego miesiąca w pamięci z TTL 5 min
- `ha_token` i `ha_url` jako opcjonalne pola schematu add-onu — dla trybu standalone bez Supervisora
- 14 testów jednostkowych pokrywających: normalny miesiąc, miesiąc bieżący, brak danych, sensor Wh, sensor kWh, restart kontenera, persistent cache, TTL cache, błąd API, brak konfiguracji, tryb standalone, oba formaty odpowiedzi, wiele bucketów

### Zmieniono
- `_ha_conn()` zwraca teraz pełny URL API (`http://supervisor/core/api` — base URL już zawiera `/api`)
- Endpointy `/api/ha-solar-fetch`, `/api/ha-grid-fetch`, `/api/ha-test` używają `ha_stats.get_monthly_energy` zamiast `_ha_fetch_energy`
- Brak danych zwraca `None` zamiast błędu tekstowego — UI może rozróżnić "zero" od "brak odczytu"

### Usunięto
- `_ha_fetch_energy()` — zastąpiona przez `ha_stats.get_monthly_energy`
- `_ha_history_delta()` — History API jako fallback zastąpiony przez Statistics API

## [2.0.6] — 2026-05-23

### Naprawiono
- Hamburger menu niewidoczny na mobile — inline `style="display:none"` nadpisywał
  regułę CSS z media query; przeniesiono kontrolę wyświetlania wyłącznie do CSS

## [2.0.5] — 2026-05-23

### Zmieniono
- Dodano GUI konfiguracji addona: pole `default_price_kwh` (float, opcjonalne, domyślnie 0.75)
- Usunięto z run.sh odczyt `ha_token` i `ha_entity` — tokeny HA przechowywane w bazie przez UI apki
- `homeassistant_api: true` dostarcza token Supervisora automatycznie

## [2.0.4] — 2026-05-23

### Naprawiono
- Crash startu w kontenerze HA — config.yaml nie jest kopiowany do obrazu
- Wersja czytana z env APP_VERSION (ustawiane przez bashio::addon.version w run.sh)
- Fallback: lokalnie (standalone) czyta config.yaml jeśli env nie ustawiony

## [2.0.3] — 2026-05-23

### Naprawiono
- Hamburger menu na mobile — sidebar startuje zwinięty, hamburger widoczny od razu
- Wersja w sidebarze dynamicznie czytana z config.yaml (nie hardcoded)

## [2.0.2] — 2026-05-23

### Naprawiono
- Przycisk hamburger niewidoczny na mobile gdy Phosphor CDN niedostępny w HA — zamieniony na Unicode ☰
- CDN Phosphor Icons zmieniony z unpkg na jsdelivr (bardziej dostępny w sieci lokalnej HA)

## [2.0.1] — 2026-05-23

### Naprawiono
- Overlay na mobile pozostawał widoczny po zwinięciu sidebara (odwrócona logika)
- Ikony Phosphor Icons w całym projekcie (zastąpienie emoji)

## [2.0.0] — 2026-05-23

### Dodano
- Phase 0: dependency hygiene, usunięcie Tesla, schema_version
- Phase 1: basic auth, CSRF protection, walidacja odczytów
- Phase 2: kumulatywny net-metering, konfigurowalny współczynnik
- Phase 3: silnik net-billingu, okresy rozliczeniowe, ceny RCE
- Phase 4: prognoza sezonowa, degradacja, eskalacja cen, zakres break-even
- Phase 5: wskaźnik domyślnej ceny, backup/restore, strony coming soon
- Responsywność mobilna (scrollowalne tabele, stacking na małych ekranach)
- Dokumentacja architektoniczna (BUSINESS.md, review-2026-05-12.md)

## [1.12.1] — 2026-05-23

### Dodano
- Backup/restore danych jako JSON na stronie Import (port z v2.0)
- `GET /backup/full` — pełny backup 6 tabel jako plik JSON do pobrania
- `POST /restore` — przywracanie danych z pliku JSON

## [1.10.0] — 2026-04-19

### Dodano
- Przycisk "🔌 Test połączenia" w ustawieniach HA — sprawdza URL/token i pobiera ostatnią miesięczną wartość encji solarnej

### Usunięto
- `default_price_kwh` z konfiguracji add-ona HA (cena kWh ustawiana jest przy odczytach/fakturach)

## [1.9.0] — 2026-04-19

### Dodano
- Pobieranie miesięcznej produkcji solarnej z HA (`GET /api/ha-solar-fetch`) — używa Statistics API HA, zwraca `change` dla encji `total_increasing`
- Pole `ha_solar_entity` w ustawieniach HA (moduł EV)
- Przycisk 🏠 HA przy polu Produkcja w formularzu odczytu

## [1.8.0] — 2026-04-19

### Dodano
- Zarządzanie wieloma pojazdami EV — każdy pojazd ma własne zużycie [kWh/100km] i odpowiednik paliwowy [L/100km]
- Tabela `ev_monthly` — kWh per pojazd per miesiąc, zapisywane przy dodawaniu/edycji odczytu
- Formularz odczytu pokazuje osobne pole kWh dla każdego dodanego pojazdu
- Historia EV pokazuje podział per pojazd w danym miesiącu
- Edycja pojazdu inline (przycisk ✏️ w tabeli pojazdów)
- ROI uwzględnia per-pojazd efficiency przy obliczaniu oszczędności vs paliwo

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
