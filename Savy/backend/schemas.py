"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal


# ============================================================================
# HEALTH & STATUS
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    environment: str
    version: str


# ============================================================================
# AUTHENTICATION
# ============================================================================

class LoginRequest(BaseModel):
    """Login request payload."""
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password", min_length=6)
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate and normalize email."""
        from utils.validators import validate_email
        if not validate_email(v):
            raise ValueError("Formato email non valido")
        return v.lower().strip()


class RegisterRequest(BaseModel):
    """Registration request payload."""
    email: str
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=100)
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate and normalize email."""
        from utils.validators import validate_email
        if not validate_email(v):
            raise ValueError("Formato email non valido")
        return v.lower().strip()
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength."""
        from utils.validators import validate_password_strength
        is_valid, error_msg = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        """Sanitize and validate full name."""
        from utils.validators import sanitize_string
        sanitized = sanitize_string(v, max_length=100)
        if len(sanitized) < 2:
            raise ValueError("Nome deve essere di almeno 2 caratteri")
        return sanitized


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int  # Access token expiry in seconds
    user_id: str  # User ID for client storage


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str = Field(..., description="Refresh token from login")


class PasswordResetRequest(BaseModel):
    """Password reset request (initiate)."""
    email: str = Field(..., description="User email")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate and normalize email."""
        from utils.validators import validate_email
        if not validate_email(v):
            raise ValueError("Formato email non valido")
        return v.lower().strip()


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation."""
    token: str = Field(..., description="Reset token from email")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength."""
        from utils.validators import validate_password_strength
        is_valid, error_msg = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v


class EmailVerificationRequest(BaseModel):
    """Email verification request."""
    token: str = Field(..., description="Verification token from email")


class ResendVerificationRequest(BaseModel):
    """Resend verification email request."""
    email: str = Field(..., description="User email")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate and normalize email."""
        from utils.validators import validate_email
        if not validate_email(v):
            raise ValueError("Formato email non valido")
        return v.lower().strip()


class FCMTokenUpdate(BaseModel):
    """FCM token update for push notifications."""
    fcm_token: str = Field(..., description="Firebase Cloud Messaging token")


# ============================================================================
# USER PROFILE
# ============================================================================

class ProfileResponse(BaseModel):
    """User profile response."""
    id: str
    email: str
    full_name: str
    current_balance: Decimal
    currency: str
    created_at: datetime
    updated_at: datetime


class ProfileUpdateRequest(BaseModel):
    """Profile update request."""
    full_name: Optional[str] = None
    current_balance: Optional[Decimal] = None


class UserSettingsUpdate(BaseModel):
    """User settings update request."""
    full_name: Optional[str] = None
    current_balance: Optional[Decimal] = Field(None, description="Account balance")
    monthly_budget: Optional[Decimal] = Field(None, ge=0)
    budget_notifications: Optional[bool] = None
    ai_tips_enabled: Optional[bool] = None
    optimization_alerts: Optional[bool] = None


class UserSettingsResponse(BaseModel):
    """User settings response."""
    full_name: str
    current_balance: Decimal
    monthly_budget: Decimal
    currency: str
    budget_notifications: bool
    ai_tips_enabled: bool
    optimization_alerts: bool


# ============================================================================
# TRANSACTIONS
# ============================================================================

class TransactionCreate(BaseModel):
    """Create transaction request."""
    amount: Decimal
    category: str
    description: Optional[str] = None
    transaction_date: date
    bank_account_id: Optional[str] = None
    is_recurring: bool = False
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        """Validate amount is positive and reasonable."""
        from utils.validators import validate_amount
        is_valid, error_msg = validate_amount(float(v))
        if not is_valid:
            raise ValueError(error_msg)
        return v
    
    @field_validator('description')
    @classmethod
    def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize description text."""
        if v:
            from utils.validators import sanitize_string, validate_transaction_description
            sanitized = sanitize_string(v, max_length=200)
            is_valid, error_msg = validate_transaction_description(sanitized)
            if not is_valid:
                raise ValueError(error_msg)
            return sanitized
        return v


class TransactionResponse(BaseModel):
    """Transaction response."""
    id: str
    user_id: str
    amount: Decimal
    category: Optional[str] = None
    category_id: Optional[str] = None
    merchant: Optional[str] = None
    description: Optional[str]
    transaction_date: date
    bank_account_id: Optional[str]
    is_recurring: bool
    needs_review: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# RECURRING BILLS
# ============================================================================

class BillCreate(BaseModel):
    """Create recurring bill request."""
    name: str
    amount: Decimal
    due_day: int = Field(..., ge=1, le=31)
    category: str
    provider: Optional[str] = None
    is_active: bool = True
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        """Validate amount is positive."""
        from utils.validators import validate_amount
        is_valid, error_msg = validate_amount(float(v))
        if not is_valid:
            raise ValueError(error_msg)
        return v
    
    @field_validator('name', 'provider')
    @classmethod
    def sanitize_text(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize text fields."""
        if v:
            from utils.validators import sanitize_string
            return sanitize_string(v, max_length=100)
        return v


class BillResponse(BaseModel):
    """Recurring bill response."""
    id: str
    user_id: str
    name: str
    amount: Decimal
    due_day: int
    category: str
    provider: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# OPTIMIZATION LEADS
# ============================================================================

class OptimizationLeadResponse(BaseModel):
    """Optimization lead response."""
    id: str
    user_id: str
    bill_id: Optional[str]
    bill_category: str
    current_cost: Decimal
    optimized_cost: Decimal
    savings_amount: Decimal
    partner_name: str
    partner_offer_details: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class OptimizationLeadUpdate(BaseModel):
    """Update optimization lead status."""
    status: str = Field(..., pattern="^(pending|accepted|rejected|contacted)$")


# ============================================================================
# CHAT / AGENT
# ============================================================================

class ChatRequest(BaseModel):
    """Chat request to the AI agent."""
    message: str = Field(..., min_length=1, max_length=1000)
    context: Optional[Dict[str, Any]] = None
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate and sanitize chat message."""
        from utils.validators import validate_user_query, sanitize_string
        sanitized = sanitize_string(v, max_length=1000)
        is_valid, error_msg = validate_user_query(sanitized)
        if not is_valid:
            raise ValueError(error_msg)
        return sanitized


class ChatResponse(BaseModel):
    """Chat response from the AI agent."""
    decision: str  # affordable, caution, not_affordable
    reasoning: str
    suggestion: Optional[str] = None
    optimization_leads: List[OptimizationLeadResponse] = []
    affiliate_offers: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatMessageResponse(BaseModel):
    """Chat message response (for history)."""
    id: str
    role: str  # user, assistant, system
    content: str
    metadata: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# AGENT STATE (Internal)
# ============================================================================

class AgentStateDict(BaseModel):
    """Internal state for LangGraph agent."""
    user_id: str
    balance: Decimal = Decimal("0.00")
    upcoming_bills: List[Dict[str, Any]] = []
    user_query: str
    analysis_result: Optional[Dict[str, Any]] = None
    decision: Optional[str] = None
    reasoning: Optional[str] = None
    optimization_leads: List[Dict[str, Any]] = []
    messages: List[Dict[str, str]] = []


# ============================================================================
# STANDARD API RESPONSE
# ============================================================================

class StandardResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ============================================================================
# CATEGORIZATION (AI Dynamic Categorization)
# ============================================================================

class TransactionCategorizeRequest(BaseModel):
    """Request to categorize a transaction with AI."""
    merchant: str = Field(..., description="Merchant/store name")
    amount: float = Field(..., description="Transaction amount")
    description: Optional[str] = Field(None, description="Optional transaction description")
    date: Optional[str] = Field(None, description="Transaction date")


class TransactionCategorizeResponse(BaseModel):
    """Response with AI categorization."""
    category: str = Field(..., description="Main category (e.g., 'groceries', 'transport')")
    subcategory: Optional[str] = Field(None, description="Subcategory (e.g., 'supermarket', 'electronics')")
    confidence: float = Field(..., description="AI confidence score (0.00-1.00)")
    needs_review: bool = Field(..., description="Whether the transaction needs manual review")
    reasoning: str = Field(..., description="Brief explanation of categorization")


# ============================================================================
# OPTIMIZATION (1-Click Optimization)
# ============================================================================

class OptimizationScanRequest(BaseModel):
    """Request to scan for optimization opportunities."""
    user_id: str = Field(..., description="User ID")
    categories: Optional[List[str]] = Field(
        default=["energy", "telco", "subscriptions", "insurance"],
        description="Bill categories to scan"
    )


class OptimizationOpportunity(BaseModel):
    """Single optimization opportunity."""
    bill_category: str
    current_provider: str
    current_cost: float
    recommended_provider: str
    optimized_cost: float
    savings_per_month: float
    savings_per_year: float
    partner_offer_url: Optional[str] = None
    confidence: float


class OptimizationScanResponse(BaseModel):
    """Response with optimization opportunities."""
    optimizations: List[OptimizationOpportunity]
    total_monthly_savings: float
    total_yearly_savings: float
    scanned_categories: List[str]


# ============================================================================
# USER CATEGORIES (Custom Categories Management)
# ============================================================================

class UserCategoryCreate(BaseModel):
    """Request to create a custom category."""
    name: str = Field(..., min_length=1, max_length=50, description="Category name")
    icon: Optional[str] = Field(None, description="Material icon name")
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$", description="Hex color")
    category_type: str = Field("expense", description="Category type: 'expense' or 'income'")
    budget_monthly: Optional[Decimal] = Field(None, ge=0, description="Monthly budget")
    
    @field_validator('name')
    @classmethod
    def validate_category_name(cls, v: str) -> str:
        """Validate and sanitize category name."""
        from utils.validators import validate_category_name, sanitize_string
        sanitized = sanitize_string(v, max_length=50)
        is_valid, error_msg = validate_category_name(sanitized)
        if not is_valid:
            raise ValueError(error_msg)
        return sanitized
    
    @field_validator('color')
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate hex color format."""
        if v:
            from utils.validators import validate_hex_color
            is_valid, error_msg = validate_hex_color(v)
            if not is_valid:
                raise ValueError(error_msg)
            return v.upper()
        return v


class UserCategoryUpdate(BaseModel):
    """Request to update a category."""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    icon: Optional[str] = None
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    budget_monthly: Optional[Decimal] = Field(None, ge=0)


class UserCategoryResponse(BaseModel):
    """Response with category data."""
    id: str
    user_id: str
    name: str
    icon: Optional[str]
    color: Optional[str]
    category_type: str
    budget_monthly: Optional[Decimal]
    is_system: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# SPENDING REPORT (Resoconto Spese)
# ============================================================================

class CategorySpending(BaseModel):
    """Spending summary for a single category."""
    category_id: Optional[str]
    category_name: str
    icon: Optional[str]
    color: Optional[str]
    total_spent: float
    transaction_count: int
    budget_monthly: float
    budget_percentage: float
    remaining_budget: float
    is_over_budget: bool
    percentage_of_total: float


class SpendingReportData(BaseModel):
    """Spending report data."""
    period: str
    start_date: str
    end_date: str
    total_spent: float
    total_income: float
    net_balance: float
    total_budget: float
    budget_remaining: float
    budget_percentage: float
    is_over_budget: bool
    categories: List[CategorySpending]
    generated_at: str


class SpendingReportResponse(BaseModel):
    """Response with spending report."""
    success: bool
    data: SpendingReportData


class DeepDiveRequest(BaseModel):
    """Request for deep dive analytics."""
    period: str = Field("monthly", description="Period: 'monthly', '3months', 'yearly'")
    bank_account_id: Optional[str] = Field(None, description="Filter by specific bank account ID")


class CategoryTrend(BaseModel):
    """Category spending trend over time."""
    date: str
    amount: float


class CategoryComparison(BaseModel):
    """Category comparison with previous period."""
    category_id: Optional[str]
    category_name: str
    icon: Optional[str]
    color: Optional[str]
    current_amount: float
    previous_amount: float
    change_percentage: float
    is_anomaly: bool
    trend_data: List[CategoryTrend]


class AIInsight(BaseModel):
    """AI-generated insight."""
    insight_type: str  # 'warning', 'success', 'info'
    title: str
    message: str
    category_id: Optional[str]


class CumulativeDataPoint(BaseModel):
    """Cumulative spending data point."""
    date: str
    daily_amount: float
    cumulative_amount: float


class DeepDiveData(BaseModel):
    """Deep dive analytics data."""
    period: str
    start_date: str
    end_date: str
    total_spent: float
    total_income: float
    net_balance: float
    previous_total_spent: float
    spending_velocity: float  # % faster/slower than usual
    projected_end_of_month: float
    current_cumulative: List[CumulativeDataPoint]
    previous_cumulative: List[CumulativeDataPoint]
    categories_comparison: List[CategoryComparison]
    ai_insights: List[AIInsight]
    generated_at: str


class DeepDiveResponse(BaseModel):
    """Response with deep dive analytics."""
    success: bool
    data: DeepDiveData



# ============================================================================
# BANK INTEGRATION
# ============================================================================

class BankInstitution(BaseModel):
    id: str
    name: str
    logo: str
    transaction_total_days: Optional[str] = "90"
    countries: List[str]

class BankConnectionResponse(BaseModel):
    id: str
    user_id: str
    connection_id: Optional[str]
    provider_code: Optional[str]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class BankLinkResponse(BaseModel):
    link: str
    # connect_session_secret: Optional[str] 

# ============================================================================
# MANUAL BANK ACCOUNTS
# ============================================================================

class BankAccountCreate(BaseModel):
    """Request to create a manual bank account."""
    name: str = Field(..., min_length=1, max_length=100)
    balance: Decimal = Field(default=0.0)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = None
    currency: str = Field(default="EUR", max_length=3)
    nature: str = Field(default="account", max_length=50)

class BankAccountUpdate(BaseModel):
    """Request to update a manual bank account."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    balance: Optional[Decimal] = None
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = None
    currency: Optional[str] = Field(None, max_length=3)
    nature: Optional[str] = Field(None, max_length=50)

class BankAccountResponse(BaseModel):
    """Response with bank account data."""
    id: str
    user_id: str
    connection_id: Optional[str]
    is_manual: bool
    provider_account_id: Optional[str]
    name: Optional[str]
    color: Optional[str]
    icon: Optional[str]
    currency: str
    balance: Optional[Decimal]
    nature: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
 
