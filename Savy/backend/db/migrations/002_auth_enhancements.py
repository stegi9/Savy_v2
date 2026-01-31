"""
Alembic migration: Add refresh tokens and auth fields
Revision ID: 002_auth_enhancements
Created: 2026-01-31
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import CHAR

# revision identifiers
revision = '002_auth_enhancements'
down_revision = '001_initial'  # Adjust based on your last migration
branch_labels = None
depends_on = None


def upgrade():
    """Add refresh tokens table and new auth fields to profiles."""
    
    # 1. Create refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', CHAR(36), primary_key=True),
        sa.Column('token', sa.String(500), nullable=False, unique=True, index=True),
        sa.Column('user_id', CHAR(36), sa.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('is_revoked', sa.Boolean, default=False, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('revoked_at', sa.DateTime, nullable=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4'
    )
    
    # Index on user_id for faster lookups
    op.create_index('idx_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    
    # 2. Add new fields to profiles table (if they don't exist)
    
    # Email verification fields
    try:
        op.add_column('profiles', sa.Column('email_verified', sa.Boolean, default=False, nullable=False, server_default='0'))
    except:
        pass  # Column might already exist
    
    try:
        op.add_column('profiles', sa.Column('email_verification_token', sa.String(100), nullable=True))
    except:
        pass
    
    try:
        op.add_column('profiles', sa.Column('email_verification_expires', sa.DateTime, nullable=True))
    except:
        pass
    
    # Password reset fields (might already exist from your schema)
    try:
        op.add_column('profiles', sa.Column('password_reset_token', sa.String(100), nullable=True))
    except:
        pass
    
    try:
        op.add_column('profiles', sa.Column('password_reset_expires', sa.DateTime, nullable=True))
    except:
        pass
    
    # FCM token for push notifications
    try:
        op.add_column('profiles', sa.Column('fcm_token', sa.String(255), nullable=True))
    except:
        pass
    
    # Refresh token storage (alternative to separate table, keeping for backward compatibility)
    try:
        op.add_column('profiles', sa.Column('refresh_token', sa.String(500), nullable=True))
    except:
        pass
    
    try:
        op.add_column('profiles', sa.Column('refresh_token_expires', sa.DateTime, nullable=True))
    except:
        pass
    
    print("✅ Migration 002: Auth enhancements applied successfully")


def downgrade():
    """Revert auth enhancements."""
    
    # Drop refresh_tokens table
    op.drop_table('refresh_tokens')
    
    # Drop added columns from profiles
    columns_to_drop = [
        'email_verified',
        'email_verification_token',
        'email_verification_expires',
        'fcm_token',
        'refresh_token',
        'refresh_token_expires'
    ]
    
    for column in columns_to_drop:
        try:
            op.drop_column('profiles', column)
        except:
            pass  # Column might not exist
    
    print("✅ Migration 002: Rolled back successfully")
