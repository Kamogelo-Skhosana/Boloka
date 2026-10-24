# Boloka

**Save, before you have to.** Boloka helps people with irregular incomes prepare for known costs. It records gig income and expenses, estimates near-term cash flow, flags a possible shortfall, and explains a weekly set-aside suggestion.

Boloka is a prototype for the FNB App of the Year 2026 Financial Inclusion hackathon. Forecasts are estimates, not financial advice or guaranteed income.

## What is in this repository

- `frontend/` — React and Vite app shell, Supabase Auth client, dark-first theme.
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
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Set `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and `SUPABASE_JWT_SECRET` in `backend/.env`. The service-role key must remain server-side. The public health route works without database credentials; authenticated data endpoints return `503` until configured.

### Frontend

```powershell
cd frontend
npm ci
Copy-Item .env.example .env
npm run dev
```

Set the Supabase URL and publishable/anon key plus the API base URL in `frontend/.env`. Authentication uses the public key; never put a service-role or secret key in the browser.

### Database and demo data

1. Create a Supabase project in the team's chosen organization and region.
2. Run `supabase/schema.sql` in its SQL editor.
3. Create a dedicated demo user in Supabase Auth.
4. Change `demo@boloka.app` in `supabase/seed.sql` to that user's email and run the seed script.
5. Configure redirect URLs in Supabase Auth for the local frontend and deployed site.

The repository does not contain a live Supabase project URL, credentials, hosted URL, or demo password. Add those through the team's private configuration and share demo login details through the hackathon submission, never in this public repository.

## API

The contract is in [`docs/api.md`](docs/api.md). Routes are rooted at `/api/v1`; all routes except `/health` require a Supabase access token. Income and expense amounts are positive integer cents in ZAR. The API derives ownership from a verified token and scopes every database operation to that user.

The forecasting baseline groups income into weeks, weights recent weeks more heavily, accounts for known recent and recurring costs, and lowers confidence when history is sparse. It intentionally uses a transparent heuristic for this prototype rather than claiming model accuracy that has not been measured.

## Verify locally

```powershell
cd backend
pip install -r requirements.txt
pip install pytest ruff
ruff check .
pytest -q
cd ..\frontend
npm ci
npm run build
```

See [`docs/judge-demo.md`](docs/judge-demo.md) for the manual judge flow and [`docs/award-benchmark.md`](docs/award-benchmark.md) for product standards drawn from the FNB App of the Year materials.

See [`docs/deployment.md`](docs/deployment.md) for one-time Vercel, Render, and Supabase setup. A public live URL and judge account are not committed because the project has not been provisioned with team credentials.

## Current release status

The local API, database definition, synthetic seed, and pitch materials are prepared. Live hosting, a real demo account, and final Sonke submission depend on team-owned credentials and account access. No live deployment or user pilot is claimed in this README.

## Team

ThaKa — Kamogelo Skhosana and Thato Maluleka.

## License

MIT. See [`LICENSE`](LICENSE).
