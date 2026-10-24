# Pitch content for review (ticket #39)

This is corrected slide copy and speaker guidance, not a rendered or approved
deck. The existing `Boloka-pitch.pptx` predates the responsible forecast review:
its dated-warning and sparse-heuristic language must be replaced before use.
Do not present that file as an up-to-date product specification. Preserve its
visual direction when transferring this copy, then render and inspect every
changed slide. The presentation authoring runtime is unavailable in this session.

## 1. Income comes in waves. Costs still arrive

Boloka helps people with irregular incomes plan around upcoming costs.

Speaker: This is a prototype with fictional demo data. No user impact or forecast
accuracy has been established. Save, before you have to, is the product aim.

## 2. The planning problem

Payout amounts vary. Rent, transport, food and data still need a plan.
A recorded balance describes entries so far; it is not available bank cash.

Speaker: This problem framing is a hypothesis to test with users. Do not present
the illustrative earning pattern as research or a prediction of a dry spell.

## 3. An illustrative user journey

Kea receives freelance and delivery payouts and has rent coming up.
She records actual payouts, enters known bills with dates, and checks the
planning estimate before deciding what she can realistically set aside.

Speaker: Kea is a fictional persona. The app does not know when the next payout
will arrive. A suggested weekly pace does not establish affordability.

## 4. Three actions in the product

1. Record and correct income and costs, in rand and cents.
2. Inspect the next-30-day estimate and its assumptions.
3. Review a conditional gap or follow the missing-input checklist.

Speaker: A past recurring flag does not schedule a future bill. Enter an actual
upcoming date. Explain sample preview versus an account-backed demo explicitly.

## 5. The calculation is inspectable

Illustrative arithmetic only, not a live forecast:

- Estimated costs R2,000 minus estimated income R1,200 minus entered cash R300
  gives a conditional horizon gap of R500.
- R500 multiplied by 7 and divided by 30 gives R116.67 per week, rounded up to
  cents. This is a planning pace, not money already saved.
- No shortfall date or probability is predicted. A zero aggregate gap does not
  show that each bill can be paid on time.

Speaker: Income uses up to eight completed earning weeks with internal empty
weeks counted as zero recorded earnings. A set-aside recommendation requires six
completed weeks plus a cost basis and no ambiguous cost overlap. Missing cash is
unknown, with zero assumed in the scenario. Confidence is low and unvalidated.

## 6. Sparse history and trust

Insufficient inputs get a checklist, not an invented savings amount:
record actual payouts, add dated bills, review overlapping costs and optionally
enter available cash. Missing entries can change the estimate.

Speaker: No ML dependency is needed for this pandas baseline. Do not claim that
tests establish real-world forecast accuracy. Language drafts use visible
English fallback until fluent isiZulu/Sesotho reviewers approve the wording.

## 7. Technical architecture

React/Vite frontend -> authenticated FastAPI API -> Supabase Postgres with RLS.
Supabase Auth issues the user token. The API verifies its project signature,
issuer, audience, expiry and identity, then forwards it with the public key.
PostgreSQL independently checks ownership. pandas computes the planning estimate.

Speaker: No secret/service-role key is used for user-data routes. Preview entries
stay in the browser session. Optional cash is not persisted. GitHub CI checks
frontend, backend and PostgreSQL ownership; hosting still needs live verification.

## 8. Judge demo and access handoff

Use the [judge runbook](../docs/judge-demo.md): sign in, add/correct an entry,
enter an upcoming cost, inspect the explanation, import a bounded CSV, sign out
and verify persistence after signing back in.

Public frontend/API URLs and dedicated-account sign-in are not yet verified.
Provide the actual URLs only after the release check. Share the demo email and
password in the private Sonke field, never this public deck or repository.

Speaker: Do not put a placeholder link on screen as working access. If hosting
is unavailable, identify the fictional preview or backup recording honestly.

## 9. Proposed validation and adoption

A proposed first pilot: 10–20 consenting participants, four weeks, one community
partner. Test logging, comprehension of the calculation, whether a weekly action
is feasible, task completion and return visits.

Speaker: No pilot has been completed. Revenue and partnership plans are
hypotheses. Real-data evaluation needs consent and an agreed deletion/retention
process. No personal transaction-data sales are proposed.

## 10. The next evidence we need

Can people understand the assumptions and make a feasible plan around their
known bills? Complete the live judge flow and fluent-language review, then test
the core planning journey with consenting users.

Speaker: Report sample size, dates, failures and limitations with any later
evaluation. Do not imply that improved financial outcomes have been demonstrated.

## Source and handoff checklist

Source of implementation claims: [API contract](../docs/api.md),
[forecast logic](../backend/app/forecasting.py),
[product review](../docs/product-review.md),
[database schema](../supabase/schema.sql), and
[localization review](../docs/localization-review.md).

- Transfer corrected text into the editable deck and preserve its visual style.
- Add the architecture and judge-access content without crowding existing slides.
- Render and visually inspect all changed slides, including font/text fit.
- Verify public URLs and private judge credentials through the hosted runbook.
- Obtain team review before final upload. Ticket #39 remains open.
