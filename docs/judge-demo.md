# Judge demo runbook

## Before the demo

- Deploy the frontend and API; verify the public HTTPS URLs and `GET /api/v1/health`.
- Configure Supabase redirect URLs and confirm sign-in works from the deployed site.
- Create a dedicated judge account and follow [synthetic dataset setup](../supabase/README.md) before running `supabase/seed.sql`.
- Keep the demo password out of GitHub and this public repository. Put it in Sonke's private submission field.
- Test from a second browser/device with no developer session. Check mobile width, keyboard entry, slow network, and sign-out.
- Check keyboard-only navigation and visible focus, confirm the chart has readable range labels, and check reduced-motion behavior.
- Record a short backup walkthrough and confirm judges can access its link.

Until Supabase is configured, use the clearly labelled sample preview only to demonstrate layout and interactions. Its values are fictional, preview entries are temporary, and it is not a substitute for the deployed, account-backed judge flow.

## Walkthrough

1. Open the hosted app and sign in with the dedicated demo account.
2. Point out the seeded, irregular income history and recurring costs. State clearly that the values are synthetic.
3. Add a sample payout and verify it appears in the user's income history.
4. Add a recurring expense and verify the recurring flag and amount.
5. Open the forecast. Explain the exact horizon, conditional planning gap, unvalidated confidence and cash/history assumptions. State that no payout day or shortfall date is predicted. Enter upcoming costs explicitly: a past recurring flag does not create a due date.
6. Import a CSV with one valid row and one invalid row; show the imported/skipped counts.
7. Sign out, then sign back in and confirm the data remains.

## Recovery checks

- If there is no network, explain that the current prototype requires a connection for authenticated data. Do not imply offline writes are supported.
- If the account is locked or an endpoint is unavailable, show the backup recording and report the issue rather than changing data on a shared account.
- Delete demo data only after the judging window. Rerunning the seed replaces only its marked fictional rows; other entries remain and affect totals. It does not reset the account.

## Technical acceptance checklist

### Reproducible preview browser checks

From `frontend`, run `npm ci`, `npx playwright install chromium`, then
`npm run test:e2e`. CI runs these checks in Chromium. They start an isolated
local server with Supabase configuration disabled, use fictional preview only,
and reject any attempted API/Supabase request. They cover create/edit/cancel/
delete, confirmation, totals, static-reference labels, fictional JSON export,
language fallback and responsive widths. Reports are ignored by Git.

If Chromium is already installed elsewhere, optional
`PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH` selects its executable for a local run.
These checks do not establish hosted Auth, database ownership between real
accounts, Android behavior, or a successful live judge demo. Complete the
account-backed checklist below before closing #35.

- [ ] Only `/api/v1/health` is publicly readable.
- [ ] A user cannot read, edit, or delete another user's rows.
- [ ] Invalid amounts and malformed dates are rejected.
- [ ] CSV file size and format are bounded and validated.
- [ ] Forecast has a low-data response and an explanation.
- [ ] CORS allows only the configured origins in production.
- [ ] No service key, real email/password, or private user transaction appears in source or screenshots.

The repository currently has no live service credentials. Complete the deployment, account, and device checks above before presenting the flow as live.
