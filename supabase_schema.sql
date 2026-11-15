-- DivulgaHub 1.1 — Supabase PostgreSQL
-- Execute no SQL Editor do projeto Supabase.
create table if not exists public.campaigns (
  id uuid primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  data jsonb not null,
  updated_at timestamptz not null default now()
);

alter table public.campaigns enable row level security;

drop policy if exists "Users can read their campaigns" on public.campaigns;
create policy "Users can read their campaigns" on public.campaigns
  for select to authenticated using (auth.uid() = user_id);

drop policy if exists "Users can insert their campaigns" on public.campaigns;
create policy "Users can insert their campaigns" on public.campaigns
  for insert to authenticated with check (auth.uid() = user_id);

drop policy if exists "Users can update their campaigns" on public.campaigns;
create policy "Users can update their campaigns" on public.campaigns
  for update to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "Users can delete their campaigns" on public.campaigns;
create policy "Users can delete their campaigns" on public.campaigns
  for delete to authenticated using (auth.uid() = user_id);

create index if not exists campaigns_user_updated_idx
  on public.campaigns (user_id, updated_at desc);
