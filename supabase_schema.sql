-- Run this ONCE in your Supabase project:
--   Dashboard -> SQL Editor -> New query -> paste this -> Run.
-- Safe to re-run: every statement is idempotent.

create table if not exists public.quotations (
  id             uuid primary key default gen_random_uuid(),
  serial         text not null,
  created_at     timestamptz not null default now(),
  quote_date     date not null,             -- set by the client in local time
  customer_name  text,
  customer_attn  text,
  items          jsonb not null,            -- [{sku, name, qty, unit_usd, unit_myr, total_myr}, ...]
  item_count     int  not null,             -- sum of qty across items (units, not lines)
  delivery_desc  text,
  delivery_price numeric,
  grand_total    numeric not null
);

create index if not exists quotations_date_idx
  on public.quotations (quote_date desc);

-- Row-level security: anonymous browser users can read history and add new
-- quotations, but cannot edit or delete existing rows. This means someone
-- with the site URL can pad the log, but cannot vandalise past records.
alter table public.quotations enable row level security;

drop policy if exists "public read"   on public.quotations;
drop policy if exists "public insert" on public.quotations;

create policy "public read"
  on public.quotations
  for select
  to anon, authenticated
  using (true);

create policy "public insert"
  on public.quotations
  for insert
  to anon, authenticated
  with check (true);
