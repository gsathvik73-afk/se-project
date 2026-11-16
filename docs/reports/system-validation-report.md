# System Validation Report

Executed at 2026-11-15T18:27:04.789597+00:00.

297 passed; 0 failed; 2 skipped.

Full case identifiers, durations and captured output are in the adjacent JUnit XML.

| Test | Result | Seconds |
|---|---|---:|
| tests.test_core.test_registration_duplicate_and_login | PASS | 1.021 |
| tests.test_core.test_registration_validation[body0] | PASS | 0.034 |
| tests.test_core.test_registration_validation[body1] | PASS | 0.032 |
| tests.test_core.test_registration_validation[body2] | PASS | 0.032 |
| tests.test_core.test_registration_validation[body3] | PASS | 0.033 |
| tests.test_core.test_logout_revokes_replayed_cookie | PASS | 0.511 |
| tests.test_core.test_csrf_required | PASS | 0.025 |
| tests.test_core.test_categories_add_rename_and_defaults | PASS | 0.533 |
| tests.test_core.test_foreign_category_budget_and_transaction_isolation | PASS | 1.065 |
| tests.test_core.test_budget_persistence_upsert_and_totals | PASS | 0.780 |
| tests.test_core.test_alert_thresholds[2500-none] | PASS | 0.523 |
| tests.test_core.test_alert_thresholds[2250-warning] | PASS | 0.524 |
| tests.test_core.test_alert_thresholds[1800-warning] | PASS | 0.521 |
| tests.test_core.test_alert_thresholds[1799-over] | PASS | 0.522 |
| tests.test_core.test_chart_breakdown_six_months_and_empty_state | PASS | 0.538 |
| tests.test_core.test_invalid_budgets_not_saved[0] | PASS | 0.517 |
| tests.test_core.test_invalid_budgets_not_saved[-1] | PASS | 0.517 |
| tests.test_core.test_invalid_budgets_not_saved[NaN] | PASS | 0.517 |
| tests.test_core.test_invalid_budgets_not_saved[Infinity] | PASS | 0.517 |
| tests.test_core.test_invalid_budgets_not_saved[0.001] | PASS | 0.518 |
| tests.test_core.test_invalid_budgets_not_saved[10000000000] | PASS | 0.517 |
| tests.test_core.test_invalid_budgets_not_saved[abc] | PASS | 0.518 |
| tests.test_core.test_invalid_month[2026-13] | PASS | 0.508 |
| tests.test_core.test_invalid_month[2026-1] | PASS | 0.506 |
| tests.test_core.test_invalid_month[0000-01] | PASS | 0.509 |
| tests.test_core.test_invalid_month[bad] | PASS | 0.508 |
| tests.test_core.test_year_rollover_trend | PASS | 0.513 |
| tests.test_core.test_user_text_escaped | PASS | 0.519 |
| tests.test_core.test_anonymous_pages_redirect[/categories] | PASS | 0.025 |
| tests.test_core.test_anonymous_pages_redirect[/budgets] | PASS | 0.025 |
| tests.test_core.test_anonymous_pages_redirect[/transactions] | PASS | 0.024 |
| tests.test_core.test_anonymous_pages_redirect[/dashboard] | PASS | 0.023 |
| tests.test_core.test_invalid_json_payload | PASS | 0.033 |
| tests.test_core.test_budget_and_category_html_forms | PASS | 0.535 |
| tests.test_csv_export.test_rpt01_download_headers | PASS | 1.003 |
| tests.test_csv_export.test_rpt01_header_row_and_rows_match_the_filter | PASS | 1.003 |
| tests.test_csv_export.test_rpt01_other_users_rows_never_exported | PASS | 1.003 |
| tests.test_csv_export.test_rpt01_formula_cells_are_neutralised | PASS | 1.004 |
| tests.test_csv_export.test_rpt01_no_matches_gives_header_only | PASS | 1.005 |
| tests.test_csv_export.test_rpt01_from_after_to_is_rejected | PASS | 1.052 |
| tests.test_csv_export.test_rpt01_anonymous_cannot_export | PASS | 0.024 |
| tests.test_csv_export.test_rpt01_export_includes_matches_beyond_first_page | PASS | 0.679 |
| tests.test_nonfunctional.test_perf01_pages_load_within_3_seconds_with_5000_transactions | PASS | 2.521 |
| tests.test_nonfunctional.test_perf02_twenty_concurrent_users_no_errors_no_mixed_data | PASS | 8.841 |
| tests.test_nonfunctional.test_rel01_saved_data_survives_a_server_restart | PASS | 0.792 |
| tests.test_nonfunctional.test_rel01_failed_save_leaves_no_partial_record_and_can_be_retried | PASS | 0.519 |
| tests.test_nonfunctional.test_rel01_failed_save_shows_friendly_message | PASS | 0.509 |
| tests.test_nonfunctional.test_ux01_validation_errors_are_next_to_the_field_and_say_how_to_fix_it | PASS | 0.034 |
| tests.test_nonfunctional.test_ux01_budget_errors_name_the_field_and_the_fix | PASS | 0.514 |
| tests.test_nonfunctional.test_ux01_dashboard_links_to_add_expense | PASS | 0.521 |
| tests.test_nonfunctional.test_port01_every_page_is_responsive[/login] | PASS | 0.505 |
| tests.test_nonfunctional.test_port01_every_page_is_responsive[/register] | PASS | 0.505 |
| tests.test_nonfunctional.test_port01_every_page_is_responsive[/dashboard] | PASS | 0.520 |
| tests.test_nonfunctional.test_port01_every_page_is_responsive[/transactions] | PASS | 0.531 |
| tests.test_nonfunctional.test_port01_every_page_is_responsive[/budgets] | PASS | 0.520 |
| tests.test_nonfunctional.test_port01_every_page_is_responsive[/categories] | PASS | 0.510 |
| tests.test_nonfunctional.test_port01_dashboard_table_scrolls_inside_a_wrapper | PASS | 0.521 |
| tests.test_nonfunctional.test_port01_stylesheet_has_mobile_layout_for_360px | PASS | 0.001 |
| tests.test_nonfunctional.test_port01_charts_use_a_local_script_that_works_in_all_browsers | PASS | 0.522 |
| tests.test_regressions.test_category_ids_cannot_be_coerced_or_overflow[True] | PASS | 0.515 |
| tests.test_regressions.test_category_ids_cannot_be_coerced_or_overflow[False] | PASS | 0.516 |
| tests.test_regressions.test_category_ids_cannot_be_coerced_or_overflow[1.9_0] | PASS | 0.517 |
| tests.test_regressions.test_category_ids_cannot_be_coerced_or_overflow[1.9_1] | PASS | 0.515 |
| tests.test_regressions.test_category_ids_cannot_be_coerced_or_overflow[9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999] | PASS | 0.517 |
| tests.test_regressions.test_category_ids_cannot_be_coerced_or_overflow[9223372036854775808] | PASS | 0.519 |
| tests.test_regressions.test_six_month_trend_cannot_underflow_calendar[/api/dashboard] | PASS | 0.506 |
| tests.test_regressions.test_six_month_trend_cannot_underflow_calendar[/dashboard] | PASS | 0.507 |
| tests.test_regressions.test_six_month_trend_cannot_underflow_calendar[/budgets] | PASS | 0.509 |
| tests.test_regressions.test_filter_amounts_cannot_overflow_database[1e1000000-min_amount] | PASS | 0.509 |
| tests.test_regressions.test_filter_amounts_cannot_overflow_database[1e1000000-max_amount] | PASS | 0.510 |
| tests.test_regressions.test_filter_amounts_cannot_overflow_database[Infinity-min_amount] | PASS | 0.509 |
| tests.test_regressions.test_filter_amounts_cannot_overflow_database[Infinity-max_amount] | PASS | 0.509 |
| tests.test_regressions.test_filter_amounts_cannot_overflow_database[-1-min_amount] | PASS | 0.508 |
| tests.test_regressions.test_filter_amounts_cannot_overflow_database[-1-max_amount] | PASS | 0.510 |
| tests.test_regressions.test_filter_amounts_cannot_overflow_database[10000000000-min_amount] | PASS | 0.508 |
| tests.test_regressions.test_filter_amounts_cannot_overflow_database[10000000000-max_amount] | PASS | 0.507 |
| tests.test_regressions.test_json_http_errors_never_leak_html_or_internal_details[/missing-404] | PASS | 0.024 |
| tests.test_regressions.test_json_http_errors_never_leak_html_or_internal_details[/register-400] | PASS | 0.024 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-001-01-unique account] | PASS | 0.106 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-001-02-normalized duplicate] | PASS | 0.051 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-001-03-empty name] | PASS | 0.048 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-001-04-malformed email] | PASS | 0.049 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-001-05-short password] | PASS | 0.049 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-001-06-eight character boundary] | PASS | 0.051 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-001-07-long name] | PASS | 0.050 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-001-08-multibyte password bound] | PASS | 0.051 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-002-01-correct credentials] | PASS | 0.054 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-002-02-wrong password] | PASS | 0.056 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-002-03-unknown email] | PASS | 0.051 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-002-04-normalized email] | PASS | 0.054 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-002-05-missing password] | PASS | 0.056 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-002-06-nonstring password] | PASS | 0.054 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-002-07-lock after five failures] | PASS | 0.082 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-002-08-session cookie flags] | PASS | 0.056 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-003-01-logout success] | PASS | 0.053 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-003-02-old cookie replay] | PASS | 0.054 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-003-03-anonymous dashboard] | PASS | 0.056 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-003-04-anonymous transactions] | PASS | 0.054 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-003-05-anonymous categories] | PASS | 0.053 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-003-06-anonymous budgets] | PASS | 0.055 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-003-07-anonymous API] | PASS | 0.054 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-003-08-logout requires CSRF] | PASS | 0.048 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-004-01-list excludes foreign row] | PASS | 0.098 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-004-02-detail blocks foreign row] | PASS | 0.070 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-004-03-update blocks foreign row] | PASS | 0.074 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-004-04-delete blocks foreign row] | PASS | 0.073 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-004-05-dashboard excludes foreign income] | PASS | 0.078 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-004-06-CSV excludes foreign note] | PASS | 0.073 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-004-07-private categories hidden] | PASS | 0.141 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-004-08-foreign budget scope blocked] | PASS | 0.074 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-005-01-smallest amount] | PASS | 0.054 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-005-02-integer amount] | PASS | 0.057 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-005-03-decimal amount] | PASS | 0.055 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-005-04-optional note] | PASS | 0.059 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-005-05-note retained] | PASS | 0.056 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-005-06-payment mode retained] | PASS | 0.057 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-005-07-today date] | PASS | 0.057 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-005-08-maximum amount] | PASS | 0.055 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-006-01-income saved] | PASS | 0.055 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-006-02-source retained] | PASS | 0.057 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-006-03-balance updated] | PASS | 0.063 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-006-04-no category required] | PASS | 0.056 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-006-05-no payment required] | PASS | 0.055 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-006-06-smallest income] | PASS | 0.057 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-006-07-past date accepted] | PASS | 0.056 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-006-08-empty source rejected] | PASS | 0.054 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-007-01-zero rejected] | PASS | 0.065 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-007-02-negative rejected] | PASS | 0.063 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-007-03-text rejected] | PASS | 0.065 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-007-04-blank rejected] | PASS | 0.063 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-007-05-future rejected] | PASS | 0.064 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-007-06-third decimal rejected] | PASS | 0.062 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-007-07-infinity rejected] | PASS | 0.063 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-007-08-positive boundary accepted] | PASS | 0.055 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-008-01-amount updated] | PASS | 0.057 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-008-02-note updated] | PASS | 0.129 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-008-03-date updated] | PASS | 0.057 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-008-04-payment updated] | PASS | 0.056 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-008-05-category updated] | PASS | 0.060 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-008-06-income source updated] | PASS | 0.057 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-008-07-invalid edit rolled back] | PASS | 0.056 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-008-08-dashboard recalculated] | PASS | 0.067 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-009-01-confirmation page] | PASS | 0.055 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-009-02-cancel preserves] | PASS | 0.059 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-009-03-confirmed form delete] | PASS | 0.054 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-009-04-JSON delete] | PASS | 0.055 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-009-05-deleted detail absent] | PASS | 0.056 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-009-06-dashboard recalculated] | PASS | 0.063 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-009-07-foreign delete blocked] | PASS | 0.079 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-009-08-missing id safe] | PASS | 0.055 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-010-01-inclusive date range] | PASS | 0.054 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-010-02-category filter] | PASS | 0.056 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-010-03-minimum amount] | PASS | 0.054 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-010-04-maximum amount] | PASS | 0.055 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-010-05-ascending amount] | PASS | 0.052 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-010-06-descending amount] | PASS | 0.052 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-010-07-empty results] | PASS | 0.055 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-010-08-invalid range rejected] | PASS | 0.053 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-011-01-eight defaults] | PASS | 0.050 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-011-02-add custom] | PASS | 0.057 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-011-03-rename custom] | PASS | 0.061 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-011-04-default immutable] | PASS | 0.053 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-011-05-duplicate rejected] | PASS | 0.056 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-011-06-case duplicate rejected] | PASS | 0.054 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-011-07-blank rejected] | PASS | 0.053 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-011-08-select custom in expense] | PASS | 0.136 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-012-01-overall saved] | PASS | 0.054 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-012-02-category saved] | PASS | 0.056 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-012-03-upsert overall] | PASS | 0.072 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-012-04-upsert category] | PASS | 0.077 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-012-05-separate month] | PASS | 0.068 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-012-06-zero rejected] | PASS | 0.060 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-012-07-negative rejected] | PASS | 0.061 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-012-08-foreign category blocked] | PASS | 0.074 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-013-01-spent exact] | PASS | 0.064 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-013-02-remaining exact] | PASS | 0.063 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-013-03-percentage exact] | PASS | 0.065 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-013-04-category spending] | PASS | 0.066 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-013-05-income excluded] | PASS | 0.066 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-013-06-negative remaining] | PASS | 0.063 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-013-07-no budget empty] | PASS | 0.057 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-013-08-zero spending] | PASS | 0.064 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-014-01-below 80] | PASS | 0.062 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-014-02-at 80] | PASS | 0.064 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-014-03-above 80] | PASS | 0.063 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-014-04-at 100] | PASS | 0.063 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-014-05-above 100] | PASS | 0.062 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-014-06-entry allowed over budget] | PASS | 0.069 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-014-07-category alert] | PASS | 0.064 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-014-08-month isolation] | PASS | 0.063 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-015-01-income total] | PASS | 0.135 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-015-02-expense total] | PASS | 0.055 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-015-03-net balance] | PASS | 0.058 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-015-04-empty month] | PASS | 0.056 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-015-05-month isolation] | PASS | 0.058 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-015-06-after expense create] | PASS | 0.063 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-015-07-after income create] | PASS | 0.063 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-015-08-invalid month] | PASS | 0.052 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-016-01-category sum] | PASS | 0.057 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-016-02-three categories] | PASS | 0.059 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-016-03-six months] | PASS | 0.059 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-016-04-zero months] | PASS | 0.058 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-016-05-selected month included] | PASS | 0.059 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-016-06-year rollover] | PASS | 0.057 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-016-07-empty category list] | PASS | 0.058 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-016-08-underflow rejected] | PASS | 0.062 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-017-01-CSV header] | PASS | 0.054 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-017-02-owner isolation] | PASS | 0.076 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-017-03-date filter] | PASS | 0.054 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-017-04-amount sorting] | PASS | 0.056 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-017-05-empty export] | PASS | 0.053 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-017-06-CSV escaping] | PASS | 0.059 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-017-07-formula neutralization] | PASS | 0.062 |
| tests.test_requirement_scenarios.test_functional_scenario[SEB-F-017-08-all pages exported] | PASS | 0.060 |
| tests.test_security.test_sec01_session_cookie_flags | PASS | 0.509 |
| tests.test_security.test_sec01_no_external_resources | PASS | 0.571 |
| tests.test_security.test_sec01_security_headers | PASS | 0.032 |
| tests.test_security.test_sec01_deployed_http_redirects_to_https | SKIP | 0.000 |
| tests.test_security.test_sec01_deployed_tls12_ok_and_valid_certificate | SKIP | 0.000 |
| tests.test_security.test_sec02_hashes_are_salted_and_passwords_never_stored | PASS | 1.307 |
| tests.test_security.test_sec02_responses_never_contain_hash | PASS | 0.567 |
| tests.test_security.test_sec02_correct_password_accepted_wrong_rejected | PASS | 0.975 |
| tests.test_security.test_sec03_foreign_transaction_is_404_and_looks_like_missing | PASS | 1.028 |
| tests.test_security.test_sec03_foreign_category_cannot_be_renamed | PASS | 0.999 |
| tests.test_security.test_sec03_default_category_cannot_be_renamed | PASS | 1.000 |
| tests.test_security.test_sec03_foreign_category_cannot_be_used_for_a_budget | PASS | 1.004 |
| tests.test_security.test_sec03_anonymous_gets_no_data | PASS | 0.994 |
| tests.test_security.test_sec03_foreign_transaction_cannot_be_changed[put-body0] | PASS | 0.999 |
| tests.test_security.test_sec03_foreign_transaction_cannot_be_changed[delete-None] | PASS | 0.998 |
| tests.test_security.test_sec03_foreign_category_cannot_be_used_on_new_expense | PASS | 0.996 |
| tests.test_security.test_sec04_sql_injection_cannot_bypass_login[' OR '1'='1' --] | PASS | 0.508 |
| tests.test_security.test_sec04_sql_injection_cannot_bypass_login[admin'--] | PASS | 0.508 |
| tests.test_security.test_sec04_sql_injection_cannot_bypass_login[a@example.com' OR '1'='1] | PASS | 0.508 |
| tests.test_security.test_sec04_sql_text_is_stored_as_plain_text_and_tables_survive | PASS | 0.514 |
| tests.test_security.test_sec04_sql_in_ids_and_filters_is_rejected | PASS | 0.984 |
| tests.test_security.test_sec04_stored_xss_is_escaped_everywhere[<script>alert('xss')</script>] | PASS | 0.587 |
| tests.test_security.test_sec04_stored_xss_is_escaped_everywhere[<img src=x onerror=alert(1)>] | PASS | 0.585 |
| tests.test_security.test_sec04_source_has_no_string_built_sql_or_unsafe_output | PASS | 0.001 |
| tests.test_security.test_sec05_password_minimum_length_boundary | PASS | 0.267 |
| tests.test_security.test_sec05_failure_counter_resets_after_success | PASS | 1.685 |
| tests.test_security.test_sec05_unknown_email_and_wrong_password_look_the_same | PASS | 0.746 |
| tests.test_security.test_sec05_login_locked_after_five_failures | PASS | 1.685 |
| tests.test_security.test_sec05_lockout_survives_restart_and_expires | PASS | 1.953 |
| tests.test_transactions.test_expense_income_edits_deletion_recalculate_dashboard | PASS | 0.576 |
| tests.test_transactions.test_invalid_amount_never_saves[0] | PASS | 0.516 |
| tests.test_transactions.test_invalid_amount_never_saves[-1] | PASS | 0.518 |
| tests.test_transactions.test_invalid_amount_never_saves[] | PASS | 0.515 |
| tests.test_transactions.test_invalid_amount_never_saves[abc] | PASS | 0.518 |
| tests.test_transactions.test_invalid_amount_never_saves[NaN] | PASS | 0.610 |
| tests.test_transactions.test_invalid_amount_never_saves[Infinity] | PASS | 0.519 |
| tests.test_transactions.test_invalid_amount_never_saves[0.001] | PASS | 0.519 |
| tests.test_transactions.test_invalid_amount_never_saves[10000000000] | PASS | 0.520 |
| tests.test_transactions.test_dates_required_fields_custom_category_and_html_retry | PASS | 0.578 |
| tests.test_transactions.test_invalid_filters_rejected[filters0] | PASS | 0.514 |
| tests.test_transactions.test_invalid_filters_rejected[filters1] | PASS | 0.514 |
| tests.test_transactions.test_invalid_filters_rejected[filters2] | PASS | 0.514 |
| tests.test_transactions.test_invalid_filters_rejected[filters3] | PASS | 0.516 |
| tests.test_transactions.test_invalid_filters_rejected[filters4] | PASS | 0.515 |
| tests.test_transactions.test_invalid_filters_rejected[filters5] | PASS | 0.517 |
| tests.test_transactions.test_invalid_filters_rejected[filters6] | PASS | 0.517 |
| tests.test_transactions.test_filters_sort_pagination_and_total | PASS | 0.811 |
| tests.test_transactions.test_html_delete_requires_confirmation_and_cancel_keeps_record | PASS | 0.564 |
| tests.test_unit.test_money_accepts_exact_positive_decimal[0.01-0.01] | PASS | 0.001 |
| tests.test_unit.test_money_accepts_exact_positive_decimal[1-1.00] | PASS | 0.000 |
| tests.test_unit.test_money_accepts_exact_positive_decimal[250.50-250.50] | PASS | 0.000 |
| tests.test_unit.test_money_accepts_exact_positive_decimal[9999999999.99-9999999999.99] | PASS | 0.000 |
| tests.test_unit.test_money_accepts_exact_positive_decimal[10-10.00] | PASS | 0.000 |
| tests.test_unit.test_money_rejects_invalid_amounts[0] | PASS | 0.000 |
| tests.test_unit.test_money_rejects_invalid_amounts[-1] | PASS | 0.000 |
| tests.test_unit.test_money_rejects_invalid_amounts[] | PASS | 0.000 |
| tests.test_unit.test_money_rejects_invalid_amounts[None] | PASS | 0.000 |
| tests.test_unit.test_money_rejects_invalid_amounts[True] | PASS | 0.000 |
| tests.test_unit.test_money_rejects_invalid_amounts[abc] | PASS | 0.000 |
| tests.test_unit.test_money_rejects_invalid_amounts[NaN] | PASS | 0.000 |
| tests.test_unit.test_money_rejects_invalid_amounts[sNaN] | PASS | 0.000 |
| tests.test_unit.test_money_rejects_invalid_amounts[Infinity] | PASS | 0.000 |
| tests.test_unit.test_money_rejects_invalid_amounts[-Infinity] | PASS | 0.000 |
| tests.test_unit.test_money_rejects_invalid_amounts[0.001] | PASS | 0.000 |
| tests.test_unit.test_money_rejects_invalid_amounts[10000000000] | PASS | 0.000 |
| tests.test_unit.test_money_rejects_invalid_amounts[1e1000000] | PASS | 0.000 |
| tests.test_unit.test_month_bounds_include_leap_year[2024-02-29] | PASS | 0.000 |
| tests.test_unit.test_month_bounds_include_leap_year[2026-02-28] | PASS | 0.000 |
| tests.test_unit.test_month_bounds_include_leap_year[2026-04-30] | PASS | 0.001 |
| tests.test_unit.test_month_bounds_include_leap_year[2026-12-31] | PASS | 0.000 |
| tests.test_unit.test_month_bounds_include_leap_year[0001-06-30] | PASS | 0.000 |
| tests.test_unit.test_month_bounds_include_leap_year[9999-12-31] | PASS | 0.000 |
| tests.test_unit.test_month_rejects_invalid_or_unrepresentable_trend[2026-00] | PASS | 0.000 |
| tests.test_unit.test_month_rejects_invalid_or_unrepresentable_trend[2026-13] | PASS | 0.000 |
| tests.test_unit.test_month_rejects_invalid_or_unrepresentable_trend[2026-1] | PASS | 0.000 |
| tests.test_unit.test_month_rejects_invalid_or_unrepresentable_trend[0000-01] | PASS | 0.000 |
| tests.test_unit.test_month_rejects_invalid_or_unrepresentable_trend[0001-01] | PASS | 0.000 |
| tests.test_unit.test_month_rejects_invalid_or_unrepresentable_trend[0001-05] | PASS | 0.000 |
| tests.test_unit.test_month_rejects_invalid_or_unrepresentable_trend[bad] | PASS | 0.000 |
| tests.test_unit.test_month_rejects_invalid_or_unrepresentable_trend[None] | PASS | 0.000 |
| tests.test_unit.test_month_rejects_invalid_or_unrepresentable_trend[202611] | PASS | 0.000 |
| tests.test_unit.test_format_money_preserves_sign_and_two_decimal_places[None-0.00] | PASS | 0.000 |
| tests.test_unit.test_format_money_preserves_sign_and_two_decimal_places[0-0.00] | PASS | 0.000 |
| tests.test_unit.test_format_money_preserves_sign_and_two_decimal_places[raw2-250.50] | PASS | 0.000 |
| tests.test_unit.test_format_money_preserves_sign_and_two_decimal_places[raw3--10.00] | PASS | 0.001 |
