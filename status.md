# Project Status: Boloka

Living status log of implementation and release readiness.

## Snapshot — 24 October 2026

- Latest `origin/main` was fetched before work; this branch starts at `1d752c8`.
- Current work is on `feat/complete-assigned-tickets`, prepared for review in a PR targeting `main`.
- Frontend lint/build and backend Ruff/pytest pass locally. Android debug APK builds and installs on the available Android emulator.
- The preview uses fictional values. Preview edits stay in memory and are never sent to Supabase.
- No production Supabase project or credentials are configured in this checkout. The live account-backed journey still needs team setup.

## Implemented in this branch

- Themeloom theme integration using the team's source repository as a pinned submodule; React/Vite/Tailwind frontend configuration.
- Supabase email/password UI and session-backed API use, income and expense forms, forecast dashboard, savings contribution API/UI, shortfall card and onboarding.
- English/isiZulu/Sesotho key-screen copy, low-data option, privacy-safe app-shell caching, and scam-awareness nudge.
- Loading, retry, offline, empty and error states; responsive layouts, labels, keyboard focus, skip link, reduced-motion support, and forecast values alongside the chart.
- Capacitor Android project and debug APK build workflow.
- SSDL engineering draft and API contract updates.

## Still needs team input or external setup

- Apply the updated Supabase schema, set hosting secrets, configure auth redirects/CORS, and test with two non-production accounts.
- Review isiZulu and Sesotho with fluent speakers; current strings are draft translations.
- Confirm the required SSDL submission template and security-owner review; `submission/ssdl-security.md` is a working draft.
- Install on a physical phone and sign a release APK with the team's release key. Only an emulator and debug signing are available here.
- Complete Vercel setup/deployment and verify the app is publicly reachable with the team's approved backend configuration.
- Post the remaining scheduled Sonke updates when those dates arrive; no future update is being claimed as completed.
- Complete the actual Sonke submission, pitch video, consented user walkthroughs and forecast validation before impact or accuracy claims.
