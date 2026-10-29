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
