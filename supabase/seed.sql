-- Fictional Boloka demo data, not evidence of forecast accuracy.
-- Run schema.sql first. Use a dedicated Auth account with no real finances.
-- In the SAME SQL editor execution/session, set these before this script:
--   set boloka.demo_email = 'YOUR-DEDICATED-DEMO-EMAIL';
--   set boloka.confirm_demo_seed = 'yes';
-- Only rows with the exact synthetic marker are replaced. Other rows survive.
-- No account is created, no password is stored, and no balance is invented.

do $$
declare
  uid uuid;
  demo_email text := nullif(trim(current_setting('boloka.demo_email', true)), '');
  marker constant text := 'Boloka synthetic demo v1';
  anchor date := (now() at time zone 'Africa/Johannesburg')::date;
  monday date;
begin
  if demo_email is null or current_setting('boloka.confirm_demo_seed', true) is distinct from 'yes' then
    raise exception 'Set boloka.demo_email and boloka.confirm_demo_seed=yes for a dedicated synthetic account';
  end if;
  select id into strict uid from auth.users where lower(email) = lower(demo_email);
  -- The earliest event starts eight completed Monday-to-Sunday weeks.
  monday := date_trunc('week', anchor::timestamp)::date;

  delete from public.income_events where user_id = uid and note = marker;
  delete from public.expenses where user_id = uid and note = marker;
  delete from public.savings_contributions where user_id = uid and note = marker;

  -- Earnings vary; weeks -6 and -3 have no recorded earnings. These are
  -- fictional gaps, not predicted dry spells. The current week is partial.
  insert into public.income_events (user_id, amount_cents, source, received_on, note)
  select uid, amount, source, monday + offset_days, marker from (values
    (38000, 'Microworkers', -56),
    (12000, 'Small gig', -53),
    (45000, 'Freelance client', -47),
    (9000, 'Microworkers', -35),
    (15000, 'Delivery', -33),
    (52000, 'Freelance client', -27),
    (8000, 'Microworkers', -25),
    (20000, 'Delivery', -14),
    (11000, 'Small gig', -11),
    (30000, 'Freelance client', -7),
    (7000, 'Microworkers', -4),
    (16000, 'Delivery', 0)
  ) as sample(amount, source, offset_days);

  -- Historic recurring flags do not create future bills. Explicit dated costs
  -- below illustrate the next-30-day planning window, including its boundary.
  insert into public.expenses (user_id, amount_cents, category, spent_on, recurring, note)
  select uid, amount, category, anchor + offset_days, recurring, marker from (values
    (120000, 'rent', -35, true),
    (120000, 'rent', -5, true),
    (9900, 'data', -20, true),
    (6000, 'transport', -28, false),
    (6000, 'transport', -12, false),
    (35000, 'groceries', -18, false),
    (4500, 'airtime', -6, false),
    (120000, 'rent', 7, true),
    (9900, 'data', 15, true),
    (18000, 'electricity', 30, true),
    (120000, 'rent', 37, true)
  ) as sample(amount, category, offset_days, recurring);

  insert into public.savings_contributions (user_id, amount_cents, saved_on, note) values
    (uid, 10000, anchor - 12, marker),
    (uid, 5000, anchor - 4, marker);

  raise notice 'Seeded fictional data: 12 income, 11 expenses, 2 savings rows. Unmarked rows preserved.';
end $$;
