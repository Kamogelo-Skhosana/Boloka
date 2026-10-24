-- Boloka seed data: a realistic irregular-income history for the demo user.
-- Run this AFTER schema.sql and AFTER creating the demo account in Supabase Auth.
-- It looks up the user by email, so set DEMO_EMAIL below to the demo account's email.
-- Money is integer cents in ZAR. Dates are relative to the day you run this.

do $$
declare
  uid uuid;
  demo_email text := 'demo@boloka.app';   -- change to your demo account email
begin
  select id into uid from auth.users where email = demo_email limit 1;

  if uid is null then
    raise notice 'No auth user found for %, create the demo account first, then re-run.', demo_email;
    return;
  end if;

  -- Clear any previous seed rows for this user so the script is repeatable
  delete from public.income_events where user_id = uid;
  delete from public.expenses      where user_id = uid;

  -- Irregular income over the last ~9 weeks: varying amounts, some gaps,
  -- and a thinning-out toward the most recent weeks so a shortfall is predictable.
  insert into public.income_events (user_id, amount_cents, source, received_on) values
    (uid, 38000, 'Microworkers',      current_date - 60),
    (uid, 12000, 'Small gig',         current_date - 57),
    (uid, 45000, 'Freelance client',  current_date - 52),
    (uid,  9000, 'Microworkers',      current_date - 45),
    (uid, 15000, 'Delivery',          current_date - 44),
    (uid, 52000, 'Freelance client',  current_date - 38),
    (uid,  8000, 'Microworkers',      current_date - 33),
    (uid, 20000, 'Delivery',          current_date - 26),
    (uid, 11000, 'Small gig',         current_date - 20),
    (uid, 30000, 'Freelance client',  current_date - 14),
    (uid,  7000, 'Microworkers',      current_date -  9),
    (uid, 16000, 'Delivery',          current_date -  3);

  -- Expenses: recurring monthly costs plus smaller frequent outflows.
  insert into public.expenses (user_id, amount_cents, category, spent_on, recurring) values
    (uid, 120000, 'rent',      (date_trunc('month', current_date) - interval '1 month')::date, true),
    (uid, 120000, 'rent',      date_trunc('month', current_date)::date,                        true),
    (uid,   9900, 'data',      current_date - 50, true),
    (uid,   9900, 'data',      current_date - 20, true),
    (uid,   6000, 'transport', current_date - 44, false),
    (uid,   6000, 'transport', current_date - 30, false),
    (uid,   6000, 'transport', current_date - 12, false),
    (uid,  35000, 'groceries', current_date - 48, false),
    (uid,  35000, 'groceries', current_date - 18, false),
    (uid,   4500, 'airtime',   current_date -  6, false);

  raise notice 'Seeded 12 income events and 10 expenses for %.', demo_email;
end $$;
