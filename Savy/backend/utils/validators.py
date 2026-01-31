"""
Input validation utilities for enhanced security and data integrity.
"""
import re
from typing import Optional
from decimal import Decimal
from datetime import datetime


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength.
    
    Password must:
    - Be at least 8 characters
    - Contain at least one uppercase letter
    - Contain at least one lowercase letter
    - Contain at least one number
    - Contain at least one special character
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password deve essere di almeno 8 caratteri"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password deve contenere almeno una lettera maiuscola"
    
    if not re.search(r'[a-z]', password):
        return False, "Password deve contenere almeno una lettera minuscola"
    
    if not re.search(r'[0-9]', password):
        return False, "Password deve contenere almeno un numero"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;/]', password):
        return False, "Password deve contenere almeno un carattere speciale"
    
    return True, None


def validate_amount(amount: float, min_value: float = 0.01, max_value: float = 1000000.0) -> tuple[bool, Optional[str]]:
    """
    Validate monetary amount.
    
    Args:
        amount: Amount to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if amount < min_value:
        return False, f"Importo deve essere almeno €{min_value:.2f}"
    
    if amount > max_value:
        return False, f"Importo non può superare €{max_value:.2f}"
    
    # Check for reasonable decimal places (max 2)
    decimal_amount = Decimal(str(amount))
    if decimal_amount.as_tuple().exponent < -2:
        return False, "Importo può avere massimo 2 decimali"
    
    return True, None


def validate_category_name(name: str) -> tuple[bool, Optional[str]]:
    """
    Validate category name.
    
    Args:
        name: Category name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name or len(name.strip()) == 0:
        return False, "Nome categoria non può essere vuoto"
    
    if len(name) > 50:
        return False, "Nome categoria troppo lungo (max 50 caratteri)"
    
    # Only alphanumeric, spaces, and common punctuation
    if not re.match(r'^[a-zA-Z0-9\sàèéìòùÀÈÉÌÒÙ_\-&\'\.]+$', name):
        return False, "Nome categoria contiene caratteri non validi"
    
    return True, None


def validate_hex_color(color: str) -> tuple[bool, Optional[str]]:
    """
    Validate hex color code.
    
    Args:
        color: Hex color to validate (e.g., #FF5733)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not color:
        return True, None  # Color is optional
    
    if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
        return False, "Colore deve essere in formato hex (es: #FF5733)"
    
    return True, None


def validate_date_string(date_str: str, format: str = "%Y-%m-%d") -> tuple[bool, Optional[str]]:
    """
    Validate date string format.
    
    Args:
        date_str: Date string to validate
        format: Expected date format (default: YYYY-MM-DD)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        datetime.strptime(date_str, format)
        return True, None
    except ValueError:
        return False, f"Data non valida (formato atteso: {format})"


def validate_due_day(day: int) -> tuple[bool, Optional[str]]:
    """
    Validate bill due day (1-31).
    
    Args:
        day: Day of month
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if day < 1 or day > 31:
        return False, "Giorno deve essere tra 1 e 31"
    
    return True, None


def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize user input string.
    
    Args:
        text: Text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    # Remove leading/trailing whitespace
    sanitized = text.strip()
    
    # Remove multiple consecutive spaces
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    # Truncate if needed
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def validate_transaction_description(description: str) -> tuple[bool, Optional[str]]:
    """
    Validate transaction description/merchant name.
    
    Args:
        description: Description to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not description or len(description.strip()) == 0:
        return False, "Descrizione non può essere vuota"
    
    if len(description) > 200:
        return False, "Descrizione troppo lunga (max 200 caratteri)"
    
    return True, None


def validate_user_query(query: str) -> tuple[bool, Optional[str]]:
    """
    Validate AI chat query.
    
    Args:
        query: User query to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not query or len(query.strip()) == 0:
        return False, "Messaggio non può essere vuoto"
    
    if len(query) > 1000:
        return False, "Messaggio troppo lungo (max 1000 caratteri)"
    
    # Check for potential injection attempts (basic)
    suspicious_patterns = [
        r'<script',
        r'javascript:',
        r'onerror=',
        r'onclick=',
    ]
    
    query_lower = query.lower()
    for pattern in suspicious_patterns:
        if re.search(pattern, query_lower):
            return False, "Messaggio contiene contenuto non consentito"
    
    return True, None
