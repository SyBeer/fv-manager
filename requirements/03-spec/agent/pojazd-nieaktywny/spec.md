<!-- GENEROWANE z PRD.md 2026-10-08 - nie edytuj. Zmiana = zmiana 03-spec/PRD.md + /sdd:spec --agent -->

# Pojazd nieaktywny

### R-019 Pojazd nieaktywny
Opis:              Właściciel instalacji oznacza pojazd jako nieaktywny (np. po sprzedaży albo wymianie auta). Dane pojazdu nieaktywnego dalej wchodzą do oszczędności EV i ROI. Pojazd nieaktywny nie ma pól EV w formularzu odczytu nowego miesiąca; jego zapisane dane są widoczne i edytowalne. Pojazd aktywny, który w miesiącu stał, ma puste pola (D-028).
Zrodlo:            [Biz] board.json, qq041 (D-025); [Biz] board.json, qq045 (D-028)
Zalozenia:         -
Reguly:            -
Status:            zatwierdzone (właściciel instalacji, 2026-10-04)
Wlasciciel:        właściciel instalacji

Kryteria akceptacji:
- AC-019-1: Given pojazd z odczytami EV za 2025.01-2025.12, When właściciel oznacza go jako nieaktywny, Then Oszczędność EV z FV z tych miesięcy dalej wchodzi do ROI (R-006), a karty /ev dalej liczą jego oszczędność.
- AC-019-2: Given pojazdy A (aktywny) i B (nieaktywny), When właściciel otwiera formularz odczytu 2026.10, Then widzi pola EV tylko dla A, a odczyt z pustymi polami EV pojazdu A zapisuje się.
- AC-019-3: Given pojazd B (nieaktywny) z danymi EV za 2025.06, When właściciel edytuje odczyt 2025.06, Then pola EV pojazdu B są widoczne z zapisanymi wartościami.
