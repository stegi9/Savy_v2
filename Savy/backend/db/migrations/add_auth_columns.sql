-- ============================================================================
-- SAVY Database Migration - Add Auth Enhancement Columns
-- Execute this script to add missing columns to your profiles table
-- ============================================================================

-- Add refresh token columns
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS refresh_token VARCHAR(500) NULL;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS refresh_token_expires DATETIME NULL;

-- Add email verification columns
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE NOT NULL;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS email_verification_token VARCHAR(100) NULL;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS email_verification_expires DATETIME NULL;

-- Add password reset columns (might already exist)
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS password_reset_token VARCHAR(100) NULL;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS password_reset_expires DATETIME NULL;

-- Add FCM token for push notifications
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS fcm_token VARCHAR(255) NULL;

-- Create refresh_tokens table if not exists
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id CHAR(36) PRIMARY KEY,
    token VARCHAR(500) NOT NULL UNIQUE,
    user_id CHAR(36) NOT NULL,
    expires_at DATETIME NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    revoked_at DATETIME NULL,
    INDEX idx_refresh_tokens_token (token),
    INDEX idx_refresh_tokens_user_id (user_id),
    FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Verify columns were added
SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'profiles' 
AND TABLE_SCHEMA = DATABASE()
ORDER BY ORDINAL_POSITION;
