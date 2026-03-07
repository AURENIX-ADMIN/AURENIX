DO $do$ BEGIN IF NOT EXISTS (
    SELECT
    FROM pg_catalog.pg_roles
    WHERE rolname = 'aurenix'
) THEN CREATE ROLE aurenix LOGIN PASSWORD 'aurenix_password';
END IF;
END $do$;
ALTER ROLE aurenix WITH SUPERUSER;
-- simplifying for dev
-- Database creation cannot be in a transaction block (DO block), 
-- so we rely on psql to ignore error if exists or check first outside.
-- But inside docker exec one-liner, it is hard.
-- We will just assume we can create it or it fails safely.