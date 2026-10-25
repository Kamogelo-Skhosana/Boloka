# Boloka secure software development lifecycle (SSDL)

**Document status:** Engineering assessment prepared for team/security-owner review. It records repository controls and known release gaps; it is not a penetration-test report, legal opinion, or certification. Transfer the verified content into any required Sonke/competition template and obtain the named owners' approval before treating the SSDL submission as complete.

| Field | Value |
| --- | --- |
| System | Boloka, a cash-flow planning app for people with irregular incomes |
| Repository | `Kamogelo-Skhosana/Boloka` |
| Reviewed baseline | `main` at `10e59ea1754f5a49ab4100def100a56ed9c50be0` (25 October 2026) |
| Data classification | Sensitive personal and financial information: account identifiers and user-entered income, expense and savings records |
| Assessment scope | Tracked application source, database schema and repository CI at the baseline above |
| Exclusions | Hosted configuration, operational logs, production accounts, penetration testing, legal/compliance determinations and private competition submission systems |

Re-review this document against the final release commit and deployed configuration. A source review cannot prove production settings are safe.

## Architecture and trust boundaries

- React/Vite browser app. Supabase Auth issues the user access token. The Supabase JavaScript client persists its session in browser storage by default. Only the public/publishable key may be included in the browser bundle; never include a service-role or other secret key.
- FastAPI API validates Supabase JWTs and derives the owner from the verified subject claim.
- Supabase Postgres schema contains profiles, income, expense, savings-contribution and forecast tables. Row-level security restricts access by owner. The backend forwards the verified caller JWT with a public project key and keeps explicit API owner filters as an additional check.
- Browser-to-API and API-to-Supabase traffic crosses network trust boundaries. Production must use HTTPS.
- CSV imports are untrusted user uploads and are parsed server-side with a 2 MB byte limit and a 10,000-row limit.
- The app has no bank credential connection or bank-statement ingestion in this release. Sample/preview records are fictional and in-memory; preview edits are not uploaded.

## Data collected and purpose

| Data | Purpose | Handling |
| --- | --- | --- |
| Email address and Supabase user ID | Account creation, sign-in, ownership | Auth provider and token; do not log credentials or tokens |
| Income amount, source, date and note | Cash-flow estimate | User-scoped `income_events` rows |
| Expense amount, category, date, recurring flag and note | Cash-flow estimate | User-scoped `expenses` rows |
| Savings contribution amount, date and note | Actual set-aside progress | User-scoped `savings_contributions` rows |
| CSV upload | Optional bulk income entry | Parsed in memory by API; only valid rows are inserted |
| Language, low-data, contrast, text-size and onboarding preferences | Local interface preferences | Browser local storage; no financial records |
| Supabase access/refresh session | Sign-in and authenticated requests | Managed by the Supabase browser client in browser storage; logout/session lifetime and shared-device expectations need product/security-owner confirmation |

The sample dashboard uses fictional data. Preview changes remain in memory and are not uploaded. No bank login details or statements are collected. The public repository contains no live project credentials or judge URL, and source configuration alone does not prove a hosted deployment is secure. Verify the selected team project, schema, redirects, CORS and signed-in flows before release. Retention periods, deletion workflow, support contact and incident-response ownership are not yet recorded and must be decided by the team before real-user rollout.

## Security controls present in code

- JWT issuer, audience, required expiry, UUID subject and authenticated role checks are implemented in the API auth dependency; invalid identities and privileged tokens are rejected. ES256/RS256 use the configured project's HTTPS JWKS endpoint and key ID. Legacy HS256 is accepted only when its signing secret is explicitly configured server-side. The JWKS URL is constrained to the project endpoint; token-provided key URLs are ignored.
- API ownership comes from verified JWT claims, not a client-supplied user ID.
- Schema enables row-level security and owner policies. CI exercises the policies using separate PostgreSQL roles and subjects; this does not verify the team's hosted project.
- `backend/app/release_check.py` provides an interactive, non-destructive check for two populated accounts against the API and direct PostgREST reads. It uses hidden password prompts, requires a public project key, validates owner separation, and attempts to sign out only the QA sessions it created. The check has automated mock tests, but no hosted run is recorded yet.
- User-data routes use the publishable/anon project key plus the verified caller JWT; they do not need a service-role key. Frontend examples use only the publishable/anon key. `.env` files and build output are ignored by Git.
- Pydantic request models enforce positive bounded amounts, dates and field lengths. Database requests use parameterized HTTP query parameters rather than SQL string concatenation. Database error bodies are not returned to callers.
- CSV file extension, UTF-8, required columns, row values, 2 MB size and 10,000-row count are checked. Invalid rows are skipped and counted.
- API errors avoid returning database response bodies or internal credentials.
- Frontend does not cache `/api/` responses in its service worker. Signed-in financial data is not stored in low-data/offline caches.
- CI runs frontend lint/tests/build and browser preview checks, backend lint/tests, and disposable PostgreSQL ownership-policy checks. Production deployment is gated on the tested main-branch workflow. Frontend dependencies are lockfile-managed; dependency vulnerability monitoring and a formal security review are not yet configured or evidenced here.

## Main threats and mitigations

| Threat | Mitigation | Residual work |
| --- | --- | --- |
| Cross-user transaction access | Caller JWT forwarded to database RLS, explicit API owner filters, PostgreSQL ownership tests in CI, and a non-destructive two-account release-check command | Apply configuration/schema and run the read check against two populated hosted accounts; separately verify write/delete isolation |
| Credential leakage | Server-side secret configuration; public client key only; release secrets and signing keys are not committed | Configure secrets in team-owned hosting and inspect deployed bundle/logs |
| Malformed or oversized CSV | 2 MB limit, strict columns, bounded fields and per-row validation | Confirm operational rate limits and abuse monitoring |
| Browser XSS / script supply-chain risk | React text rendering, lockfile-managed dependencies, HTTPS deployment | Add dependency update/security scanning and review future HTML insertion |
| Network interception | Require HTTPS in production | Confirm hosting domains, redirects and TLS settings |
| Stale private data on a shared device | Service worker caches app shell/assets only, not account API data | Supabase session persists in browser storage; decide timeout, logout and shared-device expectations with product owner |
| Forecast harm through overconfidence | Confidence labels, explanations and non-advice disclaimer | Validate against opt-in user data; keep accuracy claims out until measured |
| Availability or repeated requests | Database request timeout, loading/error states and manual retry | Configure hosting limits, backups, monitoring, rate limits and incident owner |

## Required release checks

- [x] Repository controls and trust boundaries reviewed against the baseline above; CI contains two-user PostgreSQL RLS checks. This does not verify the hosted team project.
- [x] A non-destructive two-account hosted read-check command is available at `backend/app/release_check.py`; its mock-based tests do not count as a live run.
- [ ] Security owner reviews this assessment and approves/transfers it into the final required SSDL submission form.
- [ ] Apply `supabase/schema.sql` to a team-owned project and run the command in `docs/judge-demo.md` with two populated test accounts against the HTTPS API. Record only release commit, date, environment, aliases A/B, and pass/fail; do not save credentials or tokens.
- [ ] Verify write/delete isolation separately through the hosted API and direct client requests; the release-check command is read-only and does not cover those operations.
- [ ] Never put a service-role/secret key in the browser; user-data routes do not require one. If the team deliberately uses legacy HS256, store its signing secret only in backend hosting secrets. Keep deployment tokens in protected secret stores and rotate any exposed credentials.
- [ ] Confirm HTTPS, Supabase Auth redirect allowlist, CORS origin allowlist and production API base URL.
- [ ] Test sign-up, email confirmation, sign-in, token expiry/refresh and sign-out with a non-production account.
- [ ] Inspect browser bundle, network requests and logs for secret or personal-data exposure.
- [ ] Review current dependency advisories and configure update monitoring, database backups, access ownership and incident response.
- [ ] Perform consented user testing and security testing before using real financial records.
- [ ] Decide and document retention/deletion, support contact, session expiry and shared-device handling before real-user rollout.

## Owners and review

| Responsibility | Owner | Status |
| --- | --- | --- |
| Product/data purpose, retention and deletion | Product lead — name to confirm | Purpose documented; retention/deletion decision pending |
| Supabase project access and hosted RLS verification | Backend/security owner — name to confirm | Blocked on team project access and two-account check |
| Hosting secrets and production configuration | Deployment owner — name to confirm | Team-owned hosting configuration not verified |
| Security review and final SSDL submission | Team lead/security reviewer — name to confirm | Pending review and required template confirmation |

Do not put passwords, JWTs, service-role keys, real transaction data, judge-account credentials or private Sonke submission details in this repository.

## Review notes and evidence boundaries

The service-role bypass found in the product review is addressed by ticket #10: the API forwards the verified caller JWT with a public project key, and CI exercises the schema's policies using two PostgreSQL roles/subjects. PR #70 adds a separately tested interactive read-only check for two seeded hosted accounts. The CI database and mock tests do not prove that a team-hosted project has the same schema or settings; the hosted check must still be run, and does not cover write/delete isolation. Forecast confidence remains unvalidated, no likely warning/date is produced, preview forecasts are frozen fictional references, and loaded-entry export does not implement full account deletion/export. No production security assessment or penetration test is claimed.
