"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field, validator
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


class RegisterRequest(BaseModel):
    """Registration request payload."""
    email: str
    password: str = Field(..., min_length=6)
    full_name: str


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


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
    is_recurring: bool = False


class TransactionResponse(BaseModel):
    """Transaction response."""
    id: str
    user_id: str
    amount: Decimal
    category: str
    description: Optional[str]
    transaction_date: date
    is_recurring: bool
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


class ChatResponse(BaseModel):
    """Chat response from the AI agent."""
    decision: str  # affordable, caution, not_affordable
    reasoning: str
    suggestion: Optional[str] = None
    optimization_leads: List[OptimizationLeadResponse] = []
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
