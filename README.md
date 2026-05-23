# FV Manager v2.0.1

Aplikacja webowa do zarządzania efektywnością kosztową instalacji fotowoltaicznej.
Śledzi przepływy energii, oblicza ROI, integruje się z Home Assistant i Tesla Fleet API.
Dostępna jako standalone FastAPI app oraz jako HA Add-on (ingress panel w sidebarze).

---

## Założenia

- Dane źródłowe pochodzą z **licznika dwukierunkowego** (forward = pobrane z sieci, reverse = oddane do sieci)
- Model oszczędności oparty na **starym net-meteringu** (80% oddanej energii wraca do puli rozliczeniowej)
- ROI = suma (oszczędności FV + oszczędności EV) vs suma nakładów inwestycyjnych
- Break-even: ekstrapolacja liniowa na podstawie historycznej średniej miesięcznej
- Obsługa **wielu etapów inwestycji** (panele, inwerter, magazyn, ładowarka EV)
- Obsługa **wielu pojazdów EV** z osobnym zużyciem miesięcznym per pojazd

---

## Stack techniczny

| Warstwa | Technologia |
|---------|-------------|
| Backend | Python 3.13, FastAPI, aiosqlite |
| Frontend | Jinja2, Tailwind CSS (dark theme), Chart.js |
| Baza danych | SQLite (`data/fv.db` lokalnie, `/data/fv.db` w HA) |
| Deployment | Standalone (uvicorn) lub HA Add-on (Docker, ingress) |
| Testy | pytest |
| Import danych | CSV (upload) lub API (HA, Tesla) |

---

## Struktura projektu

```
fv-manager/
├── src/
│   ├── main.py                     # FastAPI app — endpointy, helpery, integracje
│   ├── utils/
│   │   └── db.py                   # SQLite init i connection (aiosqlite)
│   └── services/
│       ├── calculations.py         # Kalkulacje: przepływy energii, ROI, EV savings
│       └── importer.py             # Import z Excela (legacy, nieużywany)
├── templates/
│   ├── base.html                   # Layout: sidebar collapsible, mobile overlay
│   ├── dashboard.html              # Dashboard — ostatnie 12 miesięcy + baner ROI
│   ├── readings.html               # Lista odczytów miesięcznych
│   ├── reading_form.html           # Formularz nowego/edytowanego odczytu
│   ├── investments.html            # Inwestycje — lista + formularz inline
│   ├── investment_form.html        # Formularz edycji inwestycji
│   ├── roi.html                    # Analiza ROI: wykres, sensitivity table
│   ├── ev.html                     # EV: pojazdy, oszczędności, ceny paliw, integracje
│   └── import.html                 # Import CSV + danger zone
├── tests/
│   ├── conftest.py                 # sys.path setup
│   └── test_calculations.py        # Testy jednostkowe kalkulacji
├── data/fv.db                      # SQLite (gitignored)
├── project.json                    # Metadane HQAI
├── requirements.txt
├── config.yaml                     # HA Add-on manifest
├── Dockerfile                      # HA Add-on container
├── run.sh                          # HA startup (bashio config, INGRESS_PATH)
├── CHANGELOG.md
└── README.md
```

---

## Schemat bazy danych

### `investments` — etapy inwestycji

```sql
id           INTEGER PRIMARY KEY AUTOINCREMENT
date         TEXT NOT NULL           -- YYYY-MM-DD
description  TEXT NOT NULL           -- "Panele 10 kWp", "Inwerter", itp.
cost_pln     REAL NOT NULL           -- koszt brutto w PLN
power_kwp    REAL                    -- moc (opcjonalna, do statystyk)
notes        TEXT
```

### `readings` — miesięczne odczyty licznika

```sql
id                   INTEGER PRIMARY KEY AUTOINCREMENT
period               TEXT NOT NULL UNIQUE    -- "2024.06"
year                 INTEGER NOT NULL
month                INTEGER NOT NULL
days                 INTEGER                 -- liczba dni w miesiącu
production_kwh       REAL NOT NULL           -- produkcja PV (z inwertera)
sent_to_grid_kwh     REAL NOT NULL           -- oddane do sieci (licznik 2.8.0 reverse)
taken_from_grid_kwh  REAL NOT NULL           -- pobrane z sieci (licznik 1.8.0 forward)
ev_kwh               REAL                   -- legacy: zużycie EV (przed multi-vehicle)
price_per_kwh        REAL                   -- cena z faktury
invoice_number       TEXT
invoice_gross        REAL                   -- kwota brutto faktury PLN
notes                TEXT
```

### `vehicles` — pojazdy elektryczne

```sql
id                            INTEGER PRIMARY KEY AUTOINCREMENT
name                          TEXT NOT NULL               -- "Tesla Model Y"
efficiency_kwh_per_100km      REAL DEFAULT 16.0
fuel_consumption_l_per_100km  REAL DEFAULT 10.0           -- odpowiednik benzynowy
fuel_type                     TEXT DEFAULT 'PB95'
notes                         TEXT
```

### `ev_monthly` — zużycie EV per pojazd per miesiąc

```sql
id          INTEGER PRIMARY KEY AUTOINCREMENT
period      TEXT NOT NULL                -- "2024.06"
vehicle_id  INTEGER NOT NULL REFERENCES vehicles(id)
kwh         REAL NOT NULL
UNIQUE(period, vehicle_id)
```

### `ev_settings` — konfiguracja EV + integracje (singleton, id=1)

```sql
id                             INTEGER PRIMARY KEY CHECK (id = 1)
efficiency_kwh_per_100km       REAL DEFAULT 16.0
fuel_consumption_l_per_100km   REAL DEFAULT 10.0
annual_km                      REAL DEFAULT 25000
fuel_type                      TEXT DEFAULT 'PB95'
ha_url                         TEXT       -- URL instancji HA
ha_token                       TEXT       -- Long-lived access token
ha_entity                      TEXT       -- legacy EV entity
ha_solar_entity                TEXT       -- sensor produkcji PV
ha_grid_consumed_entity        TEXT       -- sensor poboru z sieci
ha_grid_returned_entity        TEXT       -- sensor oddania do sieci
tesla_access_token             TEXT
tesla_site_id                  TEXT
tesla_api_base                 TEXT       -- np. "https://fleet-api.prd.eu.vn.cloud.tesla.com"
```

### `fuel_prices` — historia cen paliw

```sql
id              INTEGER PRIMARY KEY AUTOINCREMENT
date            TEXT NOT NULL
price_per_liter REAL NOT NULL
fuel_type       TEXT DEFAULT 'PB95'    -- PB95, PB98, ON
source          TEXT                   -- Orlen, PKN, itp.
```

---

## Logika kalkulacji

### Przepływy energii (`calc_monthly`)

Z trzech wartości licznika rekonstruowane są wszystkie przepływy:

```
production       = 500 kWh   (inwerter)
sent_to_grid     = 300 kWh   (licznik reverse 2.8.0)
taken_from_grid  = 100 kWh   (licznik forward 1.8.0)

auto_consumption  = production - sent_to_grid     = 200 kWh  (zużyte wprost z PV)
total_consumed    = auto_consumption + taken       = 300 kWh  (łączne zużycie domu)
net_metering_pool = sent_to_grid × 0.80           = 240 kWh  (80% zwrotu — stary net-metering)
savings_kwh       = auto_consumption + min(pool, taken_from_grid)
                  = 200 + min(240, 100)            = 300 kWh
savings_pln       = savings_kwh × price_per_kwh   = 225 zł   (jeśli cena znana)
```

Zwraca: `auto_consumption`, `total_consumed`, `net_metering_pool`, `savings_kwh`, `savings_pln`, `production_value_pln`

### ROI i break-even (`calc_roi`)

```
total_fv_savings    = Σ savings_pln (wszystkie miesiące)
total_ev_savings    = Σ ev_savings_pln (multi-vehicle lub legacy)
total_savings       = total_fv_savings + total_ev_savings
remaining           = total_investment - total_savings
avg_monthly         = total_savings / months_count          ← historyczna średnia
months_to_roi       = remaining / avg_monthly               ← ekstrapolacja liniowa
roi_achieved        = remaining ≤ 0
```

Ograniczenie: ekstrapolacja nie uwzględnia sezonowości, wzrostu cen prądu ani degradacji paneli.

### Oszczędności EV (`calc_ev_savings`)

Porównanie kosztu jazdy EV vs równoważny samochód benzynowy:

```
km_driven       = (ev_kwh / efficiency_kwh_per_100km) × 100
fuel_cost       = (km_driven / 100) × fuel_l_per_100km × fuel_price
electricity_cost = ev_kwh × price_per_kwh
ev_net_savings  = fuel_cost - electricity_cost
```

### Analiza wrażliwości (`roi_sensitivity`)

Oblicza break-even dla cen kWh: 0.50, 0.60, 0.70, 0.80, 0.90, 1.00, 1.10, 1.20 zł.

### Wzbogacenie odczytów o EV (`_ev_enrich`)

Dwie ścieżki (kolejność priorytetu):
1. **Multi-vehicle** (preferred): dla każdego odczytu sumuje `calc_ev_savings` per pojazd z `ev_monthly`
2. **Legacy fallback**: jeśli brak pojazdów — używa `readings.ev_kwh` + `ev_settings`

---

## Endpointy

### Widoki HTML

| URL | Metoda | Opis |
|-----|--------|------|
| `/` | GET | Dashboard — 12 ostatnich miesięcy, baner ROI |
| `/odczyty` | GET | Lista wszystkich odczytów miesięcznych |
| `/odczyty/nowy` | GET/POST | Formularz nowego odczytu |
| `/odczyty/{id}/edytuj` | GET/POST | Edycja odczytu + ev_monthly |
| `/odczyty/{id}/usun` | POST | Usuń odczyt |
| `/odczyty/export.csv` | GET | Export CSV wszystkich odczytów |
| `/inwestycje` | GET | Lista inwestycji + formularz inline |
| `/inwestycje/nowa` | POST | Dodaj inwestycję |
| `/inwestycje/{id}/edytuj` | GET/POST | Edycja inwestycji |
| `/inwestycje/{id}/usun` | POST | Usuń inwestycję |
| `/roi` | GET | ROI: wykres skumulowany, sensitivity table |
| `/ev` | GET | EV savings, pojazdy, ceny paliw, konfiguracja HA/Tesla |
| `/ev/settings` | POST | Zapisz konfigurację HA/Tesla |
| `/ev/pojazdy/nowy` | POST | Dodaj pojazd |
| `/ev/pojazdy/{id}/edytuj` | POST | Edytuj pojazd |
| `/ev/pojazdy/{id}/usun` | POST | Usuń pojazd + jego ev_monthly |
| `/ev/fuel-price` | POST | Dodaj cenę paliwa |
| `/ev/fuel-price/{id}/usun` | POST | Usuń cenę paliwa |
| `/import` | GET | Strona importu CSV |

### API JSON

| URL | Metoda | Opis |
|-----|--------|------|
| `/api/summary` | GET | ROI summary dla Home Assistant sensor |
| `/api/roi-preview` | POST | ROI before/after dla modal edycji odczytu |
| `/api/ha-test` | GET | Test połączenia HA + ostatnia produkcja |
| `/api/ha-solar-fetch?period=YYYY.MM` | GET | Pobierz produkcję PV z HA za miesiąc |
| `/api/ha-grid-fetch?period=YYYY.MM&direction=consumed\|returned` | GET | Pobierz dane sieci z HA |
| `/api/tesla-sites` | GET | Lista energy sites z Tesla Fleet API |
| `/api/tesla-charging-fetch?period=YYYY-MM` | GET | Pobierz kWh ładowania z Tesla za miesiąc |
| `/import/template.csv` | GET | Pobierz szablon CSV do importu |
| `/import/csv` | POST | Import z pliku CSV (INSERT OR IGNORE) |
| `/admin/clear-db` | POST | Usuń wszystkie odczyty (danger zone) |

---

## Integracje

### Home Assistant

W trybie HA Add-on aplikacja używa `SUPERVISOR_TOKEN` z ENV (nie konfiguracji).
URL bazowy: `http://supervisor/core`.

**Pobieranie danych energii (`_ha_fetch_energy`):**
1. Próba: `POST /api/recorder/statistics_during_period` (Statistics API — dla historycznych danych)
2. Fallback: `GET /api/history/period` (History API — tylko ostatnie ~10 dni)
3. Obsługuje konwersję Wh → kWh (gdy unit_class = `energy`)

Encje do skonfigurowania w `/ev` → sekcja Home Assistant:
- `ha_solar_entity` — sensor produkcji PV (np. `sensor.solaredge_energy_today`)
- `ha_grid_consumed_entity` — sensor poboru z sieci (forward, 1.8.0)
- `ha_grid_returned_entity` — sensor oddania do sieci (reverse, 2.8.0)

### Tesla Fleet API

Endpoint: `/api/1/energy_sites/{site_id}/telemetry_history?kind=charge`
Timezone: `Europe/Warsaw`

Konfiguracja w `/ev` → sekcja Tesla:
- `tesla_access_token` — token z developer.tesla.com
- `tesla_site_id` — wykrywany automatycznie przez `/api/tesla-sites`
- `tesla_api_base` — region-specific, np. `https://fleet-api.prd.eu.vn.cloud.tesla.com`

---

## Import danych

### Format CSV

```
period,production_kwh,sent_to_grid_kwh,taken_from_grid_kwh,price_per_kwh,ev_kwh,notes
2024.01,350.5,200.0,80.0,0.75,,
2024.02,280.0,150.0,120.5,0.78,45.2,z fakturą
```

- `period`: format `YYYY.MM` (wymagane)
- `production_kwh`, `sent_to_grid_kwh`, `taken_from_grid_kwh`: wymagane
- `price_per_kwh`, `ev_kwh`, `notes`: opcjonalne
- Duplikaty pomijane (`INSERT OR IGNORE` po `period`)

Szablon do pobrania: `GET /import/template.csv`

---

## Widoki — co pokazują

### Dashboard (`/`)
- Baner ROI: zielony (osiągnięty) lub żółty z progress bar i liczbą miesięcy do break-even
- Tabela ostatnich 12 miesięcy: Okres, Produkcja, Autokonsumpcja, Oddane, Pobrane, Zużycie, Oszczędności PLN

### ROI (`/roi`)
- Karty: łączna inwestycja, oszczędności FV+EV (breakdown), pozostało, śr./mies., mies. do ROI, produkcja łączna
- Wykres Chart.js: skumulowane oszczędności (FV + linia EV) vs linia inwestycji
- Tabela sensitivity: 8 cen kWh → oszczędności, pozostało, miesięcy, status ✅/⏳

### Odczyty (`/odczyty`)
- Kolumny: Okres, Produkcja, Autokons., Oddane, Pobrane, Zużycie, EV kWh (legacy), Oszczędności, Cena/kWh
- Akcje: edycja z modal ROI preview (porównanie BEFORE/AFTER zmiany)
- Export CSV jednym klikiem

### EV (`/ev`)
- Summary cards: łączne oszczędności EV PLN, łączne km, litry zaoszczędzone, ostatnia cena paliwa
- Tabela miesięczna: kWh, km (est.), koszt paliwa (gdyby), koszt prądu, oszczędność netto, litry
- Zarządzanie pojazdami (CRUD inline)
- Historia cen paliw (CRUD inline)
- Konfiguracja HA (3 entity inputs + przycisk test połączenia)
- Konfiguracja Tesla (token + autodiscovery site ID)

---

## Uruchomienie

### Lokalnie

```bash
cd fv-manager
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src uvicorn src.main:app --reload --port 8010
```

Aplikacja: `http://localhost:8010`

### Home Assistant Add-on

1. HA → **Settings → Add-ons → Add-on Store → ⋮ → Repositories**
2. Dodaj: `https://github.com/SyBeer/fv-manager`
3. Zainstaluj **FV Manager** → konfiguruj → uruchom
4. Panel pojawia się w sidebarze HA
5. Baza danych w `/data/fv.db` (uwzględniana w backupach HA)

Zmienne środowiskowe HA (przez `bashio::config`):
- `default_price_kwh` → `DEFAULT_PRICE_KWH`
- `ha_token` → `HA_TOKEN`
- `DATA_PATH` → `/data`
- `INGRESS_PATH` → automatycznie z `bashio::addon.ingress_entry`

---

## Testy

```bash
cd fv-manager
source .venv/bin/activate
pytest tests/ -v
```

Pokrycie: `calc_monthly` (basic, bez ceny), `calc_roi` (nie osiągnięty, osiągnięty), `roi_sensitivity`.
