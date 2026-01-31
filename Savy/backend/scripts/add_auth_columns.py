"""
Script to add missing auth columns to profiles table.
Run this from the backend directory:
    python -m scripts.add_auth_columns
"""
import pymysql
from config import settings

def add_column_if_not_exists(cursor, table, column, definition):
    """Add column if it doesn't exist."""
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        print(f"  [OK] Added column: {column}")
    except pymysql.err.OperationalError as e:
        if e.args[0] == 1060:  # Duplicate column name
            print(f"  [SKIP] Column already exists: {column}")
        else:
            raise

def main():
    print("=" * 60)
    print("SAVY Database Migration - Auth Enhancement Columns")
    print("=" * 60)
    
    # Connect to database
    connection = pymysql.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        database=settings.mysql_database,
        charset='utf8mb4'
    )
    
    try:
        with connection.cursor() as cursor:
            print("\n[1/2] Adding columns to 'profiles' table...")
            
            # Refresh token columns
            add_column_if_not_exists(cursor, 'profiles', 'refresh_token', 'VARCHAR(500) NULL')
            add_column_if_not_exists(cursor, 'profiles', 'refresh_token_expires', 'DATETIME NULL')
            
            # Email verification columns
            add_column_if_not_exists(cursor, 'profiles', 'email_verified', 'BOOLEAN DEFAULT FALSE NOT NULL')
            add_column_if_not_exists(cursor, 'profiles', 'email_verification_token', 'VARCHAR(100) NULL')
            add_column_if_not_exists(cursor, 'profiles', 'email_verification_expires', 'DATETIME NULL')
            
            # Password reset columns
            add_column_if_not_exists(cursor, 'profiles', 'password_reset_token', 'VARCHAR(100) NULL')
            add_column_if_not_exists(cursor, 'profiles', 'password_reset_expires', 'DATETIME NULL')
            
            # FCM token
            add_column_if_not_exists(cursor, 'profiles', 'fcm_token', 'VARCHAR(255) NULL')
            
            connection.commit()
            
            print("\n[2/2] Creating 'refresh_tokens' table if not exists...")
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS refresh_tokens (
                    id CHAR(36) PRIMARY KEY,
                    token VARCHAR(500) NOT NULL,
                    user_id CHAR(36) NOT NULL,
                    expires_at DATETIME NOT NULL,
                    is_revoked BOOLEAN DEFAULT FALSE NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    revoked_at DATETIME NULL,
                    INDEX idx_refresh_tokens_token (token),
                    INDEX idx_refresh_tokens_user_id (user_id),
                    FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            print("  [OK] refresh_tokens table ready")
            
            connection.commit()
            
            # Verify
            print("\n[VERIFY] Current columns in 'profiles':")
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'profiles' 
                AND TABLE_SCHEMA = %s
                ORDER BY ORDINAL_POSITION
            """, (settings.mysql_database,))
            
            columns = [row[0] for row in cursor.fetchall()]
            for col in columns:
                print(f"  - {col}")
            
            print("\n" + "=" * 60)
            print("Migration completed successfully!")
            print("=" * 60)
            
    finally:
        connection.close()

if __name__ == "__main__":
    main()
