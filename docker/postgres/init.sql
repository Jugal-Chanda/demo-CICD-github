-- PostgreSQL initialization script for demo Flask application
-- This script runs when the PostgreSQL container is first created

-- Create the demo_app database (if not already created by POSTGRES_DB env var)
-- Note: The database is already created by the POSTGRES_DB environment variable in docker-compose.yml

-- Switch to the demo_app database
\c demo_app;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    age INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Create index on created_at for sorting
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at DESC);

-- Insert sample data
INSERT INTO users (name, email, age) VALUES
    ('John Doe', 'john.doe@example.com', 30),
    ('Jane Smith', 'jane.smith@example.com', 25),
    ('Bob Johnson', 'bob.johnson@example.com', 35),
    ('Alice Brown', 'alice.brown@example.com', 28),
    ('Charlie Wilson', 'charlie.wilson@example.com', 42)
ON CONFLICT (email) DO NOTHING;

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (if needed)
-- GRANT ALL PRIVILEGES ON DATABASE demo_app TO demo_user;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO demo_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO demo_user;

-- Create a view for active users (example)
CREATE OR REPLACE VIEW active_users AS
SELECT id, name, email, age, created_at, updated_at
FROM users
WHERE age IS NOT NULL AND age >= 18;

-- Insert a test record that will be updated to test the trigger
-- This will be updated by the application during testing
INSERT INTO users (name, email, age) VALUES
    ('Test User', 'test@example.com', 25)
ON CONFLICT (email) DO NOTHING;