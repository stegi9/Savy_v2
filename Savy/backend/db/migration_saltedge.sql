-- ============================================================================
-- MIGRATION SCRIPT FOR SALT EDGE INTEGRATION
-- Run this script in MySQL Workbench to update your existing database.
-- ============================================================================

USE savy_db;

-- 1. Updates to PROFILES table
-- Adding customer_id to link Savy User to Salt Edge Customer
ALTER TABLE profiles 
ADD COLUMN saltedge_customer_id VARCHAR(100) NULL,
ADD INDEX idx_saltedge_customer (saltedge_customer_id);

-- 2. Updates to BANK_CONNECTIONS table
-- Adding fields for Salt Edge connection tracking
ALTER TABLE bank_connections 
ADD COLUMN connection_id VARCHAR(100) NULL,
ADD COLUMN provider_code VARCHAR(50) NULL,
ADD COLUMN last_synced_at TIMESTAMP NULL,
ADD UNIQUE INDEX unique_connection (connection_id);

-- Optional: If you want to clean up old GoCardless columns, uncomment:
-- ALTER TABLE bank_connections DROP COLUMN requisition_id;
-- ALTER TABLE bank_connections DROP COLUMN provider_metadata;

-- 3. Create BANK_ACCOUNTS table
-- New table to store details of linked accounts (Card, Checking, etc.)
CREATE TABLE IF NOT EXISTS bank_accounts (
    id CHAR(36) PRIMARY KEY,
    connection_id CHAR(36) NOT NULL,
    provider_account_id VARCHAR(100),
    name VARCHAR(255),
    currency VARCHAR(3),
    balance DECIMAL(10,2),
    nature VARCHAR(50), -- account, card, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (connection_id) REFERENCES bank_connections(id) ON DELETE CASCADE,
    UNIQUE KEY unique_provider_acc (provider_account_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Updates to TRANSACTIONS table
-- Linking transactions to bank accounts and storing provider IDs for deduplication
ALTER TABLE transactions 
ADD COLUMN bank_account_id CHAR(36) NULL,
ADD COLUMN provider_transaction_id VARCHAR(100) NULL,
ADD COLUMN extra_data JSON NULL,
ADD UNIQUE INDEX unique_provider_tx (bank_account_id, provider_transaction_id);

-- Rename 'date' column to 'transaction_date' to avoid reserved keyword usage and match code
-- Verify first if your column is named 'date'. If so, run this:
ALTER TABLE transactions CHANGE COLUMN `date` `transaction_date` DATE NOT NULL;

-- Link FK (Safe to run only if bank_account_id column successfully created)
-- ALTER TABLE transactions ADD CONSTRAINT fk_tx_bank_acc FOREIGN KEY (bank_account_id) REFERENCES bank_accounts(id) ON DELETE SET NULL;

SELECT 'Migration completed successfully!' AS status;
