#!/usr/bin/env python3
"""
Database Migration Script for Demo Flask Application

This script handles database schema migrations and data updates
during the CI/CD deployment process.

Usage:
    python database_migration.py

Environment Variables Required:
    - DB_HOST: Database host
    - DB_PORT: Database port
    - DB_NAME: Database name
    - DB_USER: Database username
    - DB_PASSWORD: Database password
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from datetime import datetime

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import get_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """Handles database migrations for the Flask application"""

    def __init__(self):
        self.config = get_config()
        self.connection = None

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
                database=self.config.DB_NAME,
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD
            )
            self.connection.autocommit = False  # Use transactions
            logger.info("Database connection established for migration")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

    def execute_query(self, query, params=None):
        """Execute a database query"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            return cursor
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    def get_current_schema_version(self):
        """Get current database schema version"""
        try:
            cursor = self.execute_query("""
                SELECT version FROM schema_migrations
                ORDER BY applied_at DESC LIMIT 1
            """)

            result = cursor.fetchone()
            cursor.close()

            if result:
                return result[0]
            else:
                return 0

        except psycopg2.Error:
            # Schema migrations table doesn't exist yet
            return 0

    def record_migration(self, version, description):
        """Record a migration as applied"""
        cursor = self.execute_query("""
            INSERT INTO schema_migrations (version, description, applied_at)
            VALUES (%s, %s, %s)
        """, (version, description, datetime.utcnow()))

        cursor.close()

    def create_migrations_table(self):
        """Create schema_migrations table if it doesn't exist"""
        logger.info("Creating schema_migrations table...")

        cursor = self.execute_query("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id SERIAL PRIMARY KEY,
                version INTEGER NOT NULL UNIQUE,
                description TEXT NOT NULL,
                applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.close()
        logger.info("Schema migrations table created")

    def migration_1_initial_schema(self):
        """Migration 1: Initial database schema"""
        logger.info("Applying migration 1: Initial schema")

        # Users table (already created in init.sql, but ensuring it exists)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                age INTEGER,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes
        self.execute_query("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
        """)

        self.execute_query("""
            CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at DESC)
        """)

        # Create trigger for updated_at
        self.execute_query("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql'
        """)

        self.execute_query("""
            DROP TRIGGER IF EXISTS update_users_updated_at ON users;
            CREATE TRIGGER update_users_updated_at
                BEFORE UPDATE ON users
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column()
        """)

        self.record_migration(1, "Initial database schema with users table")

    def migration_2_add_user_status(self):
        """Migration 2: Add status column to users table"""
        logger.info("Applying migration 2: Add user status")

        self.execute_query("""
            ALTER TABLE users ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active'
        """)

        self.execute_query("""
            UPDATE users SET status = 'active' WHERE status IS NULL
        """)

        self.record_migration(2, "Add status column to users table")

    def migration_3_add_audit_log(self):
        """Migration 3: Add audit logging table"""
        logger.info("Applying migration 3: Add audit log")

        self.execute_query("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id SERIAL PRIMARY KEY,
                table_name VARCHAR(50) NOT NULL,
                record_id INTEGER NOT NULL,
                action VARCHAR(10) NOT NULL,
                old_values JSONB,
                new_values JSONB,
                user_id INTEGER,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.execute_query("""
            CREATE INDEX IF NOT EXISTS idx_audit_log_table_record ON audit_log(table_name, record_id)
        """)

        self.record_migration(3, "Add audit logging table")

    def run_migrations(self):
        """Run all pending migrations"""
        try:
            self.connect()
            self.create_migrations_table()

            current_version = self.get_current_schema_version()
            logger.info(f"Current schema version: {current_version}")

            # Define migrations in order
            migrations = [
                (1, "Initial database schema", self.migration_1_initial_schema),
                (2, "Add user status column", self.migration_2_add_user_status),
                (3, "Add audit logging", self.migration_3_add_audit_log),
            ]

            # Apply pending migrations
            for version, description, migration_func in migrations:
                if version > current_version:
                    logger.info(f"Applying migration {version}: {description}")
                    migration_func()
                    self.connection.commit()
                    logger.info(f"Migration {version} applied successfully")

            final_version = self.get_current_schema_version()
            logger.info(f"Migration complete. Final schema version: {final_version}")

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            if self.connection:
                self.connection.rollback()
            raise
        finally:
            self.disconnect()

    def run_data_migrations(self):
        """Run data migrations (not schema changes)"""
        logger.info("Running data migrations...")

        try:
            self.connect()

            # Example data migration: Update user ages for test users
            cursor = self.execute_query("""
                UPDATE users
                SET age = age + 1, updated_at = CURRENT_TIMESTAMP
                WHERE email LIKE 'test%@example.com'
                AND age IS NOT NULL
            """)

            updated_count = cursor.rowcount
            cursor.close()

            if updated_count > 0:
                self.connection.commit()
                logger.info(f"Updated {updated_count} test user records")
            else:
                logger.info("No test user records to update")

        except Exception as e:
            logger.error(f"Data migration failed: {e}")
            if self.connection:
                self.connection.rollback()
            raise
        finally:
            self.disconnect()

def main():
    """Main migration function"""
    logger.info("Starting database migration...")

    migrator = DatabaseMigrator()

    try:
        # Run schema migrations
        migrator.run_migrations()

        # Run data migrations
        migrator.run_data_migrations()

        logger.info("✅ All migrations completed successfully")

    except Exception as e:
        logger.error(f"❌ Migration process failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()