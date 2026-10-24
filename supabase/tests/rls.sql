-- Run after bootstrap.sql + schema.sql in a disposable database.
-- These are real PostgreSQL RLS checks, not API mocks. All fixture writes roll back.
begin;
insert into auth.users (id, email) values
  ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'a@example.invalid'),
  ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'b@example.invalid');

insert into public.income_events (user_id, amount_cents, received_on)
  select id, 500, current_date from auth.users;
insert into public.expenses (user_id, amount_cents, spent_on)
  select id, 500, current_date from auth.users;
insert into public.savings_contributions (user_id, amount_cents, saved_on)
  select id, 500, current_date from auth.users;
insert into public.forecasts (user_id, horizon_days, payload)
  select id, 30, '{}'::jsonb from auth.users;

set local role authenticated;
select set_config('request.jwt.claim.sub', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', true);
do $$
declare
  tab text;
  count_rows integer;
  actor uuid := 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa';
  other_user uuid := 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb';
  test_id uuid := 'cccccccc-cccc-cccc-cccc-cccccccccccc';
  data jsonb;
begin
  foreach tab in array array['income_events', 'expenses', 'savings_contributions', 'forecasts'] loop
    execute format('select count(*) from public.%I', tab) into count_rows;
    if count_rows <> 1 then raise exception 'RLS read leaked or hid own row: %', tab; end if;
    execute format('update public.%I set user_id=$1 where user_id=$2', tab) using actor, other_user;
    get diagnostics count_rows = row_count;
    if count_rows <> 0 then raise exception 'RLS allowed foreign update: %', tab; end if;
    execute format('delete from public.%I where user_id=$1', tab) using other_user;
    get diagnostics count_rows = row_count;
    if count_rows <> 0 then raise exception 'RLS allowed foreign delete: %', tab; end if;

    data := jsonb_build_object('id', test_id, 'user_id', other_user,
      'amount_cents', 100, 'received_on', current_date, 'spent_on', current_date,
      'saved_on', current_date, 'recurring', false, 'created_at', now(),
      'generated_at', now(), 'horizon_days', 30, 'payload', '{}'::jsonb);
    begin
      execute format('insert into public.%I select * from jsonb_populate_record(null::public.%I, $1)', tab, tab) using data;
      raise exception 'RLS allowed spoofed insert: %', tab;
    exception when insufficient_privilege then null;
    end;
    data := data || jsonb_build_object('user_id', actor);
    execute format('insert into public.%I select * from jsonb_populate_record(null::public.%I, $1)', tab, tab) using data;
    begin
      execute format('update public.%I set user_id=$1 where id=$2', tab) using other_user, test_id;
      raise exception 'RLS allowed ownership transfer: %', tab;
    exception when insufficient_privilege then null;
    end;
    execute format('delete from public.%I where id=$1', tab) using test_id;
    get diagnostics count_rows = row_count;
    if count_rows <> 1 then raise exception 'RLS prevented own delete: %', tab; end if;
  end loop;
  select count(*) into count_rows from public.profiles;
  if count_rows <> 1 then raise exception 'Profile isolation failed'; end if;
  update public.profiles set email='must-not-change@example.invalid' where id=other_user;
  get diagnostics count_rows = row_count;
  if count_rows <> 0 then raise exception 'Foreign profile update succeeded'; end if;
end $$;

select set_config('request.jwt.claim.sub', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', true);
do $$
declare tab text; count_rows integer;
begin
  foreach tab in array array['income_events', 'expenses', 'savings_contributions', 'forecasts', 'profiles'] loop
    execute format('select count(*) from public.%I', tab) into count_rows;
    if count_rows <> 1 then raise exception 'Second user isolation failed: %', tab; end if;
  end loop;
end $$;

select set_config('request.jwt.claim.sub', '', true);
do $$
begin
  if exists(select 1 from public.income_events) then raise exception 'Missing subject can read rows'; end if;
end $$;
set local role anon;
do $$
begin
  perform * from public.income_events;
  raise exception 'Anonymous role can read private tables';
exception when insufficient_privilege then null;
end $$;
reset role;
rollback;
