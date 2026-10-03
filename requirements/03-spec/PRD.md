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
- K-4 Import CSV: cały plik albo nic, raport błędnych wierszy (numer, powód) - D-009, BR-002.
- K-5 „Wyczyść bazę”: tekst wymienia wszystkie usuwane dane + zalecenie kopii /backup/full - D-010.
- K-6 Poprawki tekstów: metodologia.html (pula, RCE i ceny paliwa wpisywane ręcznie, daty net-billingu, analiza wrażliwości), podtytuł tabeli na /roi z faktycznym współczynnikiem zamiast „×0.8” - D-002, D-004, D-005, D-006, D-012.
- K-7 Poprawki README: logika puli (D-002), przykład CSV z separatorem „;” i polskimi nagłówkami (D-009).

## 6. Do przegladu
(lista R/AC dotknietych zmiana zalozen, decyzji albo zakwestionowaniem elementu modelu,
wypelniana automatycznie)
- 2026-10-03: D-002..D-012, A-001, A-002 - brak R w PRD, nic do przeglądu. Kandydaci w §5a.

## 7. Otwarte pytania blokujace
(Q z etykieta blokujaca)
