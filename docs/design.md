# Boloka Design Direction

## Brand

- Name: Boloka (Sesotho and Setswana, "to save, to keep safe").
- Tagline: "Save, before you have to."
- Voice: direct, warm, street-smart, local. Speaks to the hustler, not the accountant.

## Visual direction

Dark-first and confident, so money numbers and alerts stand out. Carried over from the pitch:

- Ground: deep green-black.
- Surface: a slightly raised dark card.
- Primary / accent: teal-green (growth and saving), around #32D6A6.
- Money highlight and shortfall warning: warm amber, around #F6C14B.
- Text: near-white on dark, with a muted grey for secondary text.
- Type: a bold grotesque display face for headings, a clean sans for body.

Keep one bold element per screen (usually the forecast or the alert), everything else quiet.

## Principles

- Mobile-first, designed for 360 to 414px wide and cheap Android phones.
- Low-data: small payloads, cache aggressively, tolerate flaky connections.
- One primary action per screen.
- Always show real states: loading, empty, and error, never a blank screen.
- Accessible contrast, large tap targets, tabular numerals for money so columns line up.
- Target WCAG 2.2 AA: visible keyboard focus, skip navigation, labelled controls, semantic landmarks, and status announcements for loading and errors.
- Never use colour alone to communicate a shortfall or transaction type; pair colour with text, icons, or symbols.
- Give charts a text alternative, respect reduced-motion settings, and verify layouts at 360px, 414px, and 200% zoom.
- Multilingual: English, isiZulu, Sesotho.

## Screens (MVP)

1. Onboarding: three short cards explaining the idea, then collect the first income entries or a CSV import.
2. Sign up / Log in.
3. Dashboard (home, the hero): balance, this week's income, the forecast chart, the shortfall alert card, and set-aside progress.
4. Add income: quick form (amount, source, date).
5. Add expense: quick form (amount, category, date, recurring).
6. Forecast detail: the prediction, the plain-language "why", and the weekly series.
7. Savings / set-aside tracker: progress toward the recommended buffer.
8. Settings: language, profile, data export and delete.

## Signature component

The planning card keeps warm amber for a conditional gap, with a short plain-language heading and visible cash/history assumptions. Do not show a precise shortfall date or likely-risk warning from weekly earnings. Use a neutral information state when inputs are insufficient and label the fictional preview recommendation as unchanged by preview edits.

## Navigation

Bottom tab bar: Home, Add, Forecast, Savings. Settings reached from the home header.
