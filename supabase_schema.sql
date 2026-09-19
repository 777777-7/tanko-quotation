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
  grand_total    numeric not null,
  doc_type       text not null default 'pdf'   -- 'pdf' or 'docx' (which export produced the row)
);

-- Migration for existing databases (safe no-op if the column already exists):
alter table public.quotations
  add column if not exists doc_type text not null default 'pdf';

create index if not exists quotations_date_idx
  on public.quotations (quote_date desc);

create index if not exists quotations_doc_type_idx
  on public.quotations (doc_type);

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

-- ============================================================================
-- Confirmed purchases: quotations the customer accepted, or walk-in sales
-- recorded manually. Each row has a deadline (typed by the operator) and
-- a completion date that is set when "Mark as done" is clicked.
-- ============================================================================
create table if not exists public.purchases (
  id                uuid primary key default gen_random_uuid(),
  serial            text not null,                 -- e.g. PO-260919-001 (daily reset)
  confirmed_at      timestamptz not null default now(),
  confirm_date      date not null,                 -- local date bucket for calendar
  deadline          date not null,                 -- operator-typed
  completed_at      date,                          -- null = pending, date = done
  customer_name     text not null,
  customer_attn     text,
  customer_contact  text,
  customer_address  text,
  items             jsonb not null,                -- same shape as quotations.items
  item_count        int  not null,
  delivery_desc     text,
  delivery_price    numeric,
  grand_total       numeric not null,
  source            text not null default 'manual',  -- 'quotation' or 'manual'
  quotation_serial  text                            -- traceable ref (not shown in /sales/)
);

create index if not exists purchases_deadline_idx
  on public.purchases (deadline);
create index if not exists purchases_pending_idx
  on public.purchases (deadline)
  where completed_at is null;
create index if not exists purchases_confirm_date_idx
  on public.purchases (confirm_date desc);

alter table public.purchases enable row level security;

drop policy if exists "public read"   on public.purchases;
drop policy if exists "public insert" on public.purchases;
drop policy if exists "public update" on public.purchases;
drop policy if exists "public delete" on public.purchases;

create policy "public read"
  on public.purchases
  for select
  to anon, authenticated
  using (true);

create policy "public insert"
  on public.purchases
  for insert
  to anon, authenticated
  with check (true);

-- UI restricts edits to deadline + completed_at only; database is permissive.
create policy "public update"
  on public.purchases
  for update
  to anon, authenticated
  using (true)
  with check (true);

create policy "public delete"
  on public.purchases
  for delete
  to anon, authenticated
  using (true);
