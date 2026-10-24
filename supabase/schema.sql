-- Boloka database schema (Supabase / PostgreSQL)
-- Run this in the Supabase SQL editor. It creates the tables, Row-Level Security
-- policies, indexes, and the trigger that mirrors new auth users into profiles.
-- Money is stored as integer cents in ZAR (amount_cents). R150.00 is 15000.

-- ---------------------------------------------------------------------------
-- profiles: one row per authenticated user, mirrored from auth.users
-- ---------------------------------------------------------------------------
create table if not exists public.profiles (
  id          uuid primary key references auth.users (id) on delete cascade,
  email       text,
  created_at  timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- income_events: each payment the user receives (irregular by nature)
-- ---------------------------------------------------------------------------
create table if not exists public.income_events (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid not null references auth.users (id) on delete cascade,
  amount_cents integer not null check (amount_cents > 0),
  source       text,
  received_on  date not null,
  note         text,
  created_at   timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- expenses: outflows, recurring or once-off
-- ---------------------------------------------------------------------------
create table if not exists public.expenses (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid not null references auth.users (id) on delete cascade,
  amount_cents integer not null check (amount_cents > 0),
  category     text,
  spent_on     date not null,
  recurring    boolean not null default false,
  note         text,
  created_at   timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- savings_contributions: user-confirmed amounts actually put aside
-- ---------------------------------------------------------------------------
create table if not exists public.savings_contributions (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid not null references auth.users (id) on delete cascade,
  amount_cents integer not null check (amount_cents > 0),
  saved_on     date not null,
  note         text,
  created_at   timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- forecasts: cached output of the forecasting engine (payload is the API body)
-- ---------------------------------------------------------------------------
create table if not exists public.forecasts (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid not null references auth.users (id) on delete cascade,
  generated_at timestamptz not null default now(),
  horizon_days integer not null default 30,
  payload      jsonb not null,
  created_at   timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- Indexes for the common lookups (by user, ordered by date)
-- ---------------------------------------------------------------------------
create index if not exists income_user_date_idx   on public.income_events (user_id, received_on desc);
create index if not exists expense_user_date_idx   on public.expenses      (user_id, spent_on desc);
create index if not exists savings_user_date_idx    on public.savings_contributions (user_id, saved_on desc);
create index if not exists forecast_user_gen_idx   on public.forecasts     (user_id, generated_at desc);

-- ---------------------------------------------------------------------------
-- Row-Level Security: a user can only ever see and change their own rows
-- ---------------------------------------------------------------------------
alter table public.profiles      enable row level security;
alter table public.income_events enable row level security;
alter table public.expenses      enable row level security;
alter table public.savings_contributions enable row level security;
alter table public.forecasts     enable row level security;

-- profiles: the row is the user themselves
drop policy if exists "profiles are self" on public.profiles;
create policy "profiles are self" on public.profiles
  for all to authenticated using (id = (select auth.uid())) with check (id = (select auth.uid()));

-- income_events
drop policy if exists "own income" on public.income_events;
create policy "own income" on public.income_events
  for all to authenticated using (user_id = (select auth.uid())) with check (user_id = (select auth.uid()));

-- expenses
drop policy if exists "own expenses" on public.expenses;
create policy "own expenses" on public.expenses
  for all to authenticated using (user_id = (select auth.uid())) with check (user_id = (select auth.uid()));

drop policy if exists "own savings contributions" on public.savings_contributions;
create policy "own savings contributions" on public.savings_contributions
  for all to authenticated using (user_id = (select auth.uid())) with check (user_id = (select auth.uid()));

-- forecasts
drop policy if exists "own forecasts" on public.forecasts;
create policy "own forecasts" on public.forecasts
  for all to authenticated using (user_id = (select auth.uid())) with check (user_id = (select auth.uid()));

-- ---------------------------------------------------------------------------
-- Mirror new auth users into profiles automatically
-- ---------------------------------------------------------------------------
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  insert into public.profiles (id, email)
  values (new.id, new.email)
  on conflict (id) do nothing;
  return new;
end;
$$;

revoke all on function public.handle_new_user() from public, anon, authenticated;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();
