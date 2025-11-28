"""Domain exceptions."""


class DomainException(Exception):
    """Base exception for domain layer."""

    pass


class InvalidAmountError(DomainException):
    """Raised when an invalid amount is provided."""

    pass


class InvalidCountryError(DomainException):
    """Raised when an invalid country is provided."""

    pass


class InvalidDeliveryMethodError(DomainException):
    """Raised when an invalid delivery method is provided."""

    pass


class InvalidStateTransitionError(DomainException):
    """Raised when an invalid state transition is attempted."""

    pass


class AmbiguityResolutionError(DomainException):
    """Raised when ambiguity resolution fails."""

    pass


class ADKServiceUnavailableError(DomainException):
    """Raised when Google ADK service is unavailable after retries."""

    def __init__(self, message: str, attempts: int = 0, original_error: Exception = None):
        """
        Initialize ADK service unavailable error.

        Args:
            message: Error message
            attempts: Number of retry attempts made
            original_error: Original exception that caused the error
        """
        super().__init__(message)
        self.attempts = attempts
        self.original_error = original_error


class AgentFlowError(DomainException):
    """Raised when agent flow processing fails."""

    def __init__(self, message: str, user_friendly_message: str = None, original_error: Exception = None):
        """
        Initialize agent flow error.

        Args:
            message: Technical error message
            user_friendly_message: User-friendly error message
            original_error: Original exception that caused the error
        """
        super().__init__(message)
        self.user_friendly_message = user_friendly_message or message
        self.original_error = original_error

