"""
Enhanced Pydantic schemas with comprehensive validation.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal


# ============================================================================
# CUSTOM VALIDATORS
# ============================================================================

def validate_password(password: str) -> str:
    """Validate password strength."""
    from utils.validators import validate_password_strength
    
    is_valid, error_msg = validate_password_strength(password)
    if not is_valid:
        raise ValueError(error_msg)
    return password


def validate_email_format(email: str) -> str:
    """Validate email format."""
    from utils.validators import validate_email
    
    if not validate_email(email):
        raise ValueError("Formato email non valido")
    return email.lower()


def validate_amount_value(amount: float) -> float:
    """Validate monetary amount."""
    from utils.validators import validate_amount
    
    is_valid, error_msg = validate_amount(amount)
    if not is_valid:
        raise ValueError(error_msg)
    return amount


# ============================================================================
# AUTHENTICATION (Enhanced)
# ============================================================================

class LoginRequest(BaseModel):
    """Login request payload with validation."""
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password", min_length=6)
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        return validate_email_format(v)


class RegisterRequest(BaseModel):
    """Registration request payload with validation."""
    email: str
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=100)
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        return validate_email_format(v)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        return validate_password(v)
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        from utils.validators import sanitize_string
        sanitized = sanitize_string(v, max_length=100)
        if len(sanitized) < 2:
            raise ValueError("Nome deve essere di almeno 2 caratteri")
        return sanitized


# ============================================================================
# TRANSACTIONS (Enhanced)
# ============================================================================

class TransactionCreate(BaseModel):
    """Create transaction request with validation."""
    amount: float
    category: str
    description: Optional[str] = None
    transaction_date: date
    is_recurring: bool = False
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: float) -> float:
        return validate_amount_value(v)
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v:
            from utils.validators import sanitize_string
            return sanitize_string(v, max_length=200)
        return v


# ============================================================================
# CATEGORIES (Enhanced)
# ============================================================================

class UserCategoryCreate(BaseModel):
    """Request to create a custom category with validation."""
    name: str = Field(..., min_length=1, max_length=50)
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    category_type: str = Field("expense", pattern=r"^(expense|income)$")
    budget_monthly: Optional[Decimal] = Field(None, ge=0, le=1000000)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        from utils.validators import validate_category_name, sanitize_string
        
        sanitized = sanitize_string(v, max_length=50)
        is_valid, error_msg = validate_category_name(sanitized)
        if not is_valid:
            raise ValueError(error_msg)
        return sanitized


# ============================================================================
# CHAT (Enhanced)
# ============================================================================

class ChatRequest(BaseModel):
    """Chat request with validation."""
    message: str = Field(..., min_length=1, max_length=1000)
    context: Optional[Dict[str, Any]] = None
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v: str) -> str:
        from utils.validators import validate_user_query, sanitize_string
        
        sanitized = sanitize_string(v, max_length=1000)
        is_valid, error_msg = validate_user_query(sanitized)
        if not is_valid:
            raise ValueError(error_msg)
        return sanitized


# Note: Keep all existing schemas from the original schemas.py
# This file shows only the enhanced versions with validation
