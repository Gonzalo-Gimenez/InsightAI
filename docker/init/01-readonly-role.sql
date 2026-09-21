DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'insight_ai_ro') THEN
    CREATE ROLE insight_ai_ro LOGIN PASSWORD 'insight_ai_ro_demo';
  END IF;
END
$$;

GRANT CONNECT ON DATABASE insight_ai TO insight_ai_ro;
GRANT USAGE ON SCHEMA public TO insight_ai_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO insight_ai_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO insight_ai_ro;
