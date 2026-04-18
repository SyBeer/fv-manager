# FV Manager

Aplikacja do zarządzania efektywnością kosztową instalacji fotowoltaicznej.

Śledzi przepływy energii, oblicza ROI, obsługuje kilka faz inwestycji i integruje się z Home Assistant jako panel w sidebarze.

## Funkcje

- **Dashboard** — podsumowanie ostatnich miesięcy, baner ROI
- **Odczyty** — miesięczne dane produkcji, oddania i pobrania z sieci
- **ROI** — skumulowane oszczędności vs inwestycja, analiza wrażliwości, wykres
- **Inwestycje** — wieloetapowe nakłady (panele, inwerter, magazyn energii itp.)
- **EV** — oszczędności samochodów elektrycznych vs paliwo (Tesla Model Y, BMW i3)
- **Import** — z pliku Excel (arkusz „Moja instalacja")

## Uruchomienie lokalne

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=src uvicorn src.main:app --reload --port 8010
```

Aplikacja dostępna pod `http://localhost:8010`.

## Home Assistant Add-on

Repozytorium zawiera HA Add-on (`ha-addon/`). Aby zainstalować:

1. W HA: **Settings → Add-ons → Add-on Store → ⋮ → Repositories**
2. Dodaj: `https://github.com/SyBeer/fv-manager`
3. Zainstaluj **FV Manager** z listy
4. Skonfiguruj opcje (cena kWh, token HA do EV)
5. Uruchom — panel pojawi się w sidebarze HA

Baza danych SQLite przechowywana w `/data/fv.db` — uwzględniana w backupach HA.

## Konfiguracja (.env)

| Zmienna | Opis | Domyślnie |
|---|---|---|
| `DEFAULT_PRICE_KWH` | Cena kWh do kalkulacji ROI | `0.75` |
| `PORT` | Port aplikacji | `8010` |
| `HA_URL` | URL Home Assistant | `http://homeassistant.local:8123` |
| `HA_TOKEN` | Long-lived access token HA | — |
| `HA_ENTITY` | Encja z kWh EV | `sensor.ev_energy_total` |

## Stack

- Python 3.13, FastAPI, Jinja2, aiosqlite, openpyxl
- SQLite (baza lokalna / `/data/fv.db` w HA)
