# Copyright 2025 Raza Ahmad. Licensed under Apache 2.0.

"""
Healthcare Agents Python SDK

A Python client library for the Privacy-Preserving Healthcare Agents API.
Provides easy access to eligibility verification, prescription validation,
and federated learning capabilities with zero-knowledge proofs.
"""

from .client import HealthcareAgentsClient, HealthcareAgentsClientSync
from .models import PatientData, EligibilityRequest, PrescriptionRequest, FederatedLearningRequest
from .exceptions import HealthcareAgentsError, APIError, ValidationError

__version__ = "0.1.0"
__author__ = "Raza Ahmad"
__email__ = "raza@healthcare-agents.com"
__license__ = "Apache 2.0"

__all__ = [
    "HealthcareAgentsClient",
    "HealthcareAgentsClientSync",
    "PatientData", 
    "EligibilityRequest",
    "PrescriptionRequest", 
    "FederatedLearningRequest",
    "HealthcareAgentsError",
    "APIError",
    "ValidationError"
]