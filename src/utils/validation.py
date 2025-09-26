import re
from typing import Any, Dict, List, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)

class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


def validate_required(value: Any, field_name: str) -> Any:
    """
    Validate that a value is not None or empty

    Args:
        value: Value to validate
        field_name: Name of the field for error messages

    Returns:
        The validated value

    Raises:
        ValidationError: If value is None or empty
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationError(f"{field_name} is required", field_name)
    return value


def validate_email(email: str, field_name: str = "email") -> str:
    """
    Validate email format

    Args:
        email: Email string to validate
        field_name: Name of the field for error messages

    Returns:
        The validated email

    Raises:
        ValidationError: If email format is invalid
    """
    email = validate_required(email, field_name)

    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValidationError(f"Invalid {field_name} format", field_name)

    return email


def validate_string_length(value: str, min_length: int = None, max_length: int = None,
                          field_name: str = "string") -> str:
    """
    Validate string length constraints

    Args:
        value: String to validate
        min_length: Minimum length (optional)
        max_length: Maximum length (optional)
        field_name: Name of the field for error messages

    Returns:
        The validated string

    Raises:
        ValidationError: If length constraints are not met
    """
    value = validate_required(value, field_name)

    if min_length is not None and len(value) < min_length:
        raise ValidationError(f"{field_name} must be at least {min_length} characters", field_name)

    if max_length is not None and len(value) > max_length:
        raise ValidationError(f"{field_name} must be at most {max_length} characters", field_name)

    return value


def validate_user_data(data: Dict) -> Dict:
    """
    Validate user data for API endpoints

    Args:
        data: User data dictionary

    Returns:
        Validated and cleaned user data

    Raises:
        ValidationError: If validation fails
    """
    validated_data = {}

    # Validate name
    if 'name' in data:
        validated_data['name'] = validate_string_length(
            data['name'], min_length=2, max_length=100, field_name="name"
        )

    # Validate email
    if 'email' in data:
        validated_data['email'] = validate_email(data['email'])

    # Validate age (optional)
    if 'age' in data:
        try:
            age = int(data['age'])
            if age < 0 or age > 150:
                raise ValidationError("Age must be between 0 and 150", "age")
            validated_data['age'] = age
        except (ValueError, TypeError):
            raise ValidationError("Age must be a valid number", "age")

    return validated_data


def sanitize_input(text: str) -> str:
    """
    Sanitize input text to prevent XSS and other attacks

    Args:
        text: Input text to sanitize

    Returns:
        Sanitized text
    """
    if not text:
        return text

    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '&', '"', "'"]
    for char in dangerous_chars:
        text = text.replace(char, '')

    return text.strip()