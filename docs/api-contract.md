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
| GET /transactions | Latest 50 owned records, read-only integration view |
| GET /transactions/{id} | Owned record JSON; absent or foreign records return 404 |

Use JSON `Content-Type: application/json` for JSON responses on writes. Every write needs the Flask-WTF CSRF token: obtain it from the login form, submit in `X-CSRFToken` for JSON or `csrf_token` for forms. Authentication state is loaded as `g.user`; protect teammate routes with `@protected`. Always include `Transaction.user_id == g.user.id` or the equivalent owner restriction before lookup or mutation.

Teammate transaction contract: `type` expense/income; `amount` Decimal NUMERIC(12,2); `txn_date` date; `user_id` owner. Expenses require visible `category_id` and payment mode; income requires source; note optional. Shared database constraints reject nonpositive values and invalid types. The teammate must add form validation (including server IST date), CRUD, confirmation, filters and sorting; do not replace the shared model.

The dashboard queries stored records, so transaction changes automatically affect the next dashboard read. Default categories have `user_id=NULL`; these are visible but immutable. Custom categories, budgets and transactions are owner-scoped. Category renames keep IDs stable.

Money is formatted as decimal strings. Alert `none` below 80%, `warning` at 80% through 100%, `over` strictly above 100%; alerts never block writes. Trend spans the selected month and five preceding months, including zeros. Budget scope is unique by owner/month/category, including the monthly NULL scope.

Pending teammate endpoints: transaction POST/PUT/DELETE, filters and CSV. CSV must reuse list filters and owner scope. The TC-AUTH-04 export check and TC-CAT-01 expense selector check require those endpoints to be integrated.

Security owner must add five-failure/five-minute lockout and verify the deployed TLS, cookie settings, ownership of every teammate mutation, SQL/XSS handling and logs. Basic password hashing and minimum length are included because registration needs them; they are not a substitute for TC-SEC-01–05 execution.
