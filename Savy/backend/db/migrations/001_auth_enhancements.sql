-- =====================================================================
-- MIGRATION: Auth Enhancements (Refresh Token, Email Verification, Password Reset)
-- Date: 2026-01-31
-- =====================================================================

USE savy_db;

-- Add refresh token fields
ALTER TABLE profiles 
ADD COLUMN refresh_token VARCHAR(500) NULL AFTER saltedge_customer_id,
ADD COLUMN refresh_token_expires DATETIME NULL AFTER refresh_token;

-- Add email verification fields
ALTER TABLE profiles 
ADD COLUMN email_verified BOOLEAN DEFAULT FALSE AFTER refresh_token_expires,
ADD COLUMN email_verification_token VARCHAR(100) NULL AFTER email_verified,
ADD COLUMN email_verification_expires DATETIME NULL AFTER email_verification_token;

-- Add password reset fields
ALTER TABLE profiles
ADD COLUMN password_reset_token VARCHAR(100) NULL AFTER email_verification_expires,
ADD COLUMN password_reset_expires DATETIME NULL AFTER password_reset_token;

-- Add FCM token for push notifications
ALTER TABLE profiles
ADD COLUMN fcm_token VARCHAR(255) NULL AFTER password_reset_expires;

-- Add indexes for performance
CREATE INDEX idx_profiles_refresh_token ON profiles(refresh_token);
CREATE INDEX idx_profiles_email_verification_token ON profiles(email_verification_token);
CREATE INDEX idx_profiles_password_reset_token ON profiles(password_reset_token);
CREATE INDEX idx_profiles_fcm_token ON profiles(fcm_token);

-- Mark existing users as verified (optional - remove if you want to force verification)
UPDATE profiles SET email_verified = TRUE WHERE email_verified IS NULL;

SELECT 'Auth enhancements migration completed!' AS status;
