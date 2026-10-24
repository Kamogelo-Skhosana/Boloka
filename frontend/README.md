# Boloka Frontend

Responsive React + Vite app for people with irregular incomes. The first release includes the money overview, plain-language forecast, income and expense entry, CSV import, savings guidance, and Supabase sign-in/sign-up.

## Run locally

    npm ci
    npm run lint
    npm run dev

The app opens a clearly labelled fictional preview when no account is signed in. Preview changes stay in app memory and are not uploaded. For account-backed use, copy `.env.example` to `.env` and set:

- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`
- `VITE_API_BASE_URL`

Use only the publishable/anon key in the browser. Never expose a service-role key or other secret. The backend URL must include the API version prefix if it is not proxied as `/api/v1`.

## Product and accessibility

The interface follows `../docs/design.md`: dark green surfaces, teal actions, warm shortfall alerts, and a mobile-first layout. Sample values are labelled, forecast confidence and limitations are visible, and set-aside progress is not shown until tracking exists. Keyboard focus, skip navigation, semantic landmarks and labels, live status messages, reduced-motion support, and large touch targets are included.

See `../docs/api.md` for the API contract and `../agents.md` for repository conventions.
