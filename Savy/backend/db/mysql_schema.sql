-- ============================================================================
-- SAVY - MySQL Database Schema
-- ============================================================================
-- Version: 2.0.0
-- Architecture: Repository-Service-Controller
-- ============================================================================

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS savy_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE savy_db;

-- ============================================================================
-- PROFILES TABLE (Users)
-- ============================================================================

CREATE TABLE IF NOT EXISTS profiles (
    id CHAR(36) PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    current_balance DECIMAL(10,2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'EUR',
    saltedge_customer_id VARCHAR(100), -- Salt Edge Customer ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at),
    INDEX idx_saltedge_customer (saltedge_customer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ... (user_categories remains same) ...

-- ============================================================================
-- TRANSACTIONS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS transactions (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    bank_account_id CHAR(36), -- Link to bank_accounts
    provider_transaction_id VARCHAR(100), -- Salt Edge Transaction ID
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    merchant VARCHAR(255),
    description TEXT,
    transaction_date DATE NOT NULL, -- booking date (made_on)
    -- AI Categorization fields
    ai_confidence FLOAT,
    ai_context TEXT,
    needs_review BOOLEAN DEFAULT FALSE,
    extra_data JSON, -- Store raw provider metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE,
    -- FOREIGN KEY (bank_account_id) REFERENCES bank_accounts(id) ON DELETE SET NULL, -- Added later after table creation
    UNIQUE KEY unique_provider_tx (bank_account_id, provider_transaction_id),
    INDEX idx_user_id (user_id),
    INDEX idx_transaction_date (transaction_date),
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ... (recurring_bills, partners, optimization_leads remain same) ...

-- ============================================================================
-- BANK_CONNECTIONS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS bank_connections (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    connection_id VARCHAR(100), -- Salt Edge Connection ID
    provider_code VARCHAR(50),  -- e.g. fake_client_xf
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, disabled
    last_synced_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE,
    UNIQUE KEY unique_connection (connection_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================================
-- BANK_ACCOUNTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS bank_accounts (
    id CHAR(36) PRIMARY KEY,
    connection_id CHAR(36) NOT NULL,
    provider_account_id VARCHAR(100), -- Salt Edge Account ID
    name VARCHAR(255),
    currency VARCHAR(3),
    balance DECIMAL(10,2),
    nature VARCHAR(50), -- account, card, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (connection_id) REFERENCES bank_connections(id) ON DELETE CASCADE,
    UNIQUE KEY unique_provider_acc (provider_account_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================================
-- SEED DATA: Demo User
-- ============================================================================

INSERT INTO profiles (id, full_name, current_balance, currency, created_at, updated_at)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'Demo User',
    1500.00,
    'EUR',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
) ON DUPLICATE KEY UPDATE
    full_name = VALUES(full_name),
    current_balance = VALUES(current_balance);

-- ============================================================================
-- SEED DATA: Default System Categories for Demo User
-- ============================================================================

INSERT INTO user_categories (id, user_id, name, icon, color, is_system) VALUES
    (UUID(), '00000000-0000-0000-0000-000000000001', 'Alimentari', 'shopping_cart', '#10B981', TRUE),
    (UUID(), '00000000-0000-0000-0000-000000000001', 'Trasporti', 'directions_car', '#3B82F6', TRUE),
    (UUID(), '00000000-0000-0000-0000-000000000001', 'Ristoranti', 'restaurant', '#F59E0B', TRUE),
    (UUID(), '00000000-0000-0000-0000-000000000001', 'Bollette', 'receipt', '#EF4444', TRUE),
    (UUID(), '00000000-0000-0000-0000-000000000001', 'Intrattenimento', 'movie', '#8B5CF6', TRUE),
    (UUID(), '00000000-0000-0000-0000-000000000001', 'Shopping', 'shopping_bag', '#EC4899', TRUE),
    (UUID(), '00000000-0000-0000-0000-000000000001', 'Salute', 'health_and_safety', '#06B6D4', TRUE),
    (UUID(), '00000000-0000-0000-0000-000000000001', 'Casa', 'home', '#F97316', TRUE),
    (UUID(), '00000000-0000-0000-0000-000000000001', 'Altro', 'category', '#6B7280', TRUE)
ON DUPLICATE KEY UPDATE
    name = VALUES(name);

-- ============================================================================
-- SEED DATA: Sample Partners
-- ============================================================================

INSERT INTO partners (id, name, category, description, affiliate_url, is_active) VALUES
    (UUID(), 'Eni Luce & Gas', 'energy', 'Fornitore energia elettrica e gas', 'https://partner.example.com/eni', TRUE),
    (UUID(), 'Enel Energia', 'energy', 'Fornitore energia elettrica', 'https://partner.example.com/enel', TRUE),
    (UUID(), 'Iliad', 'telco', 'Operatore mobile low-cost', 'https://partner.example.com/iliad', TRUE),
    (UUID(), 'ho.mobile', 'telco', 'Operatore mobile virtuale', 'https://partner.example.com/ho', TRUE)
ON DUPLICATE KEY UPDATE
    name = VALUES(name);

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

SELECT '✅ MySQL Schema created successfully!' AS message;
SELECT 'Demo user UUID: 00000000-0000-0000-0000-000000000001' AS info;
SELECT 'Database: savy_db' AS database_name;


