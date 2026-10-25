# Project status: Boloka

## Two-account release-check command - 25 October 2026

Ticket #35 adds an interactive, financial-record read-only check using two
seeded demo accounts. Passwords are hidden terminal input, not arguments/files;
caller JWTs verify API owners and direct foreign-row read denial. New QA
sessions are signed out with local scope. Mock-service tests cover leaks,
missing seeds, same-account input, service failure and unsafe targets. Actual
hosted execution still requires the operator's private credentials and URL;
no live two-account result is claimed and the release ticket remains open.

## Reproducible preview QA - 25 October 2026

Ticket #35 now has repository-owned Chromium checks for the fictional preview
journey, including edit/delete cancellation, exact totals, reference labels,
JSON export, language fallback, widths and zero attempted backend calls. CI runs
the browser checks without project credentials. The local frontend environment
is configured with public values; the local API health/CORS/auth-denial checks
pass. Hosted public Auth responds and finance tables deny anonymous probes.
Actual signed-in ownership and hosted judge-flow checks remain unverified, so
the ticket stays open.

Local validation: the Chromium journey, seven frontend unit tests, ESLint and
production build pass. npm audit reports three moderate advisories in the
pre-existing Capacitor CLI/xcode/uuid development chain; these dependencies are
unchanged by the browser runner addition and require a separate mobile tooling
upgrade assessment.

## Hustle Pitch preparation - 25 October 2026

Ticket #38's script now describes conditional planning and sparse-data guidance,
not a predicted warning. It distinguishes sample preview from a live demo,
requires an explicit upcoming bill and synthetic-data label, and includes a
recording/duration/upload checklist. No video was recorded or submitted; the
ticket stays open for those team actions.

## Canvas scope review - 25 October 2026

Ticket #40's draft now describes inspectable conditional planning instead of a
predicted tight week. Proposed metrics are separate from measured results, and
the draft includes a team-review/Sonke-save handoff. The actual page transfer
and privacy decisions remain external; the ticket stays open.

## Presentation content review - 25 October 2026

Ticket #39 has corrected slide copy covering the user journey, actual forecast
limits, architecture and private judge-access handoff. The existing PowerPoint
still contains dated-warning and sparse-heuristic wording; submission/README.md
flags it as outdated. The required presentation runtime/connected session is
unavailable, so the deck was not edited, rendered or approved. Transferring the
copy, visual review, live URLs and demo-access verification remain open.

## Judge README preparation - 25 October 2026

Ticket #42 now documents the actual JWKS setup, preserves existing .env files
in setup commands, explains the ownership/forecast architecture and explicitly
marks public URLs and judge-access handoff as unverified. It stays open until
the team supplies/validates deployment URLs and private demo access.

## CI/CD gating - 25 October 2026

Ticket #45: CI covers frontend, backend and PostgreSQL ownership/seed checks.
Production frontend deployment now requires a successful push-to-main CI run
from this repository and checks out exactly its tested commit. The manual
CI-bypass trigger is removed. Render is configured for checksPass. Vercel/Render
account configuration and actual deployment verification remain external release
work; skipped deployment is not reported as live hosting success.

## Set-aside logic - 25 October 2026

Ticket #18 confirms the conditional gap calculation and uses exact integer
ceiling for the weekly pace. Tests cover a one-cent gap, short/partial horizons,
large values and the minimal whole-cent pace property. Established zero-gap
wording is distinct from an unavailable recommendation. No affordability,
savings guarantee or precise bill-payment timing is claimed.

## Forecast API contract - 25 October 2026

Ticket #21 adds a shared Pydantic/OpenAPI response contract to both authenticated
forecast routes. Monetary fields, nullable cash, supported reason/action codes,
baseline method and unvalidated confidence/date policy are explicit. Tests
cover both contracts, unknown versus known-zero cash and database failure
propagation without sample-data substitution. Live deployment remains separate.

## Sparse-history guidance - 25 October 2026

Ticket #22 adds an input-specific checklist when history/costs are insufficient.
It requests actual recorded payouts, dated bills, overlap review and optional
cash only where needed. No invented income or numeric fallback is introduced.
The existing insufficient-data state and forecast thresholds are preserved.
New language keys require fluent review; hosted flow verification is separate.

## Forecast explanation layer - 25 October 2026

Ticket #20: expose the exact income numerator/denominator and cash assumption,
give specific reasons for withheld recommendations, and show an expandable
calculation in the account forecast using existing styles. Preview keeps its
fictional label and reference calculation unchanged. Arithmetic is preserved;
zero aggregate gap is explicitly not an on-time payment guarantee. New locale
keys remain visible English fallbacks pending fluent review. Live deployment
verification remains part of the separate release tickets.

Validation: 138 backend tests, Ruff, seven frontend tests, ESLint and production
build pass. Browser checks at 375px cover keyboard expansion, conditional gap,
sparse history, covered costs, English fallback and placeholder interpolation.
An existing randomized EC-key test fixture now preserves fixed-width P-256
coordinates, removing intermittent invalid-fixture failures.

## Synthetic demo dataset - 25 October 2026

Ticket #14: seed data now requires explicit account selection and confirmation,
replaces only marked fictional rows, preserves other entries, and uses the
South African calendar. Fixtures cover eight completed weeks with earning gaps
and explicitly dated costs at/after the horizon. PostgreSQL CI exercises repeat
runs, account isolation, missing configuration and scheduled totals. No hosted
data was changed; account provisioning and the live judge flow remain external.

## Supabase signing keys - 25 October 2026

Added ES256/RS256 verification using project public JWKS, retaining explicit
legacy HS256 configuration. Local validation: 133 backend tests and Ruff pass.
The configured project's public JWKS responds with ES256 keys; no private key
is used or recorded. Live sign-in and the two-account hosted RLS test remain
release requirements. Rotate any secret shared outside private environment
settings; user-data routes need only the public key and caller JWT.

## Review branch - 24 October 2026

The responsible money-planning review starts from merged main at c1a9067.
PR #52 is merged. The follow-up for ticket #10 replaces service-role database
access with the caller JWT and a public project key, and adds real PostgreSQL
ownership checks to CI. PR #53 passed all CI jobs and is merged. Deployment
migration and a real two-account test remain.

Ticket #13 adds bounded UTF-8 CSV parsing, shared income validation, precise
money parsing and line-number errors. Malformed files are rejected before any
write; valid rows preserve source/note text instead of silently truncating it.
Reimports are explicitly documented as adding duplicates. Local validation:
119 backend tests, seven frontend tests, Ruff, ESLint and production build pass.

Implemented:

- Transparent pandas-only baseline, bounded completed-week history, explicit upcoming costs/cash assumptions, exact horizon totals, no precise date/likely warning, unvalidated confidence.
- Paginated reads, optional unsaved cash scenario in a validated POST body, owner-scoped mutation checks.
- Consistent preview totals with frozen fictional recommendations clearly labelled; no preview API requests.
- Accessible income/expense edit/delete, confirmation/cancellation, scoped loaded-record JSON export and honest account-deletion limitations.
- Catalogued main-screen copy, named placeholders, visible English fallbacks and a fluent-speaker review inventory.
- Small transaction/preview/format/account-data modules and readable CSS preserving the original rule/declaration signature.

Validation evidence and findings are in docs/product-review.md.
No forecast accuracy, language approval, user impact or live deployment is claimed.

Remaining team decisions:

- Current-catalog fluent review is complete; new recurring-bill/history/cash concepts need product and translation review when added.
- Full export scope, deletion identity verification, retention/backups, support ownership and contact route.
- Apply and verify database-layer ownership: the API now forwards caller JWTs;
  configure the public project key and run the hosted two-account release test.

External setup:

- Team Supabase/hosting, schema, secrets, redirects and CORS.
- Two-account security and live account-backed flow tests, physical-device/release-signing checks and SSDL approval.
- Actual Sonke submission, pitch recording and consented user evaluation.

## Assigned submission and mobile work - 25 October 2026

Issue #31: the current frontend builds successfully as an Android debug APK and
installs/launches on the available Android SDK emulator (`Android SDK built for
x86_64`). This verifies the wrapper's basic startup only. No physical phone is
connected, and the team's release keystore is not available in this workspace;
the signed release artifact and real-device acceptance remain open. The APK is
generated locally and ignored by Git.

Issue #41: `submission/ssdl-security.md` now records the reviewed `main`
baseline, architecture and trust boundaries, data/session handling, controls,
threat mitigations, evidence limits and owner-specific release gates. PR #69 is
merged. CI has disposable two-user PostgreSQL RLS checks, and PR #70 adds a
tested, non-destructive read check for two populated accounts. No live hosted
run is recorded. The required Sonke template/security-owner approval, hosted
read check, separate write/delete verification, retention/deletion and
operational ownership decisions remain open; this is not a security
certification.

Issue #36: the connected Vercel account still has no Boloka project and exposes
only the personal workspace. A team-owned project or team access is needed
before deployment; no production URL is claimed.

Issue #28: PR #68 has merged. The project owner recorded fluent-speaker approval
for both isiZulu and Sesotho, and the issue is closed.

Issue #43: this repository records today's progress. The private Sonke update
has not been submitted or verified, so the submission requirement remains
open.
