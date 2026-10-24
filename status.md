# Project Status: Boloka

Living status log of delivery and release readiness.

## Snapshot — 24 October 2026

- The feature work is on `feat/kamogelo-owned-issues` and awaits review in PR #46 to `main`.
- `main` was fetched and merged into the feature branch before this round of UI work.
- Backend API, synthetic seed, database schema/RLS, responsive preview UI, forecast and submission drafts are present in the branch.
- CI and deployment workflows are configured but have not yet passed on the updated pull request. Hosting secrets and a Supabase project are not configured here.
- The sample dashboard uses fictional values. Preview changes are temporary and are never sent to Supabase.
- No public deployment, real judge account, user pilot, recorded Hustle Pitch video, or Sonke final submission is claimed.

## Completed in the current feature branch

- Income and expense API routes with authenticated ownership checks, CSV import, and tests.
- Weekly income aggregation, explainable shortfall/set-aside estimates, and sparse-history behavior.
- Mobile-first dashboard, transaction entry, CSV upload, forecast, savings guidance, and account screens.
- Keyboard-visible focus, skip link, labelled forms, semantic navigation, live status messages, reduced motion, and a small-screen layout check.
- CI/deployment configuration, synthetic demo seed, judge runbook, award benchmark, Lean Canvas draft, pitch script, and editable deck.

## Remaining release work

- Review and merge PR #46 after CI passes.
- Provision the team Supabase project, apply the schema, configure secrets, and create a private judge account.
- Connect hosting, then test account sign-in and the API with seeded data on the deployed site.
- Run the complete demo on a second device, including network-failure and keyboard checks.
- Record the real 20-second pitch and complete the Sonke Canvas/final submission.
- Conduct consented user walkthroughs and validate forecast quality before making impact or accuracy claims.
