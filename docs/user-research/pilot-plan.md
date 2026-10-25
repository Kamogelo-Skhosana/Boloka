# Boloka consent-based pilot plan

Preparation for issue #78. This is a draft plan only; it is not legal advice,
approved participant consent, or evidence that a pilot has run.

## Gate before recruitment

The team must name the data owner and approve the following before collecting
real financial records:

- Clear pilot purpose, participant group, data fields and access list.
- The lawful basis and participant-facing privacy notice, reviewed by the
  team's privacy owner.
- Retention and deletion dates, including exports, logs and backups.
- Support contact, incident escalation, withdrawal and account-deletion path.
- A separate staging project and test accounts; no production judge account
  should be shared with pilot participants.
- Consent flow that is voluntary, understandable, recorded, and separate from
  consent to interviews or recordings.

If any gate is missing, test the interface with clearly fictional data and do
not collect real transaction records.

## Pilot questions

1. Can participants add the records they need without help?
2. Do they understand the difference between recorded net, available cash and
   a conditional planning gap?
3. Can they tell which assumptions or missing information affect the estimate?
4. Does the suggested next step feel possible and relevant to their situation?
5. What causes them to return or stop using the app?

## Measures

Capture the minimum aggregate observations needed to answer the questions:

- Onboarding completion and time to first useful action.
- Whether a participant can add or correct an income entry and an upcoming
  cost, and whether import review is understandable.
- Weekly return and record-entry frequency, reported in aggregate.
- Comprehension of forecast limits and action relevance from short interviews.
- Accessibility and low-data task failures.
- Participant-reported usefulness and reasons for stopping.

Do not log amounts, merchant descriptions, notes, authentication data or raw
bank statements in analytics. Keep individual financial records inside the
participant's account and out of research notes. A small pilot is formative;
do not make forecast-accuracy or population-impact claims from it.

## Suggested sequence

1. Run discovery interviews using [the segment guide](segment-discovery.md).
2. Review the flow with a few participants using fictional data.
3. Fix comprehension, accessibility and input-friction findings.
4. Obtain privacy-owner approval and prepare the deletion/support process.
5. Invite a small, voluntary cohort through an agreed community contact for a
   time-limited pilot.
6. Review aggregate measures and anonymized feedback with the team.
7. Publish methods, participant count, dates, limitations and next decision;
   delete pilot data according to the approved retention plan.

## Participant-facing consent topics

Before a consent form is drafted, the team should explain in plain language:
the pilot's purpose and duration; what account and usage information Boloka
stores; who can access it; which service providers process it; whether any AI
feature is used (off by default); how participants can withdraw or request
deletion; how to contact the team; and how to report a concern. The privacy
owner must approve the actual notice and consent process before use.
