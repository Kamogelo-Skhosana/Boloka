# Boloka secure software development lifecycle (SSDL) — working draft

**Status:** engineering draft for team/security-owner review. This is not a penetration-test report, legal opinion, or certification. Confirm the competition's required SSDL template and replace/transfer this content into it before marking issue #41 complete.

**System:** Boloka, a cash-flow planning app for people with irregular incomes.
**Repository:** `Kamogelo-Skhosana/Boloka`
**Reviewed baseline:** `main` at `1d752c8` plus the unmerged feature branch described by its pull request.
**Data classification:** financial transaction records and account identifiers are sensitive personal information.

## Architecture and trust boundaries

- React/Vite browser app. Supabase Auth issues the user access token. Only the public/anon key may be included in the browser bundle.
- FastAPI API validates Supabase JWTs and derives the owner from the verified subject claim.
- Supabase Postgres stores income and expense events. Row-level security restricts access by owner. The backend uses a service-role key server-side and scopes queries using the authenticated subject.
- Browser-to-API and API-to-Supabase traffic crosses network trust boundaries. Production must use HTTPS.
- CSV imports are untrusted user uploads and are parsed server-side with a 2 MB size limit.

## Data collected and purpose

| Data | Purpose | Handling |
| --- | --- | --- |
| Email address and Supabase user ID | Account creation, sign-in, ownership | Auth provider and token; do not log credentials or tokens |
| Income amount, source, date, note | Cash-flow estimate | User-scoped `income_events` rows |
| Expense amount, category, date, recurring flag, note | Cash-flow estimate | User-scoped `expenses` rows |
| Savings contribution amount, date, note | Actual set-aside progress | User-scoped `savings_contributions` rows |
| CSV upload | Optional bulk income entry | Parsed in memory by API; only valid rows are inserted |
| Language and low-data preference | Local interface preferences | Browser local storage; no financial records |

The sample dashboard uses fictional data. Preview changes remain in memory and are not uploaded. No live Boloka Supabase deployment is configured in this repository at the time of this draft.

## Security controls present in code

- JWT signature, issuer/audience and expiry checks are implemented in the API auth dependency; invalid identities are rejected.
- API ownership comes from verified JWT claims, not a client-supplied user ID.
- Schema enables row-level security and owner policies. Review and exercise those policies in the provisioned team project before launch.
- Service-role credentials are server-only. Frontend examples use only the publishable/anon key. `.env` files and build output are ignored by Git.
- Pydantic request models enforce positive bounded amounts, dates and field lengths. Database requests use parameterized HTTP query parameters rather than SQL string concatenation.
- CSV file extension, UTF-8, required columns, row values and total size are checked. Invalid rows are skipped and counted.
- API errors avoid returning database response bodies or internal credentials.
- Frontend does not cache `/api/` responses in its service worker. Signed-in financial data is not stored in low-data/offline caches.
- CI runs lint, build and backend checks. Dependencies are lockfile-managed for the frontend.

## Main threats and mitigations

| Threat | Mitigation | Residual work |
| --- | --- | --- |
| Cross-user transaction access | JWT-derived owner checks plus Postgres RLS | Verify with two real test accounts after project setup |
| Credential leakage | Server-side secret configuration; public client key only | Configure secrets in team-owned hosting and inspect deployed bundle/logs |
| Malformed or oversized CSV | 2 MB limit, strict columns, bounded fields and per-row validation | Confirm operational rate limits and abuse monitoring |
| Browser XSS / script supply-chain risk | React text rendering, locked dependencies, HTTPS deployment | Add dependency update/security scanning and review future HTML insertion |
| Network interception | Require HTTPS in production | Confirm Vercel/Render custom domains, redirects and TLS settings |
| Stale private data on a shared device | Service worker caches app shell/assets only, not account API data | Decide account-session timeout and logout expectations with product owner |
| Forecast harm through overconfidence | Confidence labels, explanations and non-advice disclaimer | Validate against real opt-in user data; keep accuracy claims out until measured |
| Availability or repeated requests | Request timeouts, loading/error states and manual retry | Configure hosting limits, backups, monitoring and incident owner |

## Required release checks

- [ ] Security owner approves this draft and the final required SSDL submission form.
- [ ] Apply `supabase/schema.sql` to a team-owned project; test that two users cannot read, modify, or delete each other's rows through the API or direct client requests.
- [ ] Store Supabase service key, JWT secret and deployment tokens only in hosting/GitHub secret stores; rotate any credentials that were exposed.
- [ ] Confirm HTTPS, Supabase Auth redirect allowlist, CORS origin allowlist and production API base URL.
- [ ] Test sign-up, email confirmation, sign-in, token expiry/refresh and sign-out with a non-production account.
- [ ] Inspect browser bundle, network requests and logs for secret or personal-data exposure.
- [ ] Review dependency advisories and configure database backups, access ownership and incident response.
- [ ] Perform consented user testing and security testing before using real financial records.

## Owners and review

| Responsibility | Owner | Status |
| --- | --- | --- |
| Product/data purpose and retention | Product lead to assign | Not recorded |
| Supabase project access and RLS verification | Backend/security owner to assign | Blocked on team project |
| Hosting secrets and production configuration | Deployment owner to assign | Not configured |
| Final SSDL submission approval | Team lead/security reviewer | Pending |

Do not put passwords, JWTs, service-role keys, real transaction data, judge-account credentials or private Sonke submission details in this repository.
