-- ============================================================================
-- SAVY DATABASE MIGRATIONS
-- Version: 1.0.0
-- Date: 2026-01-03
-- ============================================================================
-- 
-- Run this file in MySQL Workbench to set up or update the database schema.
-- The main schema is in: backend/db/mysql_schema.sql
-- 
-- This file contains additional columns added after initial deployment.
-- ============================================================================

-- ============================================================================
-- MIGRATION 1: Add authentication fields
-- ============================================================================

-- Add email and hashed_password columns (skip if already exist)
-- ALTER TABLE profiles
-- ADD COLUMN email VARCHAR(255) UNIQUE NOT NULL AFTER id,
-- ADD COLUMN hashed_password VARCHAR(255) NOT NULL AFTER email;

-- Add email index for faster lookups
-- ALTER TABLE profiles ADD INDEX idx_profiles_email (email);


-- ============================================================================
-- MIGRATION 2: Add user settings fields
-- ============================================================================

-- Add monthly budget column
-- ALTER TABLE profiles ADD COLUMN monthly_budget DECIMAL(10,2) DEFAULT 2000.00;

-- Add notification settings
-- ALTER TABLE profiles ADD COLUMN budget_notifications BOOLEAN DEFAULT TRUE;
-- ALTER TABLE profiles ADD COLUMN ai_tips_enabled BOOLEAN DEFAULT TRUE;
-- ALTER TABLE profiles ADD COLUMN optimization_alerts BOOLEAN DEFAULT TRUE;


-- ============================================================================
-- SAFE MIGRATION SCRIPT (run these one by one, ignore errors for existing columns)
-- ============================================================================

-- Step 1: Add email column
ALTER TABLE profiles ADD COLUMN email VARCHAR(255) AFTER id;
ALTER TABLE profiles ADD UNIQUE INDEX idx_profiles_email (email);

-- Step 2: Add password column  
ALTER TABLE profiles ADD COLUMN hashed_password VARCHAR(255) AFTER email;

-- Step 3: Add budget column
ALTER TABLE profiles ADD COLUMN monthly_budget DECIMAL(10,2) DEFAULT 2000.00 AFTER current_balance;

-- Step 4: Add notification settings
ALTER TABLE profiles ADD COLUMN budget_notifications BOOLEAN DEFAULT TRUE AFTER currency;
ALTER TABLE profiles ADD COLUMN ai_tips_enabled BOOLEAN DEFAULT TRUE AFTER budget_notifications;
ALTER TABLE profiles ADD COLUMN optimization_alerts BOOLEAN DEFAULT TRUE AFTER ai_tips_enabled;

-- Step 5: Update existing records with defaults
UPDATE profiles SET 
    email = CONCAT('user_', id, '@savy.local'),
    hashed_password = '$argon2id$v=19$m=65536,t=3,p=4$placeholder',
    monthly_budget = 2000.00,
    budget_notifications = TRUE,
    ai_tips_enabled = TRUE,
    optimization_alerts = TRUE
WHERE email IS NULL;

-- Step 6: Make required columns NOT NULL (run after updating existing data)
-- ALTER TABLE profiles MODIFY email VARCHAR(255) NOT NULL;
-- ALTER TABLE profiles MODIFY hashed_password VARCHAR(255) NOT NULL;


-- ============================================================================
-- VERIFY SCHEMA
-- ============================================================================
DESCRIBE profiles;

