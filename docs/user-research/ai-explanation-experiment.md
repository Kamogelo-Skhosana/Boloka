# Optional AI explanation experiment

Preparation for issue #79. Do not connect a model to real participant data
until user research shows demand and the team's privacy owner approves a
specific provider, endpoint, retention setting and data flow.

## Product boundary

Boloka's deterministic planning calculation remains the source of every amount,
date, status and assumption. An optional model call may only restate already
computed facts in simpler language or ask a clarifying question. It must not
invent a payday, forecast a precise shortfall date, change a ledger entry,
recommend credit, or tell someone what they can afford.

## Candidate input

Prefer structured aggregates already produced by the forecast: horizon,
history-length flags, known upcoming-cost total, estimate status, the existing
explanation and approved action codes. Do not send account IDs, email, raw
statements, merchant names, free-text notes, credentials or amounts not needed
for the requested explanation. If the user has not explicitly asked for the
explanation, make no model request.

## Candidate output

Use a bounded schema such as:

- `summary`: short plain-language explanation of supplied facts.
- `facts_used`: references to supplied field names only.
- `question`: optional clarification question; no inferred fact.
- `disclaimer`: indicates the text is AI-assisted and not financial advice.

Validate output server-side. If the model fails, times out, or returns
unsupported facts, show Boloka's deterministic explanation instead.

## Go/no-go evaluation

Only proceed after the pilot or discovery work identifies a user need. Compare
the AI explanation with existing static copy for factual fidelity,
comprehension, usefulness, latency, cost, accessibility and harmful or
unsupported statements. Use fictional or explicitly consented, minimized test
data. Record the provider's applicable retention and processing terms and the
team's privacy review. Keep AI optional and record a no-go decision if it adds
confusion or risk without a clear user benefit.
