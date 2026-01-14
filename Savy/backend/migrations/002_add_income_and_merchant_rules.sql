-- Migration: Add income support and merchant rules
-- Date: 2026-01-03

-- 1. Add transaction_type column to transactions
ALTER TABLE transactions 
ADD COLUMN transaction_type VARCHAR(20) DEFAULT 'expense' AFTER amount;

-- 2. Create merchant_rules table for AI learning
CREATE TABLE IF NOT EXISTS merchant_rules (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    category_id CHAR(36) NOT NULL,
    merchant_pattern VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES user_categories(id) ON DELETE CASCADE,
    
    -- Unique constraint: one rule per merchant per user
    UNIQUE KEY unique_user_merchant (user_id, merchant_pattern),
    
    INDEX idx_merchant_rules_user (user_id),
    INDEX idx_merchant_rules_pattern (merchant_pattern)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Update existing transactions to have transaction_type = 'expense'
UPDATE transactions SET transaction_type = 'expense' WHERE transaction_type IS NULL;

