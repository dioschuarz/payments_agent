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

