# Project status: Boloka

## Review branch - 24 October 2026

The responsible money-planning review starts from merged main at c1a9067.
PR #52 is merged. The follow-up for ticket #10 replaces service-role database
access with the caller JWT and a public project key, and adds real PostgreSQL
ownership checks to CI. PR #53 passed all CI jobs and is merged. Deployment
migration and a real two-account test remain.

Ticket #13 adds bounded UTF-8 CSV parsing, shared income validation, precise
money parsing and line-number errors. Malformed files are rejected before any
write; valid rows preserve source/note text instead of silently truncating it.
Reimports are explicitly documented as adding duplicates. Local validation:
119 backend tests, seven frontend tests, Ruff, ESLint and production build pass.

Implemented:

- Transparent pandas-only baseline, bounded completed-week history, explicit upcoming costs/cash assumptions, exact horizon totals, no precise date/likely warning, unvalidated confidence.
- Paginated reads, optional unsaved cash scenario in a validated POST body, owner-scoped mutation checks.
- Consistent preview totals with frozen fictional recommendations clearly labelled; no preview API requests.
- Accessible income/expense edit/delete, confirmation/cancellation, scoped loaded-record JSON export and honest account-deletion limitations.
- Catalogued main-screen copy, named placeholders, visible English fallbacks and a fluent-speaker review inventory.
- Small transaction/preview/format/account-data modules and readable CSS preserving the original rule/declaration signature.

Validation evidence and findings are in docs/product-review.md.
No forecast accuracy, language approval, user impact or live deployment is claimed.

Remaining team decisions:

- Fluent-speaker review; complete recurring-bill/history/cash concepts.
- Full export scope, deletion identity verification, retention/backups, support ownership and contact route.
- Apply and verify database-layer ownership: the API now forwards caller JWTs;
  configure the public project key and run the hosted two-account release test.

External setup:

- Team Supabase/hosting, schema, secrets, redirects and CORS.
- Two-account security and live account-backed flow tests, physical-device/release-signing checks and SSDL approval.
- Actual Sonke submission, pitch recording and consented user evaluation.
