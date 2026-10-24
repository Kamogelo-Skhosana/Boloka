# Boloka Frontend

Responsive React + Vite app for people with irregular incomes. The first release includes accessible first-run onboarding, a money overview, plain-language forecast, income and expense entry, CSV import, set-aside contribution tracking, Supabase sign-in/sign-up, isiZulu/Sesotho key-screen copy, low-data options, and a Capacitor Android wrapper.

## Run locally

    npm ci
    npm run lint
    npm run dev

Themeloom is included as a pinned Git submodule. After a fresh clone, run `git submodule update --init --recursive` before `npm ci` and the Vite build.

The app opens a clearly labelled fictional preview when no account is signed in. Preview changes stay in app memory and are not uploaded. Recorded totals update after create/edit/delete, but the recommendation stays an explicitly labelled fictional reference estimate. For account-backed use, copy `.env.example` to `.env` and set:

- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`
- `VITE_API_BASE_URL`

Use only the publishable/anon key in the browser. Never expose a service-role key or other secret. The backend URL must include the API version prefix if it is not proxied as `/api/v1`.

## Product and accessibility

The interface follows `../docs/design.md`: dark green surfaces, teal actions, warm shortfall alerts, and a mobile-first layout. Sample values are labelled, forecast confidence and limitations are visible, and set-aside progress is not shown until tracking exists. Keyboard focus, skip navigation, semantic landmarks and labels, live status messages, reduced-motion support, and large touch targets are included.

See `../docs/api.md` for the API contract and `../agents.md` for repository conventions.

## Local preferences and offline behavior

The first run explains the core workflow and can lead directly to income entry. The settings screen includes English, isiZulu and Sesotho key-screen copy plus a low-data preference. Language and the low-data preference use local storage. The service worker caches only the app shell and static assets; it deliberately never caches private `/api/` responses. Account changes need a connection and show a retry/offline message.

The initial translations are product drafts and should be reviewed by fluent isiZulu and Sesotho speakers before a public launch.

## Corrections, export and source structure

All loaded income/expense entries are reachable from the dashboard. Edit preserves existing values; Delete names the amount/date and requires confirmation. Cancellation leaves the record unchanged; failed saves retain editor inputs. Upcoming expenses can use a future due date.

Settings exports only currently loaded records as JSON, excluding auth tokens and marking sample data as fictional. This is not a full account export or account deletion. See `../docs/product-review.md` for privacy decisions and release limitations.

Pure preview operations and export fields live in `src/lib/transactions.js`; fixtures in `sample.js`, formatting in `format.js`, empty account state in `account-data.js`, API transport in `client.js`, and copy in `copy.js`/`strings.js`. The transaction list/editor are extracted incrementally. `../docs/localization-review.md` records missing strings; English fallbacks remain visible until fluent review.

Run `npm test`, `npm run lint` and `npm run build`. Tests guard preview totals/mutations, export fields, localization fallbacks and raw JSX copy.

## Android

Android platform files are tracked under `android/`. With Java 21 and Android SDK/build tools installed:

    npm run mobile:sync
    npm run mobile:apk

This produces a debug APK at `android/app/build/outputs/apk/debug/app-debug.apk`, signed with the local Android debug key. A store/release APK needs a team-owned signing key stored securely in CI. Install and verify the package on a physical Android phone before closing the device-testing ticket.
