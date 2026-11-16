# Unit Test Report

Executed at 2026-11-15T18:25:34.114798+00:00.

37 passed; 0 failed; 0 skipped.

Full case identifiers, durations and captured output are in the adjacent JUnit XML.

| Test | Result | Seconds |
|---|---|---:|
| tests.test_unit.test_money_accepts_exact_positive_decimal[0.01-0.01] | PASS | 0.000 |
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
| tests.test_unit.test_month_bounds_include_leap_year[2026-04-30] | PASS | 0.000 |
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
| tests.test_unit.test_format_money_preserves_sign_and_two_decimal_places[raw3--10.00] | PASS | 0.000 |
