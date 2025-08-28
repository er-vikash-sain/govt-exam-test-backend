-- Initialize exam_prep database
-- This file is run when the PostgreSQL container starts for the first time

-- Create extensions if they don't exist
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create database if it doesn't exist (this is usually handled by POSTGRES_DB env var)
-- SELECT 'CREATE DATABASE exam_prep'
-- WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'exam_prep')\gexec

-- Connect to the database
\c exam_prep;

-- Grant privileges to the user
GRANT ALL PRIVILEGES ON DATABASE exam_prep TO exam_user;
GRANT ALL ON SCHEMA public TO exam_user;

-- Create some basic indexes for performance (tables will be created by SQLAlchemy)
-- These will be created after tables are created by the application

-- Log initialization completion
SELECT 'Database initialization completed successfully' as status;
