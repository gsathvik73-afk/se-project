# Shared API and data contract

Flask/Jinja, SQLAlchemy, bcrypt and Flask-WTF; local Canvas charts also provide numerical tables. Authenticated requests use the server-side `sid` cookie (8-hour absolute lifetime). Send `Content-Type: application/json` for JSON writes, and `Accept: application/json` for JSON reads. Every write requires a Flask-WTF CSRF token from the login form, in `X-CSRFToken` or the form's `csrf_token` field.

| Route | Behaviour |
|---|---|
| GET/POST /register | Normalized unique email, name, password; JSON creates with 201 |
| GET/POST /login | Session on success; 401 on bad credentials; five failures block login for five minutes with 429 and Retry-After |
| POST /logout | Revokes server session; old cookie replay fails |
| GET/POST /categories | Eight shared defaults plus owned custom categories; create custom category |
| PUT or form POST /categories/{id} | Rename owned custom category; defaults are immutable |
| GET/PUT/POST /budgets | Read/upsert monthly or category budget; category_id=null means overall |
| GET /dashboard; GET /api/dashboard?month=YYYY-MM | Owner-scoped totals, budgets/alerts, category breakdown and six-month trend |
| GET/POST /transactions | Filtered/sorted/paged owner list or create expense/income |
| GET/PUT/DELETE /transactions/{id} | Read, update or delete an owned transaction |
| GET/POST /transactions/{id}/edit | Browser edit form; PUT is also accepted |
| GET/POST /transactions/{id}/delete | Browser confirmation; cancel keeps record, form delete requires confirm=yes |
| GET /transactions/export.csv | All owned matches with the same filters/sort as the list, independent of page |

Transactions use `type=expense|income`, positive `amount` with at most two decimals, `date=YYYY-MM-DD` no later than server IST today, optional `note`. Expenses require a visible `category_id` and `payment_mode`; income requires `source`. No client-supplied user ID is trusted. Absent or foreign records/categories return 404. Invalid fields/filters return 422; unauthenticated JSON gets 401, browser requests redirect to login. Writes recalculate dashboard totals on the next read and never get blocked by budget warnings.

List/export filters: `start`/`end` (also `from`/`to`), `category_id`, `min_amount`/`max_amount` (also `min`/`max`), `sort=date|amount|type`, `direction=asc|desc`. Combined values such as `sort=amount_desc` are accepted. Dates and amounts include both bounds. List `page` starts at 1 with up to 50 records; JSON includes `page`, `has_next` and the total across all matches. CSV has UTF-8 header `date,type,category,amount,payment_mode,source,note`, correct escaping, and formula-neutralized text cells.

Money in JSON is a decimal string. Budgets are unique by owner/month/category including overall scope. Alerts: none below 80%, warning from 80% through 100%, over strictly above 100%. Trend includes selected month and five preceding months, including zeros.

Unexpected save failures roll back, return 500 with a retry message and request reference, and omit technical details from the response. Failure logs contain the request reference, endpoint and exception type rather than passwords, SQL parameters, tokens or financial notes. Authenticated responses are not cached. Browser script/style resources are local and subject to CSP.

`init-db` creates new tables, including persistent login guards, and seeds defaults without deleting existing data. `COOKIE_SECURE=1` enables Secure cookies for a future HTTPS deployment. HTTP redirect, certificate and deployed TLS remain hosting acceptance checks.

## Exact examples for the current implementation

These examples use a synthetic logged-in user. Obtain a fresh CSRF token from GET /login and send it with the same cookie session in X-CSRFToken for every write. Public numeric IDs shown below are examples, not trusted owner inputs.

```json
POST /login
{"email":"demo@example.test","password":"DemoPass123!"}

200
{"user":{"id":1,"name":"Demo Student"}}
```

Success sets an opaque sid cookie. The app does not return a `message` field here. After five failures, an attempt during lockout receives `429 {"error":"LOGIN_LOCKED"}` and Retry-After.

```json
POST /transactions
{"type":"expense","amount":"250.00","date":"2026-10-08","category_id":1,"payment_mode":"UPI","note":"Lunch"}

201
{"transaction":{"id":1,"type":"expense","amount":"250.00","date":"2026-10-08","category_id":1,"payment_mode":"UPI","source":null,"note":"Lunch"}}
```

Creation returns the saved transaction. GET /api/dashboard?month=2026-10 performs the subsequent aggregation; totals and budget alerts are not included in this creation response.

```json
PUT /budgets
{"month":"2026-10","limit":"5000.00","category_id":null}

200
{"budget":{"id":1,"month":"2026-10","category_id":null,"limit":"5000.00"}}
```

Invalid amounts return `422 {"error":"VALIDATION_ERROR","fields":{"amount":"Enter a positive amount with at most two decimal places."}}`. Unavailable record/category requests asking for JSON return `404 {"error":"NOT_FOUND"}`. JSON CSRF failures return `400 {"error":"BAD_REQUEST"}`. Unexpected save errors return `500 {"error":"SAVE_FAILED","message":"Your data was not saved. Please retry.","request_id":"..."}`.

Filter amounts are bounded by the same maximum stored amount to avoid database conversion overflow. Category identifiers must be positive integer representations within SQLite's range; booleans and fractional IDs are unavailable. Dashboard months before June 0001 are rejected because six preceding buckets cannot be represented.
