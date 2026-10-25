# Product acceptance sessions (#76 and #77)

Use this worksheet for short, moderated checks of the income-import and home
flows. It prepares the sessions; it is not evidence that a session or
accessibility review has happened. Do not recruit or collect real financial
records until the team has approved the research and privacy process in
[`pilot-plan.md`](pilot-plan.md). Use fictional data for these checks.

## Before the session

- Ask the team to approve the purpose, note-taking, access and retention plan.
- Explain the session and ask permission for notes. Recording is optional and
  requires separate permission.
- Let the participant skip a task or stop at any time.
- Use a dedicated test account with synthetic records, or the labelled sample
  preview. Never use judge credentials or a participant's real finances.
- Ask which device, language, text size and assistive technology the
  participant prefers. Do not infer proficiency from their identity.
- Capture app version/commit, device model, Android version or browser, and
  language. Do not capture account identifiers, amounts, CSV contents, notes,
  screenshots containing private data, or accessibility-tree dumps.

## #76: add or review an income CSV

Give the participant a prepared CSV containing fictional rows, including one
valid row and one row with a correctable problem. Do not explain the interface
before the task.

1. Ask: “Please add these payouts. Stop before saving if you are unsure.”
2. Observe whether they find the review, identify the source line, correct a
   row, exclude a row, inspect another page if present, and understand which
   records will be saved.
3. Ask them to cancel. Confirm in the test account that nothing was written.
4. Start again, confirm only the intended valid rows, then verify the result
   once in the test account. Do not retry a write if its result is uncertain;
   first refresh and check for the marker row.
5. Ask: “What do you think was saved? What would you do if the result looked
   wrong?”

Record task completion without help, errors, recovery, whether the participant
understood preview versus save, and any wording that caused hesitation. For
accessibility, repeat with keyboard-only navigation and the participant's
chosen screen reader on a small Android screen. Check focus order, announced
row status/errors, selection state, page changes, confirmation and cancellation.

The automated import browser check covers focus on the review heading after
preview, Tab into the first row, focus returning to the file picker after
cancel, focus on the first row after pagination, and focus on a failed-save
alert. Focus waits until pending work releases disabled controls. These checks
use mock data and do not establish what a real screen reader announces; record
the device and assistive-technology session separately.

## #77: understand the home screen and next action

Use a synthetic account with explicitly dated upcoming costs. Avoid constructing
a result that implies a certain payday or shortfall date.

1. Ask: “Looking at this screen, what would you do next, if anything?”
2. Ask: “Which costs are included, and over what dates?”
3. Ask: “Does the recorded amount mean this is the cash in your bank account?
   Why or why not?”
4. Ask: “What would change this estimate? What does it not tell you?”
5. Ask the participant to use the primary action and then return home.

Record their interpretation before offering explanations. Note whether they
distinguish recorded net from available cash, recognize the date window, treat
the gap as conditional, and understand the next action. Mark a misconception
only when they state it or act on it; do not infer comprehension from a
positive reaction.

For accessibility, repeat at 360 CSS pixels and 200% text zoom, with high
contrast enabled, keyboard-only navigation, and the participant's chosen screen
reader. Check that the primary action is reachable, its label describes its
destination, dates and amounts are announced meaningfully, and focus/status
changes are clear. Record device/browser/assistive-technology versions and any
barrier; a screenshot alone does not establish screen-reader acceptance.

## Session record

Keep one anonymized record per session. Store it only in the team-approved
location and retention period.

```text
Alias:
Date:
Broad participant segment (no identifying details):
Task: #76 import / #77 home / both
App commit/version:
Device/browser and assistive technology (if used):
Language selected:
Notes permission: yes / no
Recording permission: yes / no (do not record without separate yes)
Completed without help: yes / partly / no
Observed friction or misunderstanding (no financial values or row contents):
Participant's suggested wording or change:
Researcher interpretation and alternative explanation:
Follow-up action:
```

## Report and acceptance

Summarize the number of participants, recruitment approach, dates, task results,
observed barriers, changes made and limitations. Separate observed behavior
from participant opinion. Share only anonymized notes with the approved team.
Do not claim usability, accessibility, language approval, market validation or
forecast accuracy beyond what was actually reviewed. For fluent-language
approval, use the separate key-by-key process in
[`../localization-review.md`](../localization-review.md).
