"""
CHRONOS Custom Exceptions
"""


class ChronosError(Exception):
    """Base exception for all CHRONOS errors."""
    
    def __init__(self, message: str, code: str = "CHRONOS_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class SecurityError(ChronosError):
    """Exception raised for security-related errors."""
    
    def __init__(self, message: str, code: str = "SECURITY_ERROR"):
        super().__init__(message, code)


class QuantumError(ChronosError):
    """Exception raised for quantum cryptography errors."""
    
    def __init__(self, message: str, code: str = "QUANTUM_ERROR"):
        super().__init__(message, code)


class ConfigurationError(ChronosError):
    """Exception raised for configuration errors."""
    
    def __init__(self, message: str, code: str = "CONFIG_ERROR"):
        super().__init__(message, code)


class IntegrationError(ChronosError):
    """Exception raised for integration/plugin errors."""
    
    def __init__(self, message: str, code: str = "INTEGRATION_ERROR"):
        super().__init__(message, code)
