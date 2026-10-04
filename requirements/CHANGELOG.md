# Changelog wymagan
# format: YYYY-MM-DD | skill | co | zrodlo
2026-09-27 | init | utworzono strukture, poziom light | -
2026-09-27 | init | zmiana poziomu light -> full (PRD.md zamiast SPEC.md) | -
2026-09-27 | intake | przebieg pierwszy: 4 zrodla w INDEX.md, 10 pytan sprzeczne (Q-001..Q-010) | BUSINESS.md, review-2026-05-12.md, README.md, metodologia.html
2026-09-27 | interview | odczyt kodu v3.2.4 jako nowe zrodlo [App] w INDEX; nowe luki Q-012, Q-013 | kod-v3.2.4-2026-09-27.md
2026-09-27 | config | zmiana SDD.yaml: backlog | panel
2026-09-27 | interview | D-001: BUSINESS.md i review-2026-05-12.md -> dotyczy innej wersji v1.12.0; Q-007 odpowiedziane; Q-003, Q-008, Q-009, Q-010 sprzeczne -> otwarte | [Biz] session-2026-09-27.md
2026-10-03 | board sync | D-002..D-012 (Q-001..Q-006, Q-008, Q-010, Q-012..Q-014 odpowiedziane), A-001, A-002 (Q-009), Q-014 z karteczki człowieka | [Biz] board.json, warsztat 2026-10-03
2026-10-03 | board sync | GLOSSARY: 9 haseł (pula, cykl, okres, net-metering, net-billing, RCE, cena paliwa, 2× oszczędność EV); RULES: BR-001, BR-002 | D-002..D-009
2026-10-03 | board sync | PRD §4 poza zakresem, §5a kandydaci K-1..K-7, §6; board.json: ref i synced | D-002..D-012
2026-10-03 | interview | Q-011 odpowiedziane bez treści o cel (historia zmian nieistotna); nowe Q-015 o cel produktu | [Biz] właściciel, sesja live 2026-10-03
2026-10-03 | interview | Q-015 odpowiedziane; A-003 (cel: miesięczny podgląd ROI i oszczędności EV) niepotwierdzone | [Biz] właściciel, sesja live 2026-10-03
2026-10-03 | sdd:board | tablica: 7 procesów aplikacji, 47 karteczek, hot Q-016, Q-017 | [App] kod-v3.2.4-2026-09-27.md, [Dok] README.md, D-002..D-012
2026-10-04 | sdd:board | tor „Inwestycje i ROI”: aktor p46, edycja/usunięcie etapu p47-p48, zdarzenie „Zwrot osiągnięty” p49, hot h03-h08 (Q-018..Q-023) | [App] src/main.py, src/services/calculations.py, src/services/forecast.py
2026-10-04 | interview | QUESTIONS: dopisane Q-016, Q-017 (były tylko na tablicy); nowe Q-018..Q-023 o ROI i inwestycje | [App] src/services/forecast.py, calc_roi; luka w README.md, BUSINESS.md
2026-10-04 | sdd:board | stan karteczek wg nowej zasady (file = gdzie jest): 20 ✓ (BR-001/002, D-004/006/007/008/010/012, Q-016..Q-023), 37 tylko na tablicy - zdjete file 'docelowe'; p10,p15,p20,p26,p27,p29,p31,p33,p41 dostaly ref D-xxx | board.json, DECISIONS.md, RULES.md, QUESTIONS.md
2026-10-04 | sdd:board sync | ACTORS: Właściciel instalacji; ENTITIES: Odczyt miesiąca, Etap inwestycji, Zwrot inwestycji, Pojazd, Cena paliwa, Okres rozliczeniowy; ✓ na tablicy p01, p46, p06, p09, p17, p25, p28, p32, p48, p49 | board.json; [App] kod-v3.2.4-2026-09-27.md, [Dok] README.md
2026-10-04 | sdd:board sync | RULES: BR-003..BR-009 (BR-009 techniczna) z karteczek p04,p11,p13,p18,p19,p24,p44; ASSUMPTIONS: A-004..A-010 niepotwierdzone; ✓ na tablicy | [App] kod-v3.2.4-2026-09-27.md, [Dok] README.md
2026-10-04 | interview | QUESTIONS: Q-024..Q-030 potwierdzające A-004..A-010 (reguły BR-003..BR-009) | ASSUMPTIONS.md, RULES.md
2026-10-04 | interview | A-004 potwierdzone (Q-024 odpowiedziane); kaskada: BR-003, brak R | [Biz] session-2026-10-04.md, Q-024
2026-10-04 | interview | A-005 potwierdzone (Q-025 odpowiedziane; współczynnik 0,8 z umowy właściciela); kaskada: BR-004, brak R | [Biz] session-2026-10-04.md, Q-025
2026-10-04 | interview | Q-026 zaparkowane (nie blokuje go-live; net-billing jak w v3.2.4); A-006 bez zmian - niepotwierdzone | [Biz] session-2026-10-04.md, Q-026
2026-10-04 | interview | A-007 potwierdzone częściowo (pozostało do zwrotu; EV = tylko ładowanie domowe, D-008), Q-027 odpowiedziane; miesiące do zwrotu dalej w Q-018; kaskada: BR-006, brak R | [Biz] session-2026-10-04.md, Q-027
2026-10-04 | interview | D-013 (zwrot po 36 mies. podawany liczbą miesięcy), Q-020 odpowiedziane, nowe Q-031; BR-007 uzupełniona; PRD: K-8, §6 wpis (brak R) | [Biz] session-2026-10-04.md, Q-028
2026-10-04 | interview | Q-028 zaparkowane (nie blokuje go-live; tabela scenariuszy jak w v3.2.4, właściciel jej nie rozumie); A-008 niepotwierdzone | [Biz] session-2026-10-04.md, Q-028
2026-10-04 | interview | A-009 potwierdzone (Q-029 odpowiedziane; bez przebiegu startowego brak rejestracji samochodu); kaskada: BR-008, brak R | [Biz] session-2026-10-04.md, Q-029
2026-10-04 | interview | A-010 potwierdzone częściowo (Q-030 odpowiedziane; mechanizm API zostaje [Dok]); kaskada: BR-009, brak R | [Biz] session-2026-10-04.md, Q-030
2026-10-04 | sdd:board sync | PRD §5a: kandydaci K-9..K-17 z 19 karteczek cmd/rm/ev, p36 -> K-4; tablica 57/57 ✓ | board.json; [App] kod-v3.2.4-2026-09-27.md, [Dok] README.md
2026-10-04 | spec | GLOSSARY: 9 haseł zatwierdzone (paczki rozliczenia + EV/paliwo) - zatwierdził właściciel instalacji | [Biz] czat sesji 2026-10-04
2026-10-04 | spec | PRD: §1-3, R-001..R-004 (robocze) z K-9, K-11, K-1, K-4; RULES/ASSUMPTIONS: kolumny Wymagania; tablica: ref R-xxx | [Biz] czat sesji 2026-10-04 (zgoda właściciela)
2026-10-04 | spec | PRD: R-005..R-008 (robocze) z K-8, K-12, K-13, K-15; nowe A-011 niepotwierdzone (R-008); tablica: ref R-xxx | [Biz] czat sesji 2026-10-04 (zgoda właściciela)
2026-10-04 | spec | PRD: R-009..R-012 (robocze) z K-2, K-3, K-10, K-14; nowe A-012 niepotwierdzone (R-012); tablica: ref R-xxx | [Biz] czat sesji 2026-10-04 (zgoda właściciela)
2026-10-04 | spec | PRD: R-013..R-016 (robocze) z K-5, K-6, K-7, K-16, K-17; nowe A-013 niepotwierdzone (R-015); wszyscy kandydaci K-1..K-17 zmapowani na R | [Biz] czat sesji 2026-10-04 (zgoda właściciela)
2026-10-04 | config | zmiana SDD.yaml: backlog, redmine_url, redmine_project | panel
2026-10-04 | spec | PRD: R-001..R-016 zatwierdzone (właściciel instalacji, „zatwierdzam wszystkie”); R-002, R-007, R-008, R-012, R-015, R-016 stoją na A niepotwierdzonych | [Biz] czat sesji 2026-10-04
2026-10-04 | config | zmiana SDD.yaml: redmine_project | panel
2026-10-04 | config | zmiana SDD.yaml: redmine_ac_field "Kryteria akceptacji" (pole wlasne Redmine, wymagane przy zmianie statusu) | Claude, na prosbe usera
2026-10-04 | validate | raport 04-validation/validate-2026-10-04.md: 0 BLOCK, WARN: AC-007-1, AC-008-1, R-008/R-012/R-015/R-016 na A [Dok]/[AI], 10 pojęć spoza słownika; gotowość 69% (11/16) | PRD.md, GLOSSARY.md, ASSUMPTIONS.md, QUESTIONS.md, INDEX.md
2026-10-04 | sdd:board sync | brak zmian z tablicy (brak nowych karteczek, odpowiedzi i edycji); 57/57 w plikach; wszystkie otwarte Q na tablicy | board.json
2026-10-04 | sdd:board | p18, p19: treść zgodna z BR-006/A-007 i BR-007/D-013; 'updated' z przyszłości (12:00) -> 'created' na kartkach pasa Inwestycje i ROI | RULES.md, ASSUMPTIONS.md, DECISIONS.md
2026-10-04 | interview | D-014 (koszt etapu ≥ 0), BR-010, Q-021 odpowiedziane, nowe Q-032; R-005 + AC-005-4/5, PRD §6; tablica h09 (Q-032) | [Biz] session-2026-10-04.md, Q-021
2026-10-04 | interview | D-015 (data etapu uwzględniana w ROI; dziś błąd), Q-019 odpowiedziane; BR-006 uzupełniona; R-006 + AC-006-3, R-008 w PRD §6 | [Biz] session-2026-10-04.md, Q-019
2026-10-04 | interview | D-016 (dofinansowanie = etap z ujemnym kosztem; zmienia D-014), BR-010 przeredagowana, Q-022 odpowiedziane; R-005 AC-005-5 zmienione, PRD §6 | [Biz] session-2026-10-04.md, Q-022
2026-10-04 | interview | D-017 (wszystkie wydatki jako etapy inwestycji), Q-023 odpowiedziane; R-005 + AC-005-6, PRD §4 i §6 | [Biz] session-2026-10-04.md, Q-023
2026-10-04 | interview | D-018 (termin zwrotu = karta mies. do ROI), Q-018 odpowiedziane; BR-006 źródło [Biz], A-007 uzupełnione; R-006 + AC-006-4, PRD §6 | [Biz] session-2026-10-04.md, Q-018
2026-10-04 | interview | D-019 (zwrot za N mies. w tabeli per scenariusz i na dashboardzie), Q-031 odpowiedziane; BR-007; R-007 AC-007-3, R-008 + AC-008-3, PRD §6 | [Biz] session-2026-10-04.md, Q-031
2026-10-04 | spec | PRD: R-017 Okresy rozliczeniowe i ceny RCE (zatwierdzone, właściciel instalacji); BR-005 -> R-017; Q-033 zaparkowane (brak RCE = 0 zł); tablica p31, p33 -> R-017, p35 -> R-003 | [Biz] czat sesji 2026-10-04; [App] src/main.py:1838-1900
2026-10-04 | validate | przebieg 2: 0 BLOCK; WARN: AC-007-1, AC-008-1, R-008/R-012/R-015/R-016 na A [Dok]/[AI], 11 pojęć spoza słownika; gotowość 71% (12/17) | PRD.md, RULES.md, DECISIONS.md, QUESTIONS.md, GLOSSARY.md
2026-10-04 | validate | AC-007-1, AC-008-1 doprecyzowane (zgoda właściciela); gotowość 76% (13/17), 0 BLOCK | PRD.md
2026-10-04 | spec --agent | 03-spec/agent: constitution.md + 7 funkcji (rozliczenia, odczyty, inwestycje-roi, ev, dane, home-assistant, teksty) - spec/plan/tasks, 17 zadań T-01..T-17 z R-001..R-017 | PRD.md
2026-10-04 | handover | próba push do Redmine (fv-manager): błąd 422 przy T-01 (projekt/typ/status puste) - nic nie założono; plik 04-validation/redmine-2026-10-04.json gotowy | Redmine API
2026-10-04 | handover | Redmine fv-manager: 17 zadań #17..#33 (T-01..T-17) dla R-001..R-017, relacje 'poprzedza' z plan.md; TRACEABILITY.md: 52 AC | 03-spec/agent/*/tasks.md
2026-10-04 | sdd:board sync | brak zmian z tablicy od commita 8098422; wszystkie karteczki w plikach; otwarte Q-016, Q-017, Q-032 na tablicy | board.json
2026-10-04 | sdd:board | p46, p47, p48, p49: 'created'/'updated' 12:00 (wpisane przed czasem) -> 2026-10-04T08:59:48 (commit d3c9041, najpóźniejszy możliwy moment powstania); panel pokazywał je jako zmienione po sync | git log board.json
2026-10-04 | sdd:board sync | odpowiedź z tablicy h02 (Q-017, właściciel instalacji): 'nie wiem' -> Q-017 zaparkowane (nie blokuje go-live; import jak w v3.2.5); h02 synced | board.json, session-2026-10-04.md
2026-10-04 | validate | odświeżenie po zaparkowaniu Q-017: R bez zmian, 0 BLOCK, gotowość 76%; nowy odcisk w raporcie i TRACEABILITY | QUESTIONS.md
2026-10-04 | sdd:board sync | odpowiedzi z tablicy h01 (Q-016), h09 (Q-032) -> D-020 (wycofanie Tesla Fleet API) + R-018, D-021 (data etapu sprzed odczytów) + AC-006-5; BR-006; PRD §4, §6; 0 otwartych Q | [Biz] board.json h01, h09
2026-10-04 | spec --agent | regeneracja: R-018 -> nowa funkcja tesla-wycofanie (T-18); inwestycje-roi i odczyty zaktualizowane (D-020, D-021) | PRD.md
2026-10-04 | handover | Redmine fv-manager: nowe #34 (T-18, R-018), zaktualizowane #17..#33; TRACEABILITY.md: 56 AC; nowy odcisk w TRACEABILITY i raporcie validate | 03-spec/agent/*/tasks.md
2026-10-04 | validate | raport: linia gotowości w formacie czytanym przez panel (78%); usunięta prognoza '94%' z zaleceń, którą panel brał za wynik | progress.js:262
2026-10-04 | interview | QUESTIONS: Q-034..Q-037 potwierdzające A-011, A-012, A-013, A-001 (WARN 8: R-008, R-012, R-015, R-016) | validate-2026-10-04.md
2026-10-04 | interview | A-011 potwierdzone (Q-034: wykres na /roi, miesiące na dashboardzie); kaskada: R-008 bez WARN 8, AC bez zmian | [Biz] session-2026-10-04.md, Q-034
2026-10-04 | interview | A-012 potwierdzone (Q-035: kwota i wpływ na ROI przy edycji); kaskada: R-012 bez WARN 8, AC bez zmian | [Biz] session-2026-10-04.md, Q-035
2026-10-04 | interview | A-013 potwierdzone (Q-036: encje z panelu Energy, Supervisor API, test połączenia; sensor nieużywany - zostaje jako regresja); R-015 AC-015-1 doprecyzowane, PRD §6 | [Biz] session-2026-10-04.md, Q-036
2026-10-04 | interview | D-022 (metodologia bez dat ustawowych; zmienia D-005), Q-037 odpowiedziane; A-001 poprawione wg źródeł z internetu [Dok], bez wymagań zależnych; R-016 bez A-001 + AC-016-5, PRD §6 | [Biz] session-2026-10-04.md, Q-037
2026-10-04 | spec --agent | regeneracja po A-013, D-022: home-assistant (R-015 AC-015-1), teksty (R-016 AC-016-5) | PRD.md
2026-10-04 | validate | przebieg 4: 0 BLOCK, WARN tylko słownik (11 pojęć); gotowość 100% (18/18) | PRD.md, ASSUMPTIONS.md, DECISIONS.md, QUESTIONS.md
2026-10-04 | handover | Redmine: zaktualizowane #32 (R-015), #33 (R-016); TRACEABILITY.md: 57 AC; nowy odcisk | 03-spec/agent/*/tasks.md
2026-10-04 | domain | GLOSSARY: 11 nowych haseł zatwierdzonych (Odczyt miesiąca, Autokonsumpcja, Etap inwestycji, Dofinansowanie, Łączna inwestycja, Pozostało do zwrotu, Oszczędność PV miesiąca, Zwrot inwestycji, Degradacja paneli, Przebieg startowy, Ładowanie publiczne) - zatwierdził właściciel instalacji | [Biz] czat sesji 2026-10-04
2026-10-04 | spec --agent | constitution.md zregenerowane (słownik 20 haseł) | GLOSSARY.md
2026-10-04 | validate | przebieg 5: 0 BLOCK, 0 WARN, gotowość 100% (18/18); nowy odcisk w raporcie i TRACEABILITY | GLOSSARY.md
2026-10-04 | build | v3.3.0: R-001..R-018 zrealizowane (Redmine #17..#34 -> Code review), 189 testów; decyzje budowy B-01..B-23 w 04-validation/build-2026-10-04.md; TRACEABILITY: kolumna Test wypełniona | PRD.md, 03-spec/agent
2026-10-04 | interview | proces „Pojazdy EV i paliwo”: luki z kodu v3.3.1 na tablicy (p50..p59) i pytania Q-038..Q-043 (Q-038 sprzeczne: dwie reguły ceny paliwa) | [App] src/main.py
2026-10-04 | board sync | odpowiedzi Q-038..Q-043 z tablicy -> D-023 (cena paliwa od wpisu do wpisu), D-024 (śledzenie cen w każdej chwili), D-025 (pojazd nieaktywny), D-026 (km ze stanu licznika); BR-011, BR-012, A-014; PRD: AC-010-3, AC-011-4, R-019 robocze, §6; ENTITIES: Pojazd nieaktywny, Śledzenie cen paliwa; nowe Q-044, Q-045; tablica p50..p61 zsynchronizowana | [Biz] board.json qq038..qq043
2026-10-04 | spec | D-027 (zmiana przebiegu startowego z wyborem przesunięcia stanów licznika); A-014 obalone; BR-012 nowe brzmienie; PRD: R-001 AC-001-5, R-009 AC-009-3/AC-009-4, R-019 bez zaślepki AC-019-2, §5a K-18/K-19, §6; tablica p51 | [Biz] session-2026-10-04.md
2026-10-04 | spec --agent | 03-spec/agent zregenerowane z 18 R zatwierdzonych (R-019 robocze pominięte); ev: T-11 R-009 Z (AC-009-3/4), T-12 R-010 B (AC-010-3); odczyty: AC-001-5; typy zadań wg stanu v3.3.1 | PRD.md
2026-10-04 | validate | przebieg 6: 0 BLOCK, 1 WARN (W9: Pojazd nieaktywny, Stan licznika), gotowość 95% (18/19, R-019 robocze); TRACEABILITY: 6 nowych AC; BR-012 Wymagania = R-009 | PRD.md
2026-10-04 | board sync | odpowiedź Q-045 z tablicy -> D-028 (pojazd nieaktywny bez pól EV w formularzu nowego miesiąca); R-019 AC-019-2, AC-019-3, zatwierdzone; ENTITIES Pojazd; PRD §6; tablica p60 | [Biz] board.json qq045
2026-10-04 | spec --agent | 03-spec/agent zregenerowane z 19 R zatwierdzonych; nowa funkcja pojazd-nieaktywny (T-19 R-019, Z) | PRD.md
2026-10-04 | validate | przebieg 7: 0 BLOCK, 1 WARN (W9: Pojazd nieaktywny, Stan licznika), gotowość 100% (19/19); TRACEABILITY: AC-019-2, AC-019-3, T-19 | PRD.md
2026-10-04 | domain | GLOSSARY: nowe hasła robocze Pojazd, Pojazd nieaktywny, Stan licznika, Śledzenie cen paliwa (test spójności: pojęcia z RULES/ENTITIES/PRD bez hasła) | D-007, D-024..D-028
2026-10-04 | domain | zatwierdzone hasła: Pojazd, Pojazd nieaktywny, Stan licznika, Śledzenie cen paliwa; Przebieg startowy - definicja uzupełniona o zmianę wartości (D-027) | właściciel instalacji
2026-10-04 | spec --agent | constitution.md zregenerowane (słownik 24 hasła) | GLOSSARY.md
2026-10-04 | validate | przebieg 8: 0 BLOCK, 0 WARN, gotowość 100% (19/19); nowy odcisk w raporcie i TRACEABILITY | GLOSSARY.md
2026-10-04 | handover | Redmine: #20, #27, #28, #29 zaktualizowane (nowe AC), nowe #111 [R-019] Pojazd nieaktywny; 19 R pokrytych zadaniami #17..#34, #111; statusy bez zmian | 03-spec/agent
2026-10-04 | interview | Q-044 -> D-029 (miesiące przed pierwszą ceną paliwa wg pierwszej ceny); R-010 AC-010-4; ENTITIES Cena paliwa; PRD §6; tablica p54 | [Biz] session-2026-10-04.md
2026-10-04 | spec --agent | ev/tasks.md: T-12 R-010 z AC-010-4 (D-029) | PRD.md
2026-10-04 | validate | przebieg 9: 0 BLOCK, 0 WARN, gotowość 100% (19/19), 66 AC, brak otwartych Q; TRACEABILITY: AC-010-4 | PRD.md
2026-10-04 | handover | Redmine #28 [R-010] zaktualizowane (AC-010-4, D-029); status bez zmian | 03-spec/agent
2026-10-04 | build | v3.4.0: R-009 (#27), R-010 (#28), R-019 (#111), testy AC-001-5 (#20), AC-011-4 (#29); przegląd architektów przed i po budowie, decyzje B-24..B-37; TRACEABILITY: kolumna Test dla 9 nowych AC; 210 testów | PRD.md, 03-spec/agent
2026-10-04 | build | v3.4.0 sprawdzona przez właściciela instalacji w HA po aktualizacji: „zgadza się wszystko” | build-2026-10-04.md
2026-10-04 | handover | Redmine: uzupełnione obowiązkowe pole „Link do środowiska UAT” w 16 zadaniach (#17-#23, #25-#29, #31, #32, #34, #111); statusy bez zmian | prośba właściciela instalacji
