# Judge demo runbook

## Before the demo

- Deploy the frontend and API; verify the public HTTPS URLs and `GET /api/v1/health`.
- Configure Supabase redirect URLs and confirm sign-in works from the deployed site.
- Create a dedicated judge account and follow [synthetic dataset setup](../supabase/README.md) before running `supabase/seed.sql`.
- Keep the demo password out of GitHub and this public repository. The owner uploaded a credential-filled judge guide through Sonke's file submission. No dedicated private credentials field was identified; verify recipient access with the organisers before sharing further credential copies.
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
6. Preview a CSV with valid and invalid rows; confirm that nothing is saved yet. Correct a valid row, exclude another, inspect each page and cancel once. Preview again, explicitly save the selected rows, then show the imported/skipped counts.
7. Sign out, then sign back in and confirm the data remains.

## Recovery checks

- If there is no network, explain that the current prototype requires a connection for authenticated data. Do not imply offline writes are supported.
- If the account is locked or an endpoint is unavailable, show the backup recording and report the issue rather than changing data on a shared account.
- Delete demo data only after the judging window. Rerunning the seed replaces only its marked fictional rows; other entries remain and affect totals. It does not reset the account.

## Technical acceptance checklist

### Private two-account read check

Use two distinct dedicated demo accounts, each with seeded income and expenses.
From an interactive terminal in `backend/`, with the usual public-key `.env`
configuration, run:

```powershell
python -m app.release_check --api-url http://localhost:8000/api/v1
```

For the hosted check, replace the API URL with the actual HTTPS base ending in
`/api/v1`. The command shows its API/Auth targets, then prompts for emails and
hidden passwords in the terminal. Do not put passwords/tokens in command-line
arguments, chat, screenshots or files. Credentials/tokens stay in memory. It
signs in through the configured project, checks account-backed list/summary/
forecast responses, requires seeded rows, verifies owners and probes direct
PostgREST foreign-user reads with each user's JWT. It signs out only its new
QA sessions using local scope; existing browser sessions are not signed out.
By default it never writes or deletes financial records. Both modes reject privileged API keys.

Record only the release commit, date, target environment, pass/fail and account
aliases A/B. A successful run verifies these read checks, not write/delete
isolation, re-login persistence, browser redirect/CORS behavior, physical-device
acceptance or forecast accuracy. Empty accounts cannot establish a meaningful
cross-account test. The owner later confirmed the end-to-end judge demo passed
and closed #35. These command limitations are supplemental evidence boundaries;
the outstanding Sonke upload and receipt are tracked separately in #44.
The command's automated tests use mock services; they are not live evidence.

### Opt-in two-account write/delete check

Use **dedicated synthetic accounts only**, after the read check succeeds. From
`backend/`, use the same virtual environment and public-key configuration:

```bash
# Windows Git Bash (interactive password prompts)
winpty ./.venv/Scripts/python.exe -m app.release_check --api-url https://boloka.onrender.com/api/v1 --check-writes
```

In PowerShell, use `.\.venv\Scripts\python.exe` instead of `winpty ...`.
The default command remains read-only; `--check-writes` explicitly enables
mutations. Warm the API with its health endpoint first. Enter credentials only
at the interactive prompts; never paste credentials or tokens into chat.

The checker reads existing IDs, prints a unique `Boloka isolation QA <UUID>`
marker, and creates temporary one-cent income, expense and savings rows. It
checks both A-against-B and B-against-A through API ownership checks and direct
PostgREST RLS. Positive own-account updates prevent a general write outage from
looking like successful isolation. Foreign updates/deletes must be denied and
leave the owner's row unchanged; spoofed inserts and ownership transfers must
also be denied. Savings has no API update route, so its update checks use
PostgREST. Successful own API deletes must persist.

Cleanup runs after failures, including a timed-out create, and verifies removal
of exact marked rows under both accounts. It refuses to delete IDs observed
before the run. Keep the printed marker until completion: closing/killing the
process or losing connectivity can leave temporary rows. If cleanup fails,
inspect only rows matching that exact marker in the dedicated accounts; do not
reset accounts or rerun the seed to remove unrelated entries. QA sessions are
signed out after cleanup is attempted.

Record only commit, date, environment, A/B aliases, pass/fail and cleanup result.
Share the final summary, never raw credential/session output. Automated tests
use mock services and do not establish live isolation. This command does not
verify browser redirects, re-login persistence, accessibility, network recovery,
physical-device acceptance or forecast accuracy. The owner confirmed the full
judge demo flow passed and closed #35; these are documented limits of this
optional checker, not a request to reopen it. Final submission and receipt remain
under #44.

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
accounts or Android behavior. The owner confirmed the full judge demo flow and
closed #35. The checklist below is a technical reference and its unchecked items
are not represented as agent-verified. Final submission and receipt remain under
#44.

- [ ] Only `/api/v1/health` is publicly readable.
- [ ] A user cannot read, edit, or delete another user's rows.
- [ ] Invalid amounts and malformed dates are rejected.
- [ ] CSV file size and format are bounded and validated.
- [ ] Forecast has a low-data response and an explanation.
- [ ] CORS allows only the configured origins in production.
- [ ] No service key, real email/password, or private user transaction appears in source or screenshots.

The owner confirms production sign-in, seeded records, persistence, the judge walkthrough and a signed-APK test on Galaxy A15 SM-A155F/DSN (Android 16). The two-account read check also passed by operator report. These confirmations do not establish cross-account mutation denial, all accessibility/network-recovery cases, measured performance or forecast accuracy. Keep those evidence boundaries when reporting release readiness.
