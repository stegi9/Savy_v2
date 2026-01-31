"""
Custom exception classes for better error handling.
"""
from fastapi import HTTPException, status


class SavyException(HTTPException):
    """Base exception for Savy application."""
    def __init__(self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(status_code=status_code, detail=detail)


class UserNotFoundException(SavyException):
    """Raised when a user is not found."""
    def __init__(self, user_id: str):
        super().__init__(
            detail=f"User {user_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class CategoryNotFoundException(SavyException):
    """Raised when a category is not found."""
    def __init__(self, category_id: str):
        super().__init__(
            detail=f"Category {category_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class TransactionNotFoundException(SavyException):
    """Raised when a transaction is not found."""
    def __init__(self, transaction_id: str):
        super().__init__(
            detail=f"Transaction {transaction_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class InvalidCredentialsException(SavyException):
    """Raised when login credentials are invalid."""
    def __init__(self):
        super().__init__(
            detail="Invalid email or password",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class DuplicateEmailException(SavyException):
    """Raised when attempting to register with an existing email."""
    def __init__(self, email: str):
        super().__init__(
            detail=f"Email {email} is already registered",
            status_code=status.HTTP_409_CONFLICT
        )


class InsufficientBalanceException(SavyException):
    """Raised when user has insufficient balance."""
    def __init__(self, balance: float, required: float):
        super().__init__(
            detail=f"Insufficient balance: €{balance:.2f} available, €{required:.2f} required",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class LLMServiceException(SavyException):
    """Raised when LLM service fails."""
    def __init__(self, error: str):
        super().__init__(
            detail=f"AI service temporarily unavailable: {error}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


class DatabaseException(SavyException):
    """Raised when database operation fails."""
    def __init__(self, error: str):
        super().__init__(
            detail="Database operation failed. Please try again later.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ValidationException(SavyException):
    """Raised when input validation fails."""
    def __init__(self, field: str, message: str):
        super().__init__(
            detail=f"Validation error for {field}: {message}",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
