# Boloka

**Save, before you have to.** Boloka helps people with irregular incomes prepare for known costs. It records gig income and expenses, estimates near-term cash flow, flags a possible shortfall, and explains a weekly set-aside suggestion.

Boloka is a prototype for the FNB App of the Year 2026 Financial Inclusion hackathon. Forecasts are estimates, not financial advice or guaranteed income.

## What is in this repository

- `frontend/` — responsive React app with dashboard, forecast, entry/import, savings and account screens.
- `backend/` — FastAPI v1 API, user-scoped CRUD, CSV import, and explainable cash-flow estimates.
- `supabase/schema.sql` — PostgreSQL tables, ownership policies, and new-user profile trigger.
- `supabase/seed.sql` — repeatable, synthetic demo income and expense history.
- `docs/` — API, design, product benchmark, demo guide, pitch and Lean Canvas.
- `submission/` — judge-facing pitch deck and 20-second video script.
- `render.yaml` — Render API Blueprint, configured to deploy after checks pass.

## Run locally

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
uvicorn app.main:app --reload
```

Set `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` in `backend/.env`. ES256/RS256 projects use the project's public JWKS endpoint automatically; optional `SUPABASE_JWKS_URL` must match that project's endpoint. Only legacy HS256 projects need `SUPABASE_JWT_SECRET`, which is a signing secret rather than an `sb_secret_` API key. Use a public publishable/anon project key; privileged project keys are rejected by user-data routes. The public health route works without database credentials. See [backend configuration](backend/README.md) for verification requirements.

### Frontend

```powershell
cd frontend
npm ci
if (!(Test-Path .env)) { Copy-Item .env.example .env }
npm run lint
npm run dev
```

Set the Supabase URL and publishable/anon key plus the API base URL in `frontend/.env`. Authentication uses the public key; never put a service-role or secret key in the browser.

### Database and demo data

1. Create a Supabase project in the team's chosen organization and region.
2. Run `supabase/schema.sql` in its SQL editor.
3. Create a dedicated demo user in Supabase Auth.
4. Follow [synthetic dataset setup](supabase/README.md) to select that dedicated user's email, explicitly confirm seeding, and run `supabase/seed.sql`. Only marked synthetic rows are replaced; other entries remain.
5. Configure redirect URLs in Supabase Auth for the local frontend and deployed site.

The repository does not contain Supabase credentials or a demo password. Add credentials through the team's private configuration and share demo login details through the hackathon submission, never in this public repository.

## Judge access and release status

| Item | Verified status |
| --- | --- |
| Hosted frontend URL | `https://boloka.vercel.app`; returned HTTP 200 on 25 October 2026. This confirms the page is reachable, not the complete signed-in flow. |
| Hosted API URL | `https://boloka.onrender.com/api/v1`; owner-reported two-account read check passed on 25 October 2026. A separate health request from this review timed out, so current API availability needs a fresh check. |
| Judge login | Owner reports production sign-in and persistence work. Dedicated judge credentials still belong in the private Sonke submission. |
| Synthetic preview | Available without sign-in; fictional reference forecast and temporary entries are labelled |
| Account-backed demo | Requires configured Supabase, schema, Auth redirects, API URL and CORS, followed by the [judge runbook](docs/judge-demo.md) |

The frontend URL and owner-reported production sign-in are recorded above; the
private judge-access handoff remains outstanding. Do not use a preview
screenshot or a skipped deployment workflow as evidence of a live
account-backed release. Tickets #9, #35 and #42 track the remaining account,
release and private-access acceptance.

## Architecture

| Component | Responsibility and boundary |
| --- | --- |
| React/Vite frontend | Entry/correction, CSV import, preview, forecast display, local language preference; only a public Supabase key is bundled |
| Supabase Auth | Issues user access tokens; the API verifies project issuer, audience, expiry and authenticated UUID identity |
| FastAPI API | Validates input, derives ownership from the verified token and forwards that token with the public project key |
| PostgreSQL / Supabase RLS | Enforces user ownership independently of API filters; no privileged key is used for user-data routes |
| pandas planning baseline | Uses completed earning weeks and explicit cost/cash assumptions; no ML dependency or validated accuracy claim |
| Hosting / CI | Vercel frontend and Render API configuration; deployment waits for successful CI on the tested main commit |

Preview entries stay in the browser session and are never sent to the API.
Optional available cash is an unsaved scenario, not a bank-verified balance.
See [product decisions and limits](docs/product-review.md),
[API contract](docs/api.md), and [deployment setup](docs/deployment.md).
The follow-on research sequence is documented in
[`docs/user-research/`](docs/user-research/): discover the first user segment,
observe the core workflow, agree privacy controls before a real-data pilot,
and evaluate optional AI only if users identify a need.

## API contract

The contract is in [`docs/api.md`](docs/api.md). Routes are rooted at `/api/v1`; all routes except `/health` require a Supabase access token. Income and expense amounts are positive integer cents in ZAR. The API derives ownership from a verified token and scopes every database operation to that user.

The pandas baseline averages up to eight completed earning weeks, preserves zero-record weeks and distinguishes explicitly dated upcoming costs from historical everyday spending. Available cash is an optional unsaved scenario, not the recorded ledger net. It does not predict a precise shortfall date or calibrated probability. Confidence is unvalidated. See the API contract for observation thresholds and assumptions.

## Verify locally

```powershell
cd backend
pip install -r requirements.txt
pip install pytest ruff
ruff check .
python -m pytest -q
cd ..\frontend
npm ci
npm run lint
npm run build
```

See [`docs/judge-demo.md`](docs/judge-demo.md) for the manual judge flow and [`docs/award-benchmark.md`](docs/award-benchmark.md) for product standards drawn from the FNB App of the Year materials.
For the Android debug build and team-key-signed release build, see [`docs/android-release.md`](docs/android-release.md).

See [`docs/deployment.md`](docs/deployment.md) for one-time Vercel, Render, and Supabase setup. A public live URL and judge account are not committed because the project has not been provisioned with team credentials.

## Current release status

The frontend can be explored without an account using clearly labelled fictional sample data. Preview edits recalculate recorded totals, but the fictional reference recommendation stays unchanged and explicitly labelled. Nothing from preview is uploaded. Live account data requires team Supabase configuration. Live hosting, a real demo account, and final Sonke submission depend on team-owned credentials and account access. No live deployment or user pilot is claimed in this README.

See [the product review](docs/product-review.md) for acceptance criteria, engineering findings and remaining privacy/release decisions, and [the localization inventory](docs/localization-review.md) for the fluent-speaker review backlog. Run `npm test` as well as frontend lint/build. Fresh clones must run `git submodule update --init --recursive` before building Themeloom.

## Team

ThaKa — Kamogelo Skhosana and Thato Maluleka.

## License

MIT. See [`LICENSE`](LICENSE).
