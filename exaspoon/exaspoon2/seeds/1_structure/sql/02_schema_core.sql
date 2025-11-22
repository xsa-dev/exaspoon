create table if not exists categories (
  id           uuid primary key default gen_random_uuid(),
  name         text not null unique,
  kind         text check (kind in ('income','expense','transfer')) default 'expense',
  description  text,
  embedding    vector(1536)
);

create index if not exists categories_embedding_idx
  on categories using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

create table if not exists accounts (
  id           uuid primary key default gen_random_uuid(),
  name         text not null,
  type         text not null check (type in ('onchain','offchain')),
  currency     text not null,
  network      text,
  institution  text,
  metadata     jsonb default '{}'::jsonb
);

create index if not exists accounts_type_idx on accounts(type);

create table if not exists transactions (
  id              uuid primary key default gen_random_uuid(),
  account_id      uuid not null references accounts(id) on delete cascade,
  amount          numeric not null,
  currency        text not null,
  direction       text not null check (direction in ('income','expense','transfer')),
  occurred_at     timestamptz not null,
  description     text,
  category_id     uuid references categories(id),
  raw_source      text,
  metadata        jsonb default '{}'::jsonb,
  embedding       vector(1536)
);

create index if not exists transactions_account_idx
  on transactions(account_id, occurred_at);

create index if not exists transactions_embedding_idx
  on transactions using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

create table if not exists plans (
  id           uuid primary key default gen_random_uuid(),
  period_start date not null,
  period_end   date not null,
  category_id  uuid references categories(id),
  account_id   uuid references accounts(id),
  amount       numeric not null,
  currency     text not null
);

create table if not exists facts (
  id           uuid primary key default gen_random_uuid(),
  period_start date not null,
  period_end   date not null,
  category_id  uuid references categories(id),
  account_id   uuid references accounts(id),
  amount       numeric not null,
  currency     text not null
);
