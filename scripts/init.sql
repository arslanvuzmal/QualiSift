-- PostgreSQL initialization run once on first container start.
-- Enables the pgvector extension so embedding/vector columns are available
-- (used for semantic lead similarity), plus trigram search for fuzzy lookups.
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
