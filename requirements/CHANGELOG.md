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
