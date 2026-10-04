# PRD - <nazwa modulu>

## 1. Cel
Po co to robimy. Jedno zdanie o problemie, jedno o efekcie.

## 2. Aktorzy
(odwolanie do 02-domain/ACTORS.md)

## 3. Zakres
## 4. Poza zakresem
(rownie wazne jak zakres)
- Strony /bateria i /ogrzewanie - makiety przyszłych funkcji (D-011).
- Uwierzytelnianie ponad istniejący opcjonalny Basic Auth (FV_AUTH_PASSWORD), dopóki tryb standalone nie jest wystawiony poza sieć domową (A-002, niepotwierdzone).
- Automatyczne pobieranie cen RCE i cen paliwa - wpisywane ręcznie (D-004, D-006).
- Wariant procentowy w analizie wrażliwości - 7 stałych cen (D-012).

## 5. Wymagania

### R-001 <tytul>
Opis:
Zrodlo:            [Biz]/[App]/[Dok]/[AI] <plik z INDEX.md>[, sekcja/wiersz]
Zalozenia:         A-xxx
Reguly:            BR-xxx
Status:            robocze | do przegladu | zatwierdzone
Wlasciciel:        (rola)

Kryteria akceptacji:
- AC-001-1: Given <stan>, When <zdarzenie>, Then <wynik>

## 5a. Kandydaci na wymagania (robocze, bez numerów R)
Z warsztatu 2026-10-03. Numer R nadaje /sdd:spec po zgodzie właściciela.
- K-1 Ustawienie miesiąca startu cyklu rozliczeniowego (domyślnie kwiecień) - D-003, BR-001.
- K-2 Przy dodawaniu pierwszego samochodu pytanie: czy śledzić ceny paliwa - D-007.
- K-3 Pozycja menu „Ceny paliwa” pod EV, widoczna tylko gdy śledzenie włączone - D-007.
- K-4 Import CSV: cały plik albo nic, raport błędnych wierszy (numer, powód) - D-009, BR-002; tablica: p36.
- K-5 „Wyczyść bazę”: tekst wymienia wszystkie usuwane dane + zalecenie kopii /backup/full - D-010.
- K-6 Poprawki tekstów: metodologia.html (pula, RCE i ceny paliwa wpisywane ręcznie, daty net-billingu, analiza wrażliwości), podtytuł tabeli na /roi z faktycznym współczynnikiem zamiast „×0.8” - D-002, D-004, D-005, D-006, D-012.
- K-7 Poprawki README: logika puli (D-002), przykład CSV z separatorem „;” i polskimi nagłówkami (D-009).
- K-8 Prognoza ROI: wykres 36 mies.; gdy zwrot później - liczba miesięcy do zwrotu słownie (np. „zwrot za 53 mies.”) - D-013, BR-007.
Z /sdd:board sync 2026-10-04 (as-built, bez potwierdzenia [Biz] - numer R po zgodzie właściciela):
- K-9 Formularz odczytu miesiąca: produkcja, oddane, pobrane, cena kWh, faktura; dane EV per pojazd (kWh domowe, km, stan licznika, ładowanie publiczne); przycisk „pobierz z HA” za okres - BR-003, A-004, A-010; tablica: p02, p03, p05; źródło: [App] kod-v3.2.4-2026-09-27.md, main.py:645, 690-720; templates/reading_form.html:266-280.
- K-10 Lista odczytów (produkcja, autokonsumpcja, oddane, pobrane, zużycie, oszczędności) i edycja odczytu z podglądem ROI przed/po zmianie - -; tablica: p07, p08; źródło: [Dok] README.md, Odczyty (/odczyty), /api/roi-preview.
- K-11 Oszczędność PV miesiąca (kWh i zł) liczona wg modelu rozliczeń okresu - BR-001, BR-004, BR-005; tablica: p14; źródło: [App] kod-v3.2.4-2026-09-27.md, enrich_readings_sequence.
- K-12 Etapy inwestycji: dodaj, edytuj, usuń (koszt, data, moc) - Q-019, Q-021; tablica: p16, p47; źródło: [Dok] README.md, investments; [App] src/main.py /inwestycje/{id}/edytuj, /usun.
- K-13 Ekran ROI (karty, wykres skumulowanych oszczędności vs inwestycja, tabela wrażliwości, prognoza break-even) i dashboard (baner ROI + 12 ostatnich miesięcy) - BR-006, BR-007, D-012, D-013, Q-018, Q-028, Q-031; tablica: p21, p22; źródło: [Dok] README.md, ROI (/roi), Dashboard (/).
- K-14 Pojazdy: dodanie (nazwa, zużycie kWh/100 km, spalanie odpowiednika, paliwo, przebieg startowy) oraz karty /ev i strona pojazdu - BR-008, D-008; tablica: p23, p30; źródło: [App] src/main.py:1562; [Dok] README.md, EV (/ev).
- K-15 Ustawienie degradacji paneli (% rocznie, domyślnie 0,6) - BR-007, A-008; tablica: p34; źródło: [App] src/main.py:1888.
- K-16 Eksport odczytów do CSV; pobranie i przywrócenie pełnej kopii JSON (przywrócenie nadpisuje dane, ustawienia zostają) - D-010; tablica: p38, p39, p40; źródło: [Dok] README.md, /odczyty/export.csv; [App] src/main.py:1161.
- K-17 Integracja HA: encje (produkcja PV, pobór, oddanie), test połączenia, sensor podsumowania ROI (/api/summary) - BR-009, A-002; tablica: p42, p43, p45; źródło: [Dok] README.md, Home Assistant, /api/ha-test, API JSON.

## 6. Do przegladu
(lista R/AC dotknietych zmiana zalozen, decyzji albo zakwestionowaniem elementu modelu,
wypelniana automatycznie)
- 2026-10-03: D-002..D-012, A-001, A-002 - brak R w PRD, nic do przeglądu. Kandydaci w §5a.
- 2026-10-04: D-013 (BR-007), A-004/A-005/A-007/A-009/A-010 potwierdzone - brak R w PRD, nic do przeglądu. Kandydat K-8 w §5a.

## 7. Otwarte pytania blokujace
(Q z etykieta blokujaca)
