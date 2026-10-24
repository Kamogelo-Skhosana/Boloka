# Synthetic demo dataset (ticket #14)

These values are fictional examples of gig earnings and costs. They are not
observed user data, evidence of forecast accuracy, or predictions of dry spells.
Use a dedicated demo account and state this clearly when presenting it.

Create the account through Supabase Auth, apply `schema.sql`, then run the
following in the SQL editor in the **same execution** as the contents of
`seed.sql`. Replace the email with the dedicated account's actual email:

```sql
set boloka.demo_email = 'YOUR-DEDICATED-DEMO-EMAIL';
set boloka.confirm_demo_seed = 'yes';
-- Paste seed.sql below these settings and execute together.
```

The seed refuses missing confirmation, missing email, or an unknown/ambiguous
account. Its changes are atomic. It never creates an Auth user or stores a
password. Keep judge credentials in the private submission, outside Git.

The seed replaces only rows belonging to this account whose note exactly equals
`Boloka synthetic demo v1`. Every seeded row carries that marker, visible in
transaction details. Other entries and other accounts are preserved. Editing a
seeded row's note removes its marker, so it survives later runs. Rows created by
the old unmarked seed also survive: use a fresh demo account to avoid duplicates.
Rerunning at a later date moves the marked dataset forward; this is not a full
account reset. Do not use this script for an account with real financial data.

Dates use the Africa/Johannesburg calendar. Twelve income events cover eight
completed Monday-to-Sunday weeks (two with no recorded earnings) and a current
partial week. Eleven expenses include historic spending and explicit future
costs at days 7, 15, 30 and 37. The next-30-day scheduled total is R1,479; day 37
is excluded. Two savings contributions total R150, which is not an available
bank balance. Historic recurring flags do not generate additional due dates.
Forecast results remain conditional on recorded history and optional cash input.

CI runs `tests/seed.sql` against disposable PostgreSQL after applying the schema.
It checks repeatability, earning gaps, cost boundaries and preservation of other
data. Never apply `tests/bootstrap.sql` to hosted Supabase. Hosted sign-in and
two-account isolation still require a separate release check.
