# Responsible money-planning review

Reviewed the merged baseline at `c1a9067`. This review implements the requested
cross-cutting product correction in focused commits; it does not certify
forecast accuracy, language quality, security or user impact.

## Findings and acceptance criteria, recorded before editing

| Concern | Baseline finding | Acceptance |
| --- | --- | --- |
| Forecast credibility | A fixed 21-day warning date, unverified confidence, cash ignored, future expenses mixed with history, category-based bill merging | Explicit bounded calculation and assumptions; no likely risk/date; exact horizon totals; cash separated from ledger net; edge tests |
| Preview | Balance changed but weekly income and forecast did not | Ledger totals derive from records; unchanged fictional recommendation labelled on dashboard, forecast and savings; no API traffic |
| Corrections/privacy | Mutation endpoints existed without UI; no export/deletion policy | Reachable labelled edit/delete controls, confirmation/cancellation, preserved inputs on failure; scoped export; documented deletion decisions |
| Localization | Headings, dynamic messages, chart and accessible labels bypassed keys | Catalogued main-screen text; named interpolation; explicit fallback and fluent-speaker inventory |
| Maintainability | Large stateful App, duplicated totals, ML and docs out of step | Small modules, pandas-only baseline, incremental extraction plan |
| Readability | CSS compressed into one line | Readable CSS with unchanged parsed rules/declarations, then a production build |

## Calculation delivered

See `api.md` and `backend/app/forecasting.py` for the exact formula. The product
uses the last eight completed earning weeks including zero-record weeks. A
partial week is not extrapolated. Two completed weeks permit a simple income
mean; six plus a cost basis permit a conditional planning gap. These thresholds
are conservative prototype choices, not validated accuracy boundaries.

The horizon is tomorrow through 30 days from today in Africa/Johannesburg.
Explicit upcoming costs count once. Everyday costs use up to 30 days of
non-recurring history spanning at least 14 days. Past recurring costs are not
repeated without a due entry: the schema has no bill identity or cadence.
Zero projected everyday costs can mean unknown spending, not free living.
An upcoming non-recurring cost may overlap the everyday estimate. In that
case the combined total is a conservative scenario and the product suppresses
gap/set-aside recommendations. Resolving this requires a bill/budget identity
and completeness model rather than category-based deduplication.

Recorded net is an incomplete ledger total, not available cash. A separate
optional cash scenario uses a validated POST body, is not saved/exported, and
resets when records refresh or the account changes. Savings contributions are
transfer records, not extra income or a verified available balance. A planning
gap uses the stated cash assumption; it is never called a likely shortfall.
Weekly earnings cannot support a precise day. Confidence stays unvalidated.

The fitted Ridge model and scikit-learn dependency were removed. Its four-week
selection check was insufficient product evidence to justify added complexity.
Any future learned model needs consented evaluation, time-ordered backtests,
comparison with this baseline and agreed product acceptance before adoption.

Database reads now paginate to exhaustion, including short server pages, with
stable ID tie-breaking and an explicit failure at 100,000 records. They do not
silently treat one PostgREST page as complete history. Concurrent external
changes can still affect a multi-request snapshot; atomic exports would need
a database-side snapshot. This is a future engineering improvement.

## Implemented structure and next small steps

Current boundaries:

- `backend/app/forecasting.py`: pure planning calculation, with local date helper.
- `frontend/src/lib/client.js`: API and auth transport.
- `frontend/src/lib/transactions.js`: pure preview ledger mutations and export allowlist.
- `frontend/src/lib/sample.js`: fictional fixtures, kept out of backend requests.
- `frontend/src/lib/format.js`: locale-aware date and cents formatting.
- `frontend/src/lib/copy.js` and `strings.js`: copy selection, placeholders and explicit fallbacks.
- `components/TransactionList.jsx` and `screens/TransactionEditor.jsx`: accessible correction UI.

Next, extract the account-data loading lifecycle into one hook with session
cancellation tests. Then extract Forecast and Settings screens individually,
preserving their props and visual classes. Extract shared Field/Button only
after repeated behavior is clear. Do not replace routing, state management or
the design system as part of these steps. Keep each extraction independently
reviewable and run the same behavior tests before and after.

## Remaining team decisions

- Have fluent isiZulu and Sesotho reviewers approve the inventory in
  `localization-review.md`, including existing drafts. English fallbacks are
  visible and intentional; meaningful language support is not complete yet.
- Agree how users establish complete earning/spending history, identify
  recurring bills, record cadence/due dates and confirm available cash. A
  budget opening balance and an account balance are different product concepts.
- Choose a deletion policy and an owner: reauthentication, active-session
  revocation, deletion of Auth identity and all linked records, backups and
  retention, support contact, failure recovery and deletion confirmation.
  Do not label sign-out or individual record deletion as account deletion.
- Define a full account export (profile, transactions, savings and any stored
  forecasts), pagination/snapshot behavior, format and secure delivery. The UI
  JSON download is explicitly only currently loaded records, excludes auth
  tokens and scenario cash, and marks fictional exports. No legal compliance
  claim is made.
- Agree retention and access logging. Scenario cash is in a POST body rather
  than a URL, but hosting must still avoid logging request bodies and tokens.
- Decide whether savings records represent transfers between owned accounts
  or spending, before incorporating them into available cash.

## External setup and release verification

- Provision team Supabase/hosting and configure auth redirects, CORS and secrets.
- Run the schema and test cross-user reads, edits and deletion with two real
  non-production accounts. **Existing architecture limitation:** the backend
  uses a service-role token, which bypasses RLS; API filters scope those calls.
  This is not database-layer ownership enforcement for backend requests.
  Before using real financial data, choose caller-JWT database access or a
  database function/role that enforces the verified subject, and verify it.
- Verify account-backed scenario, edits, failed reloads and export on the
  deployed environment. Local mocks/preview checks do not establish that.
- Review the SSDL with the security owner, physical-device behavior and release
  signing. None is claimed complete by this review.

Ticket #10 follow-up: the service-role bypass described above was replaced by
caller-JWT database access. The API now requires a public project key and checks
issuer, expiry, audience, UUID subject and authenticated role. CI applies the
schema to PostgreSQL and checks two-subject ownership independently of API
filters. The original finding remains above as review history; configuration
migration and hosted two-account verification remain release requirements.

## Verification evidence

Focused tests cover missing/partial/future earning weeks, bounded windows,
exact horizon sums, due-date boundaries, shared-category bills, available cash,
insufficient histories, pagination and owner-scoped mutations. Frontend tests
cover preview create/edit/delete and totals, failed requests without local
mutation, export allowlisting, locale fallback/interpolation and a raw-copy
guard for main-screen JSX and accessible labels.

Final local checks passed: 63 backend tests, seven frontend tests, Ruff, ESLint and production build. The existing dependency-level TestClient deprecation warning remains; no live forecast accuracy is inferred from tests.

Headless Chrome against the local preview exercised add, edit, cancel, delete
confirmation/cancellation, JSON download and EN/isiZulu/Sesotho switching. It
checked 360/375/414/1120 widths, no horizontal overflow, no preview API calls
and no page errors. CSS was parsed before/after formatting: its original rule,
selector, declaration and at-rule signature was identical. New styles are
limited to the added correction controls and assumption/scenario sections.
