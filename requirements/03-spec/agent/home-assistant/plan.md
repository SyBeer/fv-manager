<!-- GENEROWANE z PRD.md 2026-10-08 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Plan - Integracja z Home Assistant

## Kolejność
1. R-020 Kontrakt: liczniki energii z Home Assistant (wejście) - weryfikacja (działanie obecne v3.4.0 - testy regresji z AC); zależy od: R-001 (T-04)
2. R-015 Integracja z Home Assistant - zmiana (AC-015-2: usunięcie /api/summary, D-030); zależy od: R-020 (T-20)

## Encje do odczytu (02-domain/ENTITIES.md)
## Odczyt miesiąca
Pola: okres (RRRR.MM), produkcja, oddane, pobrane (S-002), cena kWh (S-003, BR-014), faktura - numer i kwota brutto, pomocnicze do odnalezienia faktury, poza obliczeniami (S-003, D-033); dane EV per pojazd (kWh domowe - S-009, km i stan licznika - S-007, ładowanie publiczne kWh i koszt - S-008)
Stany: zapisany (z danymi EV), usunięty
Przejscia: [*] -> zapisany (Właściciel instalacji, po walidacji); zapisany -> zapisany (edycja, Właściciel instalacji); zapisany -> usunięty (Właściciel instalacji)

## Integracje (02-domain/SYSTEMS.md)
| ID | System | Wymiana | Przy awarii | Krytyczna |
|---|---|---|---|---|
| S-002 | Home Assistant | liczniki -> my na żądanie przy wpisie odczytu (wybrany miesiąc); podsumowanie ROI my -> HA - do usunięcia (D-030) | brak danych z HA - komunikat „Brak danych dla <encja> za RRRR-MM”, odczyt nie jest blokowany, właściciel przepisuje liczby ręcznie z aplikacji do zarządzania fotowoltaiką (A-015; nazwa - Q-054 zaparkowane) | nie |
