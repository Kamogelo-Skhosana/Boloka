# Shortfall timing: validation gate (#19)

## Current finding

The production pandas forecast averages up to eight completed earning weeks.
Zero recorded weeks are retained; partial weeks are excluded. It cannot infer
the next payout day, verify available cash, or establish complete bill/spending
coverage. A positive 30-day gap does not identify a date; a zero gap does not
prove every bill can be paid on time. Production therefore keeps
`shortfall.likely=false` and `shortfall.date=null`.

Do not distribute weekly averages across days and label the first negative
running total a likely shortfall date. Do not use fictional seeds as evidence
that dated predictions work. No new AI/ML dependency is needed for evaluation.

## Work delivered

`backend/app/timing_validation.py` is an offline evaluator of candidate dates,
not a predictor or an API endpoint. It requires one observed closing cash amount
for every future horizon day, an explicit completeness declaration, timezone-aware
cutoff/prediction timestamps, and a candidate date inside that horizon or null
for abstention. Missing days, duplicates, unknown fields, fractional money,
boolean money and predictions recorded after the cutoff fail validation.

The outcome is the **first negative end-of-day cash**. Zero is not negative.
This is a research definition, not a record of intraday missed payments:
cash observed at day's end can hide a bill that could not be paid earlier.
If people cannot have negative cash without borrowing, this label may miss unmet
needs entirely. Validate the outcome definition with participants before a pilot.
The evaluator rejects incomplete cases rather than silently filling gaps with
zero. Validation cannot establish that the supplied completeness claim is true.

Reports contain aggregate event true/false positives/negatives, precision,
shortfall recall, false-alarm rate, abstentions, matched-date absolute/signed
error and recall within a preselected date tolerance. Wrong-date warnings count
as event detections but not timely detections. Date error is conditional on both
an actual event and a warning, so always read it alongside missed-event counts.
Undefined rates are null, never reported as perfect scores. Always-warn and
always-abstain event counts expose trivial strategies; neither validates timing.
No probability calibration or forecast accuracy is claimed by these reports.

## Private local use

Use consented, de-identified records only after the team's data-handling review.
Keep datasets outside Git, for example under ignored `output/validation/`.
Do not include email, passwords, tokens, account IDs or free-text transaction notes.
The evaluator has no network calls or backend writes and outputs aggregates only.
Do not publish small-cohort results that could identify participants.

Fictional format example (three days, deliberately too small for evidence):

```json
{
  "cases": [{
    "cutoff_at": "2026-10-25T20:00:00+02:00",
    "prediction_recorded_at": "2026-10-25T19:00:00+02:00",
    "horizon_days": 3,
    "predicted_date": "2026-10-27",
    "complete_cash_record": true,
    "daily_cash": [
      {"day": "2026-10-26", "closing_cash_cents": 100},
      {"day": "2026-10-27", "closing_cash_cents": -1},
      {"day": "2026-10-28", "closing_cash_cents": 200}
    ]
  }]
}
```

From `backend/`, using the configured virtual environment:

```bash
python -m app.timing_validation ../output/validation/private-cases.json --tolerance-days 0
```

On Windows Git Bash use `./.venv/Scripts/python.exe` if `python` is unavailable.
No credentials are requested. The file limit is 2 MB. An invalid dataset fails
as a whole; exclusions must be documented before evaluation, not chosen to
improve results. The default exact-date tolerance is zero days; choose any
alternative before looking at results and report it with all metrics.

## Required study design before a dated warning ships

1. Agree what a shortfall means: missed essential payment, cash below a chosen
   buffer, or negative closing cash. Add an evaluator for the chosen outcome if
   negative cash is inappropriate; do not silently change the label.
2. Obtain consent and define data access, retention and deletion. Collect cash
   on hand at the cutoff, confirmed future payout amounts/dates and their
   uncertainty, dated obligations, actual arrivals/spending and reporting gaps.
   Manual cash/eWallet tracking must distinguish absent entries from no activity.
3. Freeze candidate inputs and predictions at each cutoff before observing the
   future. Timestamp fields alone cannot prove this: retain a private immutable
   prediction record and audit feature availability. No future rows, corrected
   records learned later, or whole-history preprocessing may enter training.
4. Evaluate forward in time on held-out people and periods. Prevent overlapping
   horizons/person reuse from inflating sample size; report participant count,
   event prevalence, exclusions, missingness and outcomes by relevant cohort.
   This tool scores cases, not independent participants; confidence intervals
   and participant-level analyses require a separate study analysis.
5. Set false-alarm, missed-event, date-tolerance, warning-lead-time and abstention
   criteria with users before evaluation. Compare to simple baselines using the
   same information and assess uncertainty. A point estimate or a passing unit
   test is not a release threshold.
6. Review false reassurance and unnecessary saving pressure with participants.
   If probabilities or “likely” wording are proposed, separately evaluate
   calibration, understandable explanations and failure behavior. Test language
   and accessibility before releasing any new warning.

## Remaining team decisions

The outcome definition, consent/data-retention plan, candidate timing model,
minimum independent sample, release thresholds and user-facing wording remain
unapproved. No suitable real evaluation dataset has been supplied. #19 stays
open for these decisions and prospective evidence. The evaluator and its
synthetic tests do not unlock dated warnings or alter the production forecast.
