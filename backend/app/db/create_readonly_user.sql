-- Create read-only database user for query execution
-- This script is idempotent - safe to run multiple times

-- Check if user exists, create if not
-- Note: Password should be passed via READONLY_DB_PASSWORD environment variable
DO
$$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'query_app_readonly') THEN
        EXECUTE format('CREATE USER query_app_readonly WITH PASSWORD %L', current_setting('app.readonly_password'));
        RAISE NOTICE 'User query_app_readonly created';
    ELSE
        RAISE NOTICE 'User query_app_readonly already exists';
    END IF;
END
$$;

-- Grant connect permission to database
GRANT CONNECT ON DATABASE hr_db TO query_app_readonly;

-- Revoke all existing permissions first (clean slate)
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM query_app_readonly;

-- Grant SELECT-only permission on employees table
GRANT SELECT ON employees TO query_app_readonly;

-- Ensure no write permissions
REVOKE INSERT, UPDATE, DELETE, TRUNCATE ON employees FROM query_app_readonly;

-- Log completion
DO
$$
BEGIN
    RAISE NOTICE 'Read-only user configured successfully';
END
$$;
