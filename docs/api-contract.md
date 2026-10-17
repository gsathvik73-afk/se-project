# Shared API and data contract

The app serves Flask/Jinja pages and JSON responses from the same routes. This contract follows [the route handlers](../smartexpense/routes.py) and [application configuration](../smartexpense/__init__.py).

## Session and request format

Authenticated requests use the `sid` cookie, backed by a server-side session with an eight-hour absolute lifetime. Send `Content-Type: application/json` for JSON writes and `Accept: application/json` for JSON reads. JSON write bodies must be objects.

Every write requires a Flask-WTF CSRF token. Fetch `/login` first, retain the cookies, and send the hidden form token as `X-CSRFToken` or `csrf_token` in a form submission. The Flask session cookie that accompanies the token is also needed; the `sid` cookie alone is insufficient for CSRF validation. Do not disable CSRF for API clients.

| Route | Behaviour |
|---|---|
| GET/POST /register | Normalize email; create a user with JSON status 201 |
| GET/POST /login | Start a session; 401 for bad credentials; 429 with `Retry-After` while locked |
| POST /logout | Revoke the server session and clear `sid` |
| GET/POST /categories | List shared defaults and owned categories, or create an owned category |
| PUT or form POST /categories/{id} | Rename an owned custom category; shared defaults return 403 |
| GET/PUT/POST /budgets | Read or upsert a monthly/category budget; null category means overall |
| GET /dashboard | Render the dashboard page |
| GET /api/dashboard?month=YYYY-MM | Return dashboard totals, budgets, category breakdown, and six-month trend |
| GET/POST /transactions | List filtered, sorted, paged owned records, or create a transaction |
| GET/PUT/DELETE /transactions/{id} | Read JSON, update, or delete an owned record |
| GET/POST/PUT /transactions/{id}/edit | Render the browser edit form, or save edits |
| GET/POST/DELETE /transactions/{id}/delete | Render confirmation, or delete the record |
| GET /transactions/export.csv | Download all owned matches with list filters and ordering |

## Transaction fields

| Field | Rules |
|---|---|
| `type` | `expense` or `income`; creation defaults to `expense` |
| `amount` | Positive, at most two decimal places, maximum `9999999999.99` |
| `date` | ISO date, `YYYY-MM-DD`; cannot be later than server date in Asia/Kolkata |
| `category_id` | Required for expenses; must be a shared or owned category |
| `payment_mode` | Required for expenses; trimmed text, 1–30 characters |
| `source` | Required for income; trimmed text, 1–100 characters |
| `note` | Optional, trimmed, at most 2,000 characters; empty text is stored as null |

Money is returned as a decimal string. No client-supplied user ID is used. Income clears category and payment mode; expenses clear source. For updates, omitted fields retain their current values where applicable. Changing the type requires the fields for the new type.

Example expense request after authentication and CSRF setup:

```http
POST /transactions
Content-Type: application/json
Accept: application/json
X-CSRFToken: <token from the login form>
Cookie: <session cookies>

{"type":"expense","amount":"250.00","date":"2026-10-10","category_id":1,"payment_mode":"UPI","note":"Lunch"}
```

Use a category ID returned by `GET /categories`; `1` is illustrative. Successful creation returns 201:

```json
{"transaction":{"id":42,"type":"expense","amount":"250.00","date":"2026-10-10","category_id":1,"payment_mode":"UPI","source":null,"note":"Lunch"}}
```

An income request uses `{"type":"income","amount":"2000.00","date":"2026-10-10","source":"Freelance"}`. `GET /transactions/42` and a successful JSON update return the same `transaction` wrapper. A JSON delete returns `{"ok":true}`. Browser form deletion requires `confirm=yes`; a GET or unconfirmed form POST only shows the confirmation page.

## Filters, ordering, and pagination

List and CSV routes share these query parameters. Date and amount bounds are inclusive.

| Parameter | Meaning |
|---|---|
| `start`, `end` | Date bounds; aliases `from`, `to` |
| `category_id` | Visible category ID |
| `min_amount`, `max_amount` | Finite nonnegative amounts; aliases `min`, `max` |
| `sort` | `date` (default), `amount`, or `type` |
| `direction` | `desc` (default) or `asc` |
| `page` | Integer from 1 to 1,000,000; default 1, fixed page size of 50 |

Combined sorts such as `amount_desc` and `date_asc` override `direction`. Unsupported sort fields fall back to `date`; directions other than `asc` use descending order. Ties use record ID descending. Invalid filters return 422. Canonical parameter names take precedence over their aliases when both appear.

```http
GET /transactions?start=2026-10-01&end=2026-10-31&min_amount=100&sort=amount_desc&page=1
Accept: application/json
```

An illustrative response with one matching record:

```json
{"page":1,"has_next":false,"transactions":[{"id":42,"type":"expense","amount":"250.00","date":"2026-10-10","category_id":1,"payment_mode":"UPI","source":null,"note":"Lunch"}],"total":"250.00"}
```

`total` is the sum of positive amounts across **all** matching records, including both income and expense; it is not a record count, page subtotal, or net balance. An empty page has `transactions: []` and `has_next: false`, but `total` still describes all matches. No total record count or page count is returned.

## CSV export

Use `/transactions/export.csv` with the same filters and sort. Export ignores page offsets and includes every matching record, but still validates the `page` parameter if provided. The response uses `text/csv; charset=utf-8` and `Content-Disposition: attachment; filename="smartexpense.csv"`.

```csv
date,type,category,amount,payment_mode,source,note
2026-10-10,expense,Food,250.00,UPI,,Lunch
```

The first row is always present, including empty exports. CSV quoting handles commas, quotes, and line breaks. Text cells beginning with spreadsheet formula markers (`=`, `+`, `-`, `@`, including after leading whitespace), or a leading tab/newline/carriage return, receive a leading apostrophe. Export stays scoped to the authenticated user.

## Categories, budgets, and dashboard

`GET /categories` returns `{"categories":[{"id":1,"name":"Food","is_default":true}]}` with the eight shared defaults plus the user's custom categories, sorted by name. POST accepts `{"name":"Books"}` and returns a `category` object with status 201. Names must be unique among visible categories, ignoring case, and 1–80 characters long.

A budget write such as `{"month":"2026-10","limit":"5000.00","category_id":null}` upserts the overall monthly budget. A visible category ID creates or updates that category's budget. The response is `{"budget":{"id":3,"month":"2026-10","category_id":null,"limit":"5000.00"}}`. Budget scope is unique by owner, month, and category. `GET /budgets?month=2026-10` returns the month and budget entries with spending, remaining, percentage, and alert values.

Dashboard JSON contains `month`, `income`, `expense`, `balance`, `budgets`, `categories`, and `trend`. Category entries contain `name` and `total`; trend entries contain `month` and `expense`. The trend covers the selected month and five preceding months, including zero-spend months. Budget alerts are `none` below 80%, `warning` from 80% through 100%, and `over` strictly above 100%. Warnings never block transaction saves.

## Errors and deployment

Unauthenticated JSON requests return 401 with `{"error":"NOT_AUTHENTICATED"}`; browser requests redirect to login. Validation returns 422, for example:

```json
{"error":"VALIDATION_ERROR","fields":{"amount":"Enter a positive amount with at most two decimal places."}}
```

Bad login credentials return `INVALID_CREDENTIALS` with 401. After five failures for an existing account, the following attempts return `LOGIN_LOCKED` with 429 for five minutes and a `Retry-After` header. The fifth failed attempt itself returns 401. A successful login resets the failure counter.

Missing or foreign transaction/category records return 404. An invalid list category filter returns a 422 field error instead. CSRF errors and abort-generated errors such as 403/404 use framework responses; clients should check status codes rather than assume every error has the validation JSON shape.

Unexpected save failures roll back and return 500. JSON responses contain `error: "SAVE_FAILED"`, a retry message, and `request_id`. Logs contain the request reference, endpoint, and exception type rather than passwords, SQL parameters, tokens, or financial notes. Non-static responses use `Cache-Control: no-store`.

`init-db` creates missing tables and seeds default categories without deleting data. `COOKIE_SECURE=1` enables Secure cookies for an HTTPS host. Public HTTP redirection, valid certificates, and deployed TLS remain hosting acceptance checks.
