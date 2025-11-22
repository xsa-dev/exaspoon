create or replace function search_similar_transactions(
  query_embedding vector(1536),
  match_count int default 5
)
returns table (
  id uuid,
  account_id uuid,
  amount numeric,
  currency text,
  direction text,
  occurred_at timestamptz,
  description text,
  category_id uuid,
  distance float
)
language sql
as $$
  select
    t.id,
    t.account_id,
    t.amount,
    t.currency,
    t.direction,
    t.occurred_at,
    t.description,
    t.category_id,
    t.embedding <=> query_embedding as distance
  from transactions t
  where t.embedding is not null
  order by t.embedding <=> query_embedding
  limit match_count;
$$;

create or replace function search_similar_categories(
  query_embedding vector(1536),
  match_count int default 5
)
returns table (
  id uuid,
  name text,
  kind text,
  description text,
  distance float
)
language sql
as $$
  select
    c.id,
    c.name,
    c.kind,
    c.description,
    c.embedding <=> query_embedding as distance
  from categories c
  where c.embedding is not null
  order by c.embedding <=> query_embedding
  limit match_count;
$$;
