# Shared API and data contract

The simplified SAD and SRS remain the requirement sources. This implementation uses Flask/Jinja, SQLAlchemy, bcrypt and Flask-WTF. Charts use local Canvas JavaScript rather than Chart.js; numerical data is also shown as text/tables. This is a small design change, not a requirement change.

Implemented routes:

| Route | Behaviour |
|---|---|
| GET/POST /register | Unique normalized email, name, password; JSON creates with 201 |
| GET/POST /login | Credentials create an 8-hour server-side session and HttpOnly `sid` cookie |
| POST /logout | Deletes the server-side session; replay of old cookie fails |
| GET /categories; POST /categories | Eight defaults plus owner's categories; add custom category |
| PUT or form POST /categories/{id} | Owner rename; defaults read-only |
| GET /budgets; PUT or form POST /budgets | Monthly or category budget upsert; `category_id=null` means overall |
| GET /dashboard; GET /api/dashboard?month=YYYY-MM | Owner totals, budgets and alerts, category breakdown and six months |
| GET /transactions | Owner-filtered records, 50 per page; date/category/min/max filters, date/amount ascending/descending sort |
| GET /transactions/{id} | Owned record JSON; absent or foreign records return 404 |

Use JSON `Content-Type: application/json` for JSON responses on writes. Every write needs the Flask-WTF CSRF token: obtain it from the login form, submit in `X-CSRFToken` for JSON or `csrf_token` for forms. Authentication state is loaded as `g.user`; protect teammate routes with `@protected`. Always include `Transaction.user_id == g.user.id` or the equivalent owner restriction before lookup or mutation.

Teammate transaction contract: `type` expense/income; `amount` Decimal NUMERIC(12,2); `txn_date` date; `user_id` owner. Expenses require visible `category_id` and payment mode; income requires source; note optional. Shared database constraints reject nonpositive values and invalid types. Form and server validation enforce these constraints, including current IST date; CRUD, delete confirmation, filters and sorting are implemented.

The dashboard queries stored records, so transaction changes automatically affect the next dashboard read. Default categories have `user_id=NULL`; these are visible but immutable. Custom categories, budgets and transactions are owner-scoped. Category renames keep IDs stable.

Money is formatted as decimal strings. Alert `none` below 80%, `warning` at 80% through 100%, `over` strictly above 100%; alerts never block writes. Trend spans the selected month and five preceding months, including zeros. Budget scope is unique by owner/month/category, including the monthly NULL scope.

Additional implemented endpoints: GET /transactions/new, POST /transactions, GET /transactions/{id}/edit, PUT or form POST /transactions/{id}, GET /transactions/{id}/delete, DELETE /transactions/{id} or POST /transactions/{id}/delete with confirm=true/yes, and GET /transactions/export.csv. CSV reuses all filters and owner scope, includes all matching pages and neutralizes spreadsheet formulas. Query parameters: from, to, category_id, min, max, sort=date|amount, order=asc|desc, page.

Five failed logins lock the account for five minutes; a locked login returns 429 with Retry-After. Passwords require at least eight characters, use salted bcrypt and never enter logs. Tests cover owner mutations, SQL injection and escaped stored XSS. HTTPS enforcement, HttpOnly/Secure cookies and HSTS are configured; live TLS certificate/protocol acceptance remains pending deployment. SQLAlchemy failures rollback and return a retry message without logging SQL/private fields.
