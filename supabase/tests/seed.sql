-- Disposable database only. Exercise the actual seed twice without committing.
begin;
insert into auth.users (id, email) values
  ('cccccccc-cccc-cccc-cccc-cccccccccccc', 'synthetic-demo@example.invalid'),
  ('dddddddd-dddd-dddd-dddd-dddddddddddd', 'other-demo@example.invalid');
insert into public.income_events (user_id, amount_cents, received_on, note) values
  ('cccccccc-cccc-cccc-cccc-cccccccccccc', 123, current_date, 'Keep this user entry'),
  ('dddddddd-dddd-dddd-dddd-dddddddddddd', 456, current_date, 'Boloka synthetic demo v1');
insert into public.expenses (user_id, amount_cents, spent_on, note) values
  ('cccccccc-cccc-cccc-cccc-cccccccccccc', 123, current_date, 'Keep this user entry');
insert into public.savings_contributions (user_id, amount_cents, saved_on, note) values
  ('cccccccc-cccc-cccc-cccc-cccccccccccc', 123, current_date, 'Keep this user entry');

set local boloka.demo_email = 'synthetic-demo@example.invalid';
set local boloka.confirm_demo_seed = 'yes';
\ir ../seed.sql
\ir ../seed.sql

do $$
declare
  uid constant uuid := 'cccccccc-cccc-cccc-cccc-cccccccccccc';
  anchor date := (now() at time zone 'Africa/Johannesburg')::date;
  monday date;
  weeks integer;
begin
  monday := date_trunc('week', anchor::timestamp)::date;
  if (select count(*) from public.income_events where user_id = uid) <> 13
     or (select count(*) from public.expenses where user_id = uid) <> 12
     or (select count(*) from public.savings_contributions where user_id = uid) <> 3 then
    raise exception 'Repeat seeding duplicated rows or removed unmarked entries';
  end if;
  if not exists (select 1 from public.income_events
      where user_id = 'dddddddd-dddd-dddd-dddd-dddddddddddd' and amount_cents = 456) then
    raise exception 'Seeding changed another account';
  end if;
  select count(distinct date_trunc('week', received_on::timestamp)) into weeks
    from public.income_events where user_id = uid and note = 'Boloka synthetic demo v1'
      and received_on < monday;
  if weeks <> 6 or (select min(received_on) from public.income_events where user_id = uid) <> monday - 56 then
    raise exception 'Expected eight completed weeks with two earning gaps';
  end if;
  if (select sum(amount_cents) from public.expenses where user_id = uid
      and spent_on > anchor and spent_on <= anchor + 30) <> 147900 then
    raise exception 'Upcoming cost totals or horizon boundary changed';
  end if;
  if exists (select 1 from public.income_events where user_id = uid and received_on > anchor) then
    raise exception 'Seed invented a future payout';
  end if;
end $$;
rollback;
