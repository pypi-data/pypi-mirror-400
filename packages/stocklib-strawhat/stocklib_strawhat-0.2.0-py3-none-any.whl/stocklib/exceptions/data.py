from typing import Any, List, Optional


class DataError(Exception):
    """
    Base exception for data-related errors.
    Raised when data is invalid, missing, or cannot be processed.
    """
    pass


class DataValidationError(DataError):
    """
    Exception raised when data fails validation (e.g., Pydantic validation).
    
    Args:
        message: Error message describing the validation failure
        field: Optional field name that failed validation
        value: Optional value that failed validation
    """
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)


class IncompleteDataError(DataError):
    """
    Exception raised when required data is missing or incomplete.
    
    Args:
        message: Error message describing what data is missing
        missing_fields: Optional list of missing field names
    """
    def __init__(self, message: str, missing_fields: Optional[List[str]] = None):
        self.message = message
        self.missing_fields = missing_fields or []
        super().__init__(self.message)


class DataParsingError(DataError):
    """
    Exception raised when data cannot be parsed (e.g., date parsing, number conversion).
    
    Args:
        message: Error message describing the parsing failure
        data: Optional raw data that failed to parse
        data_type: Optional expected data type
    """
    def __init__(self, message: str, data: Any = None, data_type: Optional[str] = None):
        self.message = message
        self.data = data
        self.data_type = data_type
        super().__init__(self.message)

