<!-- GENEROWANE z PRD.md 2026-10-10 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Plan - Eksport, kopia, czyszczenie

## Kolejność
1. R-013 Eksport i kopia danych - weryfikacja (działanie obecne - testy regresji z AC, poprawka różnic); zależy od: -
2. R-014 Wyczyść bazę - weryfikacja (działanie obecne - testy regresji z AC, poprawka różnic); zależy od: R-013 (T-14)

## Encje do odczytu (02-domain/ENTITIES.md)
## Odczyt miesiąca
Pola: okres (RRRR.MM), produkcja, oddane, pobrane (S-002), cena kWh (S-003, BR-014), faktura - numer i kwota brutto, pomocnicze do odnalezienia faktury, poza obliczeniami (S-003, D-033); dane EV per pojazd (kWh domowe - S-009, km i stan licznika - S-007, ładowanie publiczne kWh i koszt - S-008)
Stany: zapisany (z danymi EV), usunięty
Przejscia: [*] -> zapisany (Właściciel instalacji, po walidacji); zapisany -> zapisany (edycja, Właściciel instalacji); zapisany -> usunięty (Właściciel instalacji)
Zrodlo: [App] kod-v3.2.4-2026-09-27.md, Walidacja odczytów, main.py /odczyty/nowy; [Dok] README.md, /odczyty/{id}/usun
Zakwestionowane:
## Etap inwestycji
Pola: data, opis, koszt brutto (zł), moc kWp (opcjonalna), notatki
Stany: zapisany, zmieniony, usunięty
Przejscia: [*] -> zapisany (Właściciel instalacji); zapisany -> zmieniony (Właściciel instalacji); zapisany/zmieniony -> usunięty (Właściciel instalacji)
Zrodlo: [Dok] README.md, investments, /inwestycje/nowa; [App] src/main.py update_investment, delete_investment
Zakwestionowane:
## Pojazd
Pola: nazwa, zużycie kWh/100 km, spalanie odpowiednika l/100 km, rodzaj paliwa, przebieg startowy (wymagany), okres posiadania (od-do), notatki
Stany: dodany, nieaktywny, usunięty
Przejscia: [*] -> dodany (Właściciel instalacji, tylko z przebiegiem startowym); dodany -> nieaktywny (Właściciel instalacji, D-025; dane dalej w oszczędnościach; bez pól EV w formularzu odczytu nowego miesiąca, D-028); dodany / nieaktywny -> usunięty (Właściciel instalacji, D-034; domyślnie dane miesięczne zostają i liczą się jak dane pojazdu nieaktywnego; skasowanie danych miesięcznych tylko po wyraźnym potwierdzeniu)
Zrodlo: [App] src/main.py create_vehicle (/ev/pojazdy/nowy), update_vehicle, delete_vehicle; [Biz] D-025, D-034
Zakwestionowane:
## Cena paliwa
Pola: data, cena, typ paliwa, źródło
Stany: zapisana
Przejscia: [*] -> zapisana (Właściciel instalacji, wpis ręczny, D-006)
Zrodlo: [App] kod-v3.2.4-2026-09-27.md, Ceny paliwa; [Biz] D-006; obowiązuje od daty wpisu do następnego wpisu (D-023); miesiące przed pierwszą ceną - wg pierwszej ceny (D-029)
Zakwestionowane:
## Okres rozliczeniowy
Pola: data startu, model rozliczeń (net-metering / net-billing)
Stany: ustawiony
Przejscia: [*] -> ustawiony (Właściciel instalacji, D-004)
Zrodlo: [App] kod-v3.2.4-2026-09-27.md, Net-billing i RCE; [Biz] D-004; miesiąc liczony wg okresu obowiązującego 1. dnia miesiąca (D-032, BR-013)
Zakwestionowane:
