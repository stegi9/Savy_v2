import os
import sys
import pymysql
from dotenv import load_dotenv

# Add backend directory to path to import config if needed, 
# but for this script we'll just load .env directly for simplicity/robustness
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_PORT = int(os.getenv("MYSQL_PORT", 3306))
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
DB_NAME = os.getenv("MYSQL_DATABASE", "savy_db")

def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

def column_exists(cursor, table, column):
    cursor.execute(
        "SELECT COUNT(*) as count FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s",
        (DB_NAME, table, column)
    )
    return cursor.fetchone()['count'] > 0

def table_exists(cursor, table):
    cursor.execute(
        "SELECT COUNT(*) as count FROM information_schema.TABLES "
        "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s",
        (DB_NAME, table)
    )
    return cursor.fetchone()['count'] > 0

def run_migration():
    print(f"🔌 Connecting to database {DB_NAME} at {DB_HOST}...")
    try:
        conn = get_connection()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    with conn.cursor() as cursor:
        print("✅ Connected!")

        # 1. Update PROFILES (Users)
        print("checking 'profiles' table...")
        if not column_exists(cursor, 'profiles', 'saltedge_customer_id'):
            print("  -> Adding 'saltedge_customer_id' column")
            cursor.execute("ALTER TABLE profiles ADD COLUMN saltedge_customer_id VARCHAR(100) NULL, ADD INDEX idx_saltedge_customer (saltedge_customer_id)")
        else:
            print("  -> 'saltedge_customer_id' exists")

        # 2. Update BANK_CONNECTIONS
        print("Checking 'bank_connections' table...")
        if not column_exists(cursor, 'bank_connections', 'connection_id'):
            print("  -> Adding 'connection_id' column")
            cursor.execute("ALTER TABLE bank_connections ADD COLUMN connection_id VARCHAR(100) NULL, ADD UNIQUE INDEX unique_connection (connection_id)")
        
        if not column_exists(cursor, 'bank_connections', 'provider_code'):
            print("  -> Adding 'provider_code' column")
            cursor.execute("ALTER TABLE bank_connections ADD COLUMN provider_code VARCHAR(50) NULL")

        if not column_exists(cursor, 'bank_connections', 'last_synced_at'):
            print("  -> Adding 'last_synced_at' column")
            cursor.execute("ALTER TABLE bank_connections ADD COLUMN last_synced_at TIMESTAMP NULL")

        # 3. Create BANK_ACCOUNTS
        print("Checking 'bank_accounts' table...")
        if not table_exists(cursor, 'bank_accounts'):
            print("  -> Creating 'bank_accounts' table")
            cursor.execute("""
                CREATE TABLE bank_accounts (
                    id CHAR(36) PRIMARY KEY,
                    connection_id CHAR(36) NOT NULL,
                    provider_account_id VARCHAR(100),
                    name VARCHAR(255),
                    currency VARCHAR(3),
                    balance DECIMAL(10,2),
                    nature VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (connection_id) REFERENCES bank_connections(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_provider_acc (provider_account_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
        else:
            print("  -> 'bank_accounts' table exists")

        # 4. Update TRANSACTIONS
        print("Checking 'transactions' table...")
        if not column_exists(cursor, 'transactions', 'bank_account_id'):
            print("  -> Adding 'bank_account_id' column")
            cursor.execute("ALTER TABLE transactions ADD COLUMN bank_account_id CHAR(36) NULL")
            # Usually strict FK requires data integrity, adding without FK constraint first or ensuring data is clean
            # Adding FK definition:
            # cursor.execute("ALTER TABLE transactions ADD CONSTRAINT fk_tx_bank_acc FOREIGN KEY (bank_account_id) REFERENCES bank_accounts(id) ON DELETE SET NULL")

        if not column_exists(cursor, 'transactions', 'provider_transaction_id'):
            print("  -> Adding 'provider_transaction_id' column")
            cursor.execute("ALTER TABLE transactions ADD COLUMN provider_transaction_id VARCHAR(100) NULL")
            cursor.execute("ALTER TABLE transactions ADD UNIQUE KEY unique_provider_tx (bank_account_id, provider_transaction_id)")

        if not column_exists(cursor, 'transactions', 'currency'):
            print("  -> Adding 'currency' column")
            cursor.execute("ALTER TABLE transactions ADD COLUMN currency VARCHAR(3) DEFAULT 'EUR'")

        if not column_exists(cursor, 'transactions', 'transaction_date'):
            print("  -> Adding 'transaction_date' column (migrating from 'date' if exists)")
            if column_exists(cursor, 'transactions', 'date'):
                 cursor.execute("ALTER TABLE transactions CHANGE COLUMN `date` `transaction_date` DATE NOT NULL")
            else:
                 cursor.execute("ALTER TABLE transactions ADD COLUMN transaction_date DATE NOT NULL DEFAULT (CURRENT_DATE)")

        if not column_exists(cursor, 'transactions', 'extra_data'):
            print("  -> Adding 'extra_data' column")
            cursor.execute("ALTER TABLE transactions ADD COLUMN extra_data JSON NULL")

    print("\n✅ Database update completed successfully!")
    conn.close()

if __name__ == "__main__":
    run_migration()
