-- DivulgaCerto 2.2 — migração de métricas verificáveis
-- Execute no SQL Editor do projeto Supabase antes de ativar o rastreamento.
create table if not exists public.divulgacerto_tracking_links (
  token text primary key,
  campaign_id text not null,
  user_id uuid not null references auth.users(id) on delete cascade,
  destination text not null,
  created_at timestamptz not null default now()
);
create index if not exists divulgacerto_tracking_links_owner_campaign_idx
  on public.divulgacerto_tracking_links(user_id, campaign_id);

create table if not exists public.divulgacerto_click_events (
  id bigint generated always as identity primary key,
  token text not null references public.divulgacerto_tracking_links(token) on delete cascade,
  campaign_id text not null,
  user_id uuid not null references auth.users(id) on delete cascade,
  created_at timestamptz not null default now()
);
create index if not exists divulgacerto_click_events_campaign_idx
  on public.divulgacerto_click_events(user_id, campaign_id, created_at desc);

create table if not exists public.divulgacerto_conversion_events (
  id bigint generated always as identity primary key,
  campaign_id text not null,
  order_id text not null unique,
  amount numeric(12,2),
  currency text not null default 'BRL',
  source text not null default 'webhook',
  created_at timestamptz not null default now()
);
create index if not exists divulgacerto_conversion_events_campaign_idx
  on public.divulgacerto_conversion_events(campaign_id, created_at desc);

alter table public.divulgacerto_tracking_links enable row level security;
alter table public.divulgacerto_click_events enable row level security;
alter table public.divulgacerto_conversion_events enable row level security;

drop policy if exists "Owners read tracking links" on public.divulgacerto_tracking_links;
create policy "Owners read tracking links" on public.divulgacerto_tracking_links
  for select to authenticated using (auth.uid() = user_id);
drop policy if exists "Owners read click events" on public.divulgacerto_click_events;
create policy "Owners read click events" on public.divulgacerto_click_events
  for select to authenticated using (auth.uid() = user_id);
-- Escrita feita exclusivamente pela API com SUPABASE_SERVICE_ROLE_KEY.
-- Não conceder INSERT/UPDATE/DELETE ao papel anon ou authenticated.
-- Conversões também são gravadas exclusivamente pela API/webhook.
