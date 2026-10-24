# Judge demo runbook

## Before the demo

- Deploy the frontend and API; verify the public HTTPS URLs and `GET /api/v1/health`.
- Configure Supabase redirect URLs and confirm sign-in works from the deployed site.
- Create a dedicated judge account and seed the synthetic data using `supabase/seed.sql`.
- Keep the demo password out of GitHub and this public repository. Put it in Sonke's private submission field.
- Test from a second browser/device with no developer session. Check mobile width, keyboard entry, slow network, and sign-out.
- Record a short backup walkthrough and confirm judges can access its link.

## Walkthrough

1. Open the hosted app and sign in with the dedicated demo account.
2. Point out the seeded, irregular income history and recurring costs. State clearly that the values are synthetic.
3. Add a sample payout and verify it appears in the user's income history.
4. Add a recurring expense and verify the recurring flag and amount.
5. Open the forecast. Explain the horizon, likely gap, confidence label, and why the suggestion was made.
6. Import a CSV with one valid row and one invalid row; show the imported/skipped counts.
7. Sign out, then sign back in and confirm the data remains.

## Recovery checks

- If there is no network, explain that the current prototype requires a connection for authenticated data. Do not imply offline writes are supported.
- If the account is locked or an endpoint is unavailable, show the backup recording and report the issue rather than changing data on a shared account.
- Delete demo data only after the judging window; the seed script intentionally clears and recreates rows for the selected demo user.

## Technical acceptance checklist

- [ ] Only `/api/v1/health` is publicly readable.
- [ ] A user cannot read, edit, or delete another user's rows.
- [ ] Invalid amounts and malformed dates are rejected.
- [ ] CSV file size and format are bounded and validated.
- [ ] Forecast has a low-data response and an explanation.
- [ ] CORS allows only the configured origins in production.
- [ ] No service key, real email/password, or private user transaction appears in source or screenshots.

The repository currently has no live service credentials. Complete the deployment, account, and device checks above before presenting the flow as live.
