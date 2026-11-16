# Maintenance and deployment plan

Sathik owns account, budget and dashboard fixes. Sahana owns transaction flows and categories used in those flows. Arya owns filtered export, test evidence and security verification. All changes use GitHub issues, focused branches and PRs; owners review each other's work. Assignment does not rewrite authorship.

## Recovery and updates

Stop writes before backing up SQLite, or use SQLite's online backup API. Copying an active database file alone can miss journal data. Store backups outside Git with restricted permissions. Restore into a separate instance, run integrity_check, init-db and smoke tests, then switch over. Never upload user databases, environment files or session keys to the repository.

Before a dependency update, create a branch, update exact pins, run scripts/quality.py and browser checks, and inspect release notes. Roll back the code and restore a compatible backup if a schema change is irreversible. init-db only creates missing tables; use a reviewed migration script for column changes. Keep the previous release tag available.

Review failed requests without logging tokens, passwords or financial notes. Investigate 5xx errors, increased SQLite lock waits, failed backups and authentication anomalies. Expired sessions can be deleted periodically with a reviewed maintenance command. Tests use temporary databases; never point tests at a personal database.

## Container and HTTPS

CI builds Dockerfile and uploads a deployable image archive. To run on a chosen host, provide a strong SECRET_KEY, persist /app/instance, and bind the container only behind an HTTPS reverse proxy. Set COOKIE_SECURE=1. Use a valid domain certificate and redirect HTTP to HTTPS; permit TLS 1.2 or later. Configure the proxy to forward requests securely and keep port 8000 private. No arbitrary forwarded headers are trusted by the app.

Example local container command after building `smartexpense:local`:

```sh
docker run --rm -p 127.0.0.1:8000:8000 --env-file .env -v smartexpense-data:/app/instance smartexpense:local
```

Do not enable Secure cookies on an ordinary HTTP demo: the browser will not send them. Public acceptance requires running the deployed tests with SEB_DEPLOYED_URL and recording the domain, certificate and date. Packaging a container does not establish a working public deployment.

## Defect triage

Critical: cross-user disclosure or data loss; stop affected use, reproduce on synthetic data, patch and rerun security/regression checks. Major: incorrect totals or a broken core flow; fix before acceptance. Minor: cosmetic issue; record an owner and priority. Close issues only with evidence. Monthly review: dependencies, backup restore, open acceptance items and log hygiene.
