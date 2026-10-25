# Deployment setup

## Vercel frontend

The repository contains the GitHub Actions deployment workflow. It runs only after CI succeeds on `main`. In GitHub, configure:

- Secret: `VERCEL_TOKEN` (least privilege needed to deploy the project).
- Repository variables: `VERCEL_ORG_ID` and `VERCEL_PROJECT_ID`.
- Vercel project root directory: `frontend`.
- Production branch: `main`.

In the Vercel project's **Production** environment, set these build-time
variables before redeploying:

| Name | Value |
| --- | --- |
| `VITE_SUPABASE_URL` | The team's Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | The project's public anon/publishable key; never a secret or service-role key |
| `VITE_API_BASE_URL` | `https://boloka.onrender.com/api/v1` |

Vite embeds `VITE_*` values during the production build. After saving the
variables, trigger a new Production deployment; changing settings does not
repair an already-built deployment. The account screen only renders the
email/password sign-in and account-creation forms when both Supabase variables
are present. Verify that the forms appear, then sign in with the team's
authorized demo account and confirm its seeded records load from the API.
Never put the demo credentials in this repository or a public issue.

The workflow skips safely until all three values are configured. It passes the token through the step environment and pins the Vercel CLI version. Add the public frontend URL to the backend's `CORS_ORIGINS` after the first Vercel deployment.

Production deploys only after successful CI from a push to this repository's
`main`. It checks out that CI run's exact commit. Pull-request runs and fork
runs cannot deploy. There is no manual dispatch that bypasses CI. To redeploy,
rerun the successful push-to-main CI workflow for the desired release commit;
confirm the intended release is still current before rerunning an older run.
Repository CI/CD configuration can be complete while live hosting remains
unconfigured; ticket #37 tracks the hosted API and its real health check.

## Render API

The root `render.yaml` defines a Python web service in Frankfurt, checks `/api/v1/health`, pins Python 3.12.11, and deploys only when GitHub checks pass. Create a Render Blueprint from the repository and provide these values in Render's private environment prompt:

- `SUPABASE_URL`
- `SUPABASE_PUBLISHABLE_KEY`
- `CORS_ORIGINS` (the exact Vercel origin, no trailing slash)

No secrets are stored in the Blueprint. Render's region and compute plan should be confirmed in the team account before applying the Blueprint.

Migration for ticket #10: configure `SUPABASE_PUBLISHABLE_KEY` and remove
`SUPABASE_SERVICE_ROLE_KEY` from the API service. User-data routes reject
privileged project keys. Apply the updated schema grants/RLS before deployment.
ES256/RS256 signing keys are fetched from the project's HTTPS JWKS endpoint
automatically. Optional `SUPABASE_JWKS_URL` must match the project's
`/auth/v1/.well-known/jwks.json` URL exactly. Only legacy HS256 projects need
`SUPABASE_JWT_SECRET` added manually in Render. Secret API keys are not JWT
signing secrets. Never configure an `sb_secret_` key for user-data routes.
Signing-key rotation is observed within the 60-second public-key cache lifetime.

## Supabase

Create or select a team-owned project and region, run `supabase/schema.sql`, then copy the project's URL and server credentials into the private deployment settings above. Both API and frontend use a publishable/anon project key. The API forwards the verified caller access token so database RLS checks ownership. No service-role key is needed for user-data routes. Configure Supabase Auth's allowed redirect URLs for local development and the deployed frontend.

## Release gate

1. Merge a reviewed PR to `main`.
2. Confirm GitHub CI completed successfully.
3. Confirm Render reports a healthy deployment and `/api/v1/health` returns `{"status":"ok"}`.
4. Sign in through the deployed frontend, exercise a small income/expense entry and forecast, then sign out.
5. Keep the judge demo account and password in the private Sonke submission, not in this repository.

The repository has no live service credentials. This configuration prepares the services but does not claim that either has been provisioned or deployed.
