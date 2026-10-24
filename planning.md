# Boloka Project Plan

Agile delivery plan for the FNB App of the Year 2026 hackathon (Financial Inclusion and Money Confidence challenge).

## Team (ThaKa)
- Kamogelo Skhosana (@Kamogelo-Skhosana): Backend, Data and cash planning, and submission artifacts.
- Thato Maluleka (@thato899): Frontend, UI/UX, Mobile (Capacitor), and QA.

## Methodology: Agile (Scrum-lite)
We run a compressed Scrum across the 72-hour window (Sat 24 to Mon 26 Oct):
- Backlog: GitHub Issues (45 tickets), each with an Owner and an Area.
- Sprints: three one-day sprints (Sat, Sun, Mon).
- Daily standup: posted as the Sonke daily update and recorded in status.md (done, next, blockers).
- Board: GitHub Issues filtered by assignee.
- We hold to the Definition of Ready and Definition of Done below.

## Sprint plan
### Sprint 1, Sat 24 Oct: Foundation
Repo and CI/CD, frontend scaffold, FastAPI skeleton, Supabase (Postgres and Auth), auth screens, income and expense entry, seed data. Hustle Pitch video (gate: Sat 13:30).

### Sprint 2, Sun 25 Oct: Differentiator and product
Transparent cash-planning baseline (pandas), shortfall and set-aside logic, forecast API, dashboard and shortfall alert card, low-data mode and i18n, deploy to Vercel and Render.

### Sprint 3, Mon 26 Oct: Package and submit
Capacitor signed APK and real-device test, end-to-end demo run, presentation deck, Lean Canvas, SSDL, README. Final Sonke submission (target 20:00, hard deadline 23:59).

## Milestones
- Sat 13:30: Hustle Pitch video uploaded.
- Daily before midnight: Sonke progress update.
- Mon 23:59: Final submission (repo link, build file, slides).

## Definition of Ready
- The issue has a clear title, an owner, and an area.
- Acceptance criteria are understood and dependencies identified.

## Definition of Done
- Code is merged to main through a reviewed pull request.
- CI is green (lint and tests) on the pull request.
- The feature works in the deployed environment and in the judge demo flow.
- No secrets are committed and the SSDL security rules are respected.

## Branching and workflow
- main is always deployable and gated by CI.
- Work happens on feature branches: feat/<area>-<short> or fix/<short>.
- Open a pull request to main, let CI pass, then squash-merge.
- Reference the issue in the pull request (for example, Closes #17).

## Risks and mitigations
- Over-scoping: if time runs short, cut in this order: scam-awareness module, then full i18n, then the APK.
- Forecast quality on sparse data: covered by the cold-start fallback (issue #22).
- Submission-system crunch near the deadline: submit early, by 20:00.
