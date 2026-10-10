# Śledzenie wymagań - R → AC → zadanie → test

Handover 2026-10-04 do Redmine, projekt FV-Manager (http://192.168.1.4:3001/projects/fv-manager), zadania #17..#34.
Kolumna „Test” wypełniona po budowie v3.3.0 (2026-10-04): testy w `tests/`, nazwa = AC-xxx-n. Ponowny handover 2026-10-04: #20, #27, #28, #29 zaktualizowane (AC-001-5, AC-009-3, AC-009-4, AC-010-3, AC-011-4), nowe #111 R-019 (AC-019-1..AC-019-3) - testy dopisane w v3.4.0.
Odcisk wymagan: sha256:0bad40296613c0343982cd2c070423cfd7ef8e1804700a3a2882fc809861f216

| Wymaganie | Kryterium | Zadanie | Test |
|---|---|---|---|
| R-001 | AC-001-1 | [#20](http://192.168.1.4:3001/issues/20) (T-04) | `test_r001_odczyt.py::test_AC_001_1_poprawny_odczyt_na_liscie` |
| R-001 | AC-001-2 | [#20](http://192.168.1.4:3001/issues/20) (T-04) | `test_r001_odczyt.py::test_AC_001_2_zly_format_okresu` |
| R-001 | AC-001-3 | [#20](http://192.168.1.4:3001/issues/20) (T-04) | `test_r001_odczyt.py::test_AC_001_3_oddane_wieksze_niz_produkcja` |
| R-001 | AC-001-4 | [#20](http://192.168.1.4:3001/issues/20) (T-04) | `test_r001_odczyt.py::test_AC_001_4_przyciski_pobierz_z_ha` |
| R-001 | AC-001-5 | [#20](http://192.168.1.4:3001/issues/20) (T-04) | `test_r001_odczyt.py::test_AC_001_5_km_ze_stanu_licznika` |
| R-002 | AC-002-1 | [#18](http://192.168.1.4:3001/issues/18) (T-02) | `test_r002_r003_rozliczenie.py::test_AC_002_1_net_metering_pula` |
| R-002 | AC-002-2 | [#18](http://192.168.1.4:3001/issues/18) (T-02) | `test_r002_r003_rozliczenie.py::test_AC_002_2_pula_zeruje_sie_w_kwietniu` |
| R-002 | AC-002-3 | [#18](http://192.168.1.4:3001/issues/18) (T-02) | `test_r002_r003_rozliczenie.py::test_AC_002_3_net_billing_320_zl` |
| R-002 | AC-002-4 | [#18](http://192.168.1.4:3001/issues/18) (T-02) | `test_r002_r003_rozliczenie.py::test_AC_002_4_cena_sprzedazy_nadpisuje_rce` |
| R-003 | AC-003-1 | [#19](http://192.168.1.4:3001/issues/19) (T-03) | `test_r002_r003_rozliczenie.py::test_AC_003_1_domyslnie_kwiecien` |
| R-003 | AC-003-2 | [#19](http://192.168.1.4:3001/issues/19) (T-03) | `test_r002_r003_rozliczenie.py::test_AC_003_2_ustawiony_czerwiec_zeruje_pule_w_czerwcu` |
| R-004 | AC-004-1 | [#21](http://192.168.1.4:3001/issues/21) (T-05) | `test_r004_import_csv.py::test_AC_004_1_dziesiec_poprawnych_wierszy` |
| R-004 | AC-004-2 | [#21](http://192.168.1.4:3001/issues/21) (T-05) | `test_r004_import_csv.py::test_AC_004_2_blad_w_wierszu_4_nic_nie_zapisane` |
| R-005 | AC-005-1 | [#23](http://192.168.1.4:3001/issues/23) (T-07) | `test_r005_etapy.py::test_AC_005_1_dodanie_etapu` |
| R-005 | AC-005-2 | [#23](http://192.168.1.4:3001/issues/23) (T-07) | `test_r005_etapy.py::test_AC_005_2_usuniecie_etapu` |
| R-005 | AC-005-3 | [#23](http://192.168.1.4:3001/issues/23) (T-07) | `test_r005_etapy.py::test_AC_005_3_zmiana_kosztu` |
| R-005 | AC-005-4 | [#23](http://192.168.1.4:3001/issues/23) (T-07) | `test_r005_etapy.py::test_AC_005_4_koszt_zero` |
| R-005 | AC-005-5 | [#23](http://192.168.1.4:3001/issues/23) (T-07) | `test_r005_etapy.py::test_AC_005_5_dofinansowanie_ujemne` |
| R-005 | AC-005-6 | [#23](http://192.168.1.4:3001/issues/23) (T-07) | `test_r005_etapy.py::test_AC_005_6_etap_serwisowy_bez_mocy_nie_zmienia_prognozy` |
| R-006 | AC-006-1 | [#24](http://192.168.1.4:3001/issues/24) (T-08) | `test_r006_pozostalo_do_zwrotu.py::test_AC_006_1_pozostalo_bez_ladowania_publicznego` |
| R-006 | AC-006-2 | [#24](http://192.168.1.4:3001/issues/24) (T-08) | `test_r006_pozostalo_do_zwrotu.py::test_AC_006_2_zwrot_osiagniety` |
| R-006 | AC-006-3 | [#24](http://192.168.1.4:3001/issues/24) (T-08) | `test_r006_pozostalo_do_zwrotu.py::test_AC_006_3_inwestycja_schodkowo_wg_dat_etapow`, `test_r006_pozostalo_do_zwrotu.py::test_AC_006_3_wykres_roi_inwestycja_schodkowo` |
| R-006 | AC-006-4 | [#24](http://192.168.1.4:3001/issues/24) (T-08) | `test_r006_pozostalo_do_zwrotu.py::test_AC_006_4_miesiace_do_zwrotu_z_karty` |
| R-006 | AC-006-5 | [#24](http://192.168.1.4:3001/issues/24) (T-08) | `test_r006_pozostalo_do_zwrotu.py::test_AC_006_5_etap_sprzed_pierwszego_odczytu` |
| R-007 | AC-007-1 | [#25](http://192.168.1.4:3001/issues/25) (T-09) | `test_r007_prognoza.py::test_AC_007_1_degradacja_488_1` |
| R-007 | AC-007-2 | [#25](http://192.168.1.4:3001/issues/25) (T-09) | `test_r007_prognoza.py::test_AC_007_2_domyslna_degradacja_w_ustawieniach` |
| R-007 | AC-007-3 | [#25](http://192.168.1.4:3001/issues/25) (T-09) | `test_r007_prognoza.py::test_AC_007_3_tabela_scenariuszy_zwrot_po_36_mies` |
| R-008 | AC-008-1 | [#26](http://192.168.1.4:3001/issues/26) (T-10) | `test_r008_roi_dashboard.py::test_AC_008_1_karty_wykres_wrazliwosc` |
| R-008 | AC-008-2 | [#26](http://192.168.1.4:3001/issues/26) (T-10) | `test_r008_roi_dashboard.py::test_AC_008_2_dashboard_baner_i_12_miesiecy` |
| R-008 | AC-008-3 | [#26](http://192.168.1.4:3001/issues/26) (T-10) | `test_r008_roi_dashboard.py::test_AC_008_3_dashboard_po_36_miesiacach` |
| R-009 | AC-009-1 | [#27](http://192.168.1.4:3001/issues/27) (T-11) | `test_r009_r010_r011_ev.py::test_AC_009_1_pojazd_dodany` |
| R-009 | AC-009-2 | [#27](http://192.168.1.4:3001/issues/27) (T-11) | `test_r009_r010_r011_ev.py::test_AC_009_2_bez_przebiegu_nie_dodany` |
| R-009 | AC-009-3 | [#27](http://192.168.1.4:3001/issues/27) (T-11) | `test_r009_przebieg_startowy.py::test_AC_009_3_tak_przesuwa_stany_licznika_km_bez_zmian`, `::test_AC_009_3_zmiana_bez_wyboru_pokazuje_ostrzezenie_i_nie_zapisuje` |
| R-009 | AC-009-4 | [#27](http://192.168.1.4:3001/issues/27) (T-11) | `test_r009_przebieg_startowy.py::test_AC_009_4_nie_usuwa_nizsze_stany_licznika_dane_ladowania_zostaja` |
| R-010 | AC-010-1 | [#28](http://192.168.1.4:3001/issues/28) (T-12) | `test_r009_r010_r011_ev.py::test_AC_010_1_oszczednosc_ev_z_fv_240_zl` |
| R-010 | AC-010-2 | [#28](http://192.168.1.4:3001/issues/28) (T-12) | `test_r009_r010_r011_ev.py::test_AC_010_2_ladowanie_publiczne_poza_roi` |
| R-010 | AC-010-3 | [#28](http://192.168.1.4:3001/issues/28) (T-12) | `test_r010_cena_paliwa.py::test_AC_010_3_cena_od_wpisu_do_wpisu_tak_samo_ev_i_roi` |
| R-010 | AC-010-4 | [#28](http://192.168.1.4:3001/issues/28) (T-12) | `test_r010_cena_paliwa.py::test_AC_010_4_miesiace_przed_pierwsza_cena_wg_pierwszej`, `::test_AC_010_4_strona_pojazdu_i_karty_ev` |
| R-011 | AC-011-1 | [#29](http://192.168.1.4:3001/issues/29) (T-13) | `test_r009_r010_r011_ev.py::test_AC_011_1_pierwszy_samochod_pyta_o_ceny_paliwa` |
| R-011 | AC-011-2 | [#29](http://192.168.1.4:3001/issues/29) (T-13) | `test_r009_r010_r011_ev.py::test_AC_011_2_sledzenie_wlaczone_pozycja_menu` |
| R-011 | AC-011-3 | [#29](http://192.168.1.4:3001/issues/29) (T-13) | `test_r009_r010_r011_ev.py::test_AC_011_3_sledzenie_wylaczone_brak_pozycji` |
| R-011 | AC-011-4 | [#29](http://192.168.1.4:3001/issues/29) (T-13) | `test_r009_r010_r011_ev.py::test_AC_011_4_wlacz_i_wylacz_sledzenie_pozniej` |
| R-012 | AC-012-1 | [#22](http://192.168.1.4:3001/issues/22) (T-06) | `test_r012_lista_edycja.py::test_AC_012_1_kolumny_listy` |
| R-012 | AC-012-2 | [#22](http://192.168.1.4:3001/issues/22) (T-06) | `test_r012_lista_edycja.py::test_AC_012_2_podglad_roi_przed_i_po` |
| R-013 | AC-013-1 | [#30](http://192.168.1.4:3001/issues/30) (T-14) | `test_r013_r014_dane.py::test_AC_013_1_eksport_csv_12_wierszy` |
| R-013 | AC-013-2 | [#30](http://192.168.1.4:3001/issues/30) (T-14) | `test_r013_r014_dane.py::test_AC_013_2_pelna_kopia_json` |
| R-013 | AC-013-3 | [#30](http://192.168.1.4:3001/issues/30) (T-14) | `test_r013_r014_dane.py::test_AC_013_3_przywrocenie_nadpisuje_dane_ustawienia_zostaja` |
| R-014 | AC-014-1 | [#31](http://192.168.1.4:3001/issues/31) (T-15) | `test_r013_r014_dane.py::test_AC_014_1_wyczysc_baze_usuwa_wszystko_ustawienia_zostaja` |
| R-014 | AC-014-2 | [#31](http://192.168.1.4:3001/issues/31) (T-15) | `test_r013_r014_dane.py::test_AC_014_2_tekst_wymienia_dane_i_zaleca_kopie` |
| R-015 | AC-015-1 | [#32](http://192.168.1.4:3001/issues/32) (T-16) | `test_r015_home_assistant.py::test_AC_015_1_format_wyniku_testu`, `test_r015_home_assistant.py::test_AC_015_1_ekran_dopisuje_okres`, `test_r015_home_assistant.py::test_AC_015_1_bez_polaczenia_komunikat_bledu` |
| R-015 | AC-015-2 | [#32](http://192.168.1.4:3001/issues/32) (T-16) | `test_roi_consistency.py::test_api_summary_matches_roi_page` |
| R-016 | AC-016-1 | [#33](http://192.168.1.4:3001/issues/33) (T-17) | `test_r016_r018_teksty_tesla.py::test_AC_016_1_rce_i_paliwo_recznie` |
| R-016 | AC-016-2 | [#33](http://192.168.1.4:3001/issues/33) (T-17) | `test_r016_r018_teksty_tesla.py::test_AC_016_2_pula_w_cyklu` |
| R-016 | AC-016-3 | [#33](http://192.168.1.4:3001/issues/33) (T-17) | `test_r016_r018_teksty_tesla.py::test_AC_016_3_wrazliwosc_7_cen_i_wspolczynnik` |
| R-016 | AC-016-4 | [#33](http://192.168.1.4:3001/issues/33) (T-17) | `test_r016_r018_teksty_tesla.py::test_AC_016_4_readme_przyklad_csv` |
| R-016 | AC-016-5 | [#33](http://192.168.1.4:3001/issues/33) (T-17) | `test_r016_r018_teksty_tesla.py::test_AC_016_5_metodologia_bez_dat_ustawowych` |
| R-017 | AC-017-1 | [#17](http://192.168.1.4:3001/issues/17) (T-01) | `test_r017_okresy_i_rce.py::test_AC_017_1_bez_okresow_net_metering` |
| R-017 | AC-017-2 | [#17](http://192.168.1.4:3001/issues/17) (T-01) | `test_r017_okresy_i_rce.py::test_AC_017_2_okres_net_billing_od_2024_07` |
| R-017 | AC-017-3 | [#17](http://192.168.1.4:3001/issues/17) (T-01) | `test_r017_okresy_i_rce.py::test_AC_017_3_ostatnia_cena_rce_do_konca_miesiaca` |
| R-017 | AC-017-4 | [#17](http://192.168.1.4:3001/issues/17) (T-01) | `test_r017_okresy_i_rce.py::test_AC_017_4_po_usunieciu_ceny_wraca_poprzednia` |
| R-018 | AC-018-1 | [#34](http://192.168.1.4:3001/issues/34) (T-18) | `test_r016_r018_teksty_tesla.py::test_AC_018_1_brak_tesla_w_kodzie` |
| R-018 | AC-018-2 | [#34](http://192.168.1.4:3001/issues/34) (T-18) | `test_r016_r018_teksty_tesla.py::test_AC_018_2_readme_i_changelog` |
| R-018 | AC-018-3 | [#34](http://192.168.1.4:3001/issues/34) (T-18) | `test_r016_r018_teksty_tesla.py::test_AC_018_3_migracja_nie_rusza_danych` |
| R-019 | AC-019-1 | [#111](http://192.168.1.4:3001/issues/111) (T-19) | `test_r019_pojazd_nieaktywny.py::test_AC_019_1_nieaktywny_dalej_w_roi_i_kartach_ev` |
| R-019 | AC-019-2 | [#111](http://192.168.1.4:3001/issues/111) (T-19) | `test_r019_pojazd_nieaktywny.py::test_AC_019_2_formularz_nowego_miesiaca_bez_pol_nieaktywnego`, `::test_AC_019_2_odczyt_z_pustymi_polami_aktywnego_zapisuje_sie` |
| R-019 | AC-019-3 | [#111](http://192.168.1.4:3001/issues/111) (T-19) | `test_r019_pojazd_nieaktywny.py::test_AC_019_3_edycja_odczytu_pokazuje_dane_nieaktywnego`, `::test_AC_019_3_zapis_edycji_zachowuje_dane_nieaktywnego` |

## Zasada dla dev
Zmiana wymagania po przekazaniu = zmiana `03-spec/PRD.md` (przez właściciela) i ponowny handover (/sdd:spec --agent, /sdd:handover) - nigdy zadanie „z boku” w Redmine.
