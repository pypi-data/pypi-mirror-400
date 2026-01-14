class ValidationException(Exception):
    """Raised when input validation fails"""
    pass


class NetworkException(Exception):
    """Raised when network request fails or captcha is not ready"""
    pass


class TimeoutException(Exception):
    """Raised when captcha solving timeout is exceeded"""
    pass


class ApiException(Exception):
    """Raised when API returns an error"""
    pass


class SolverExceptions:
    """Container for all solver exceptions"""
    VALIDATION_EXCEPTION = ValidationException
    NETWORK_EXCEPTION = NetworkException
    TIMEOUT_EXCEPTION = TimeoutException
    API_EXCEPTION = ApiException
