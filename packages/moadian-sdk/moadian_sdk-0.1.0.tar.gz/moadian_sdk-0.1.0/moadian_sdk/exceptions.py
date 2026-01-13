"""Custom exceptions for Moadian SDK"""


class MoadianException(Exception):
    """Base exception for Moadian SDK errors"""

    pass


class AuthenticationException(MoadianException):
    """Raised when authentication fails"""

    pass


class APIException(MoadianException):
    """Raised when API returns an error"""

    pass


class CertificateException(MoadianException):
    """Raised when certificate operations fail"""

    pass


class InvoiceException(MoadianException):
    """Raised when invoice operations fail"""

    pass
