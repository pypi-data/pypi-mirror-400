# Copyright 2025 Raza Ahmad. Licensed under Apache 2.0.

"""
Healthcare Agents SDK Exceptions

Custom exception classes for the Healthcare Agents SDK.
"""

class HealthcareAgentsError(Exception):
    """Base exception for Healthcare Agents SDK"""
    pass

class APIError(HealthcareAgentsError):
    """Exception raised for API-related errors"""
    
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code

class ValidationError(HealthcareAgentsError):
    """Exception raised for data validation errors"""
    pass

class AuthenticationError(HealthcareAgentsError):
    """Exception raised for authentication errors"""
    pass

class RateLimitError(HealthcareAgentsError):
    """Exception raised when rate limit is exceeded"""
    pass

class NetworkError(HealthcareAgentsError):
    """Exception raised for network-related errors"""
    pass