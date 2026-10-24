# Deployment setup

## Vercel frontend

The repository contains the GitHub Actions deployment workflow. It runs only after CI succeeds on `main`. In GitHub, configure:

- Secret: `VERCEL_TOKEN` (least privilege needed to deploy the project).
- Repository variables: `VERCEL_ORG_ID` and `VERCEL_PROJECT_ID`.
- Vercel project root directory: `frontend`.
- Production branch: `main`.

The workflow skips safely until all three values are configured. It passes the token through the step environment and pins the Vercel CLI version. Add the public frontend URL to the backend's `CORS_ORIGINS` after the first Vercel deployment.

## Render API

The root `render.yaml` defines a Python web service in Frankfurt, checks `/api/v1/health`, pins Python 3.12.11, and deploys only when GitHub checks pass. Create a Render Blueprint from the repository and provide these values in Render's private environment prompt:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_JWT_SECRET`
- `CORS_ORIGINS` (the exact Vercel origin, no trailing slash)

No secrets are stored in the Blueprint. Render's region and compute plan should be confirmed in the team account before applying the Blueprint.

## Supabase

Create or select a team-owned project and region, run `supabase/schema.sql`, then copy the project's URL and server credentials into the private deployment settings above. The backend service key is server-only; the frontend must use only the publishable/anon key. Configure Supabase Auth's allowed redirect URLs for local development and the deployed frontend.

## Release gate

1. Merge a reviewed PR to `main`.
2. Confirm GitHub CI completed successfully.
3. Confirm Render reports a healthy deployment and `/api/v1/health` returns `{"status":"ok"}`.
4. Sign in through the deployed frontend, exercise a small income/expense entry and forecast, then sign out.
5. Keep the judge demo account and password in the private Sonke submission, not in this repository.

The repository has no live service credentials. This configuration prepares the services but does not claim that either has been provisioned or deployed.
