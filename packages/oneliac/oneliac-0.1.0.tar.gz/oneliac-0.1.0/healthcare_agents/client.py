# Copyright 2025 Raza Ahmad. Licensed under Apache 2.0.

"""
Healthcare Agents API Client

Main client class for interacting with the Healthcare Agents API.
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Union
from .models import PatientData, EligibilityRequest, PrescriptionRequest, FederatedLearningRequest
from .exceptions import APIError, ValidationError

class HealthcareAgentsClient:
    """
    Client for Healthcare Agents API
    
    Provides methods for eligibility verification, prescription validation,
    and federated learning operations with privacy-preserving features.
    """
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 30):
        """
        Initialize the Healthcare Agents client
        
        Args:
            base_url: Base URL of the Healthcare Agents API
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "healthcare-agents-python-sdk/0.1.0"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        Make HTTP request to the API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request data for POST requests
            
        Returns:
            Response data as dictionary
            
        Raises:
            APIError: If the API returns an error
        """
        if not self.session:
            raise RuntimeError("Client must be used as async context manager")
        
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        try:
            async with self.session.request(
                method, url, headers=headers, json=data
            ) as response:
                response_data = await response.json()
                
                if response.status >= 400:
                    error_msg = response_data.get('detail', f'HTTP {response.status}')
                    raise APIError(f"API Error: {error_msg}", status_code=response.status)
                
                return response_data
                
        except aiohttp.ClientError as e:
            raise APIError(f"Connection error: {str(e)}")
        except json.JSONDecodeError:
            raise APIError("Invalid JSON response from API")
    
    async def health_check(self) -> Dict[str, str]:
        """
        Check API health status
        
        Returns:
            Health status information
        """
        return await self._make_request("GET", "/health")
    
    async def verify_eligibility(self, request: EligibilityRequest) -> Dict[str, Union[bool, str, float]]:
        """
        Verify patient eligibility for a medical procedure
        
        Args:
            request: Eligibility verification request
            
        Returns:
            Eligibility verification result with ZK proof
        """
        data = {
            "patient_data": request.patient_data.to_dict(),
            "procedure_code": request.procedure_code
        }
        return await self._make_request("POST", "/eligibility/verify", data)
    
    async def validate_prescription(self, request: PrescriptionRequest) -> Dict[str, Union[bool, List, float]]:
        """
        Validate prescription safety and check for drug interactions
        
        Args:
            request: Prescription validation request
            
        Returns:
            Prescription validation result with safety information
        """
        data = {
            "patient_data": request.patient_data.to_dict(),
            "drug_code": request.drug_code
        }
        return await self._make_request("POST", "/prescription/validate", data)
    
    async def federated_learning_train(self, request: FederatedLearningRequest) -> Dict[str, Union[bool, str, float]]:
        """
        Participate in federated learning training round
        
        Args:
            request: Federated learning training request
            
        Returns:
            Training result with model updates
        """
        data = {
            "patient_datasets": [pd.to_dict() for pd in request.patient_datasets]
        }
        return await self._make_request("POST", "/federated-learning/train", data)
    
    async def federated_learning_status(self) -> Dict[str, Union[int, float, str]]:
        """
        Get federated learning system status
        
        Returns:
            Current status of federated learning system
        """
        return await self._make_request("GET", "/federated-learning/status")

# Synchronous wrapper for easier usage
class HealthcareAgentsClientSync:
    """
    Synchronous wrapper for HealthcareAgentsClient
    
    Provides the same functionality but with synchronous methods.
    """
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 30):
        self.client = HealthcareAgentsClient(base_url, api_key, timeout)
    
    def _run_async(self, coro):
        """Run async coroutine in sync context"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)
    
    def health_check(self) -> Dict[str, str]:
        """Check API health status (synchronous)"""
        async def _health_check():
            async with self.client as client:
                return await client.health_check()
        return self._run_async(_health_check())
    
    def verify_eligibility(self, request: EligibilityRequest) -> Dict[str, Union[bool, str, float]]:
        """Verify patient eligibility (synchronous)"""
        async def _verify_eligibility():
            async with self.client as client:
                return await client.verify_eligibility(request)
        return self._run_async(_verify_eligibility())
    
    def validate_prescription(self, request: PrescriptionRequest) -> Dict[str, Union[bool, List, float]]:
        """Validate prescription (synchronous)"""
        async def _validate_prescription():
            async with self.client as client:
                return await client.validate_prescription(request)
        return self._run_async(_validate_prescription())
    
    def federated_learning_train(self, request: FederatedLearningRequest) -> Dict[str, Union[bool, str, float]]:
        """Participate in federated learning (synchronous)"""
        async def _federated_learning_train():
            async with self.client as client:
                return await client.federated_learning_train(request)
        return self._run_async(_federated_learning_train())
    
    def federated_learning_status(self) -> Dict[str, Union[int, float, str]]:
        """Get federated learning status (synchronous)"""
        async def _federated_learning_status():
            async with self.client as client:
                return await client.federated_learning_status()
        return self._run_async(_federated_learning_status())