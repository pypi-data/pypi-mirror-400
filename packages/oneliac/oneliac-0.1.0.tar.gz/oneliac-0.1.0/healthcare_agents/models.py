# Copyright 2025 Raza Ahmad. Licensed under Apache 2.0.

"""
Healthcare Agents SDK Models

Data models for API requests and responses.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import hashlib
import json

@dataclass
class PatientData:
    """
    Patient data structure for healthcare operations
    
    Attributes:
        patient_id: Unique patient identifier
        encrypted_data: Encrypted patient information
        ipfs_cid: IPFS content identifier for data storage
        data_hash: Hash of the patient data for verification
    """
    patient_id: str
    encrypted_data: str
    ipfs_cid: str
    data_hash: str
    
    @classmethod
    def create(cls, patient_id: str, raw_data: Dict, encryption_key: Optional[str] = None) -> 'PatientData':
        """
        Create PatientData from raw patient information
        
        Args:
            patient_id: Unique patient identifier
            raw_data: Raw patient data dictionary
            encryption_key: Optional encryption key (uses default if not provided)
            
        Returns:
            PatientData instance with encrypted data
        """
        # Convert raw data to JSON string
        data_json = json.dumps(raw_data, sort_keys=True)
        
        # Create hash of the data
        data_hash = hashlib.sha256(data_json.encode()).hexdigest()
        
        # For demo purposes, use base64 encoding as "encryption"
        # In production, use proper encryption like Fernet
        import base64
        encrypted_data = base64.b64encode(data_json.encode()).decode()
        
        # Generate mock IPFS CID
        ipfs_cid = f"Qm{data_hash[:32]}"
        
        return cls(
            patient_id=patient_id,
            encrypted_data=encrypted_data,
            ipfs_cid=ipfs_cid,
            data_hash=data_hash
        )
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for API requests"""
        return {
            "patient_id": self.patient_id,
            "encrypted_data": self.encrypted_data,
            "ipfs_cid": self.ipfs_cid,
            "data_hash": self.data_hash
        }

@dataclass
class EligibilityRequest:
    """
    Request for patient eligibility verification
    
    Attributes:
        patient_data: Patient data with encrypted information
        procedure_code: Medical procedure code to check eligibility for
    """
    patient_data: PatientData
    procedure_code: str
    
    def validate(self) -> bool:
        """Validate the request data"""
        if not self.patient_data.patient_id:
            raise ValueError("Patient ID is required")
        if not self.procedure_code:
            raise ValueError("Procedure code is required")
        return True

@dataclass
class PrescriptionRequest:
    """
    Request for prescription validation
    
    Attributes:
        patient_data: Patient data with encrypted medical history
        drug_code: Drug code to validate
    """
    patient_data: PatientData
    drug_code: str
    
    def validate(self) -> bool:
        """Validate the request data"""
        if not self.patient_data.patient_id:
            raise ValueError("Patient ID is required")
        if not self.drug_code:
            raise ValueError("Drug code is required")
        return True

@dataclass
class FederatedLearningRequest:
    """
    Request for federated learning participation
    
    Attributes:
        patient_datasets: List of patient data for training
    """
    patient_datasets: List[PatientData]
    
    def validate(self) -> bool:
        """Validate the request data"""
        if not self.patient_datasets:
            raise ValueError("At least one patient dataset is required")
        for pd in self.patient_datasets:
            if not pd.patient_id:
                raise ValueError("All patient datasets must have patient_id")
        return True

# Response models for type hints
@dataclass
class EligibilityResponse:
    """Response from eligibility verification"""
    eligible: bool
    coverage_percentage: Optional[float]
    zk_proof_hash: str
    reason: Optional[str] = None

@dataclass
class PrescriptionResponse:
    """Response from prescription validation"""
    safe: bool
    interactions: List[str]
    confidence: float
    warnings: List[str]

@dataclass
class FederatedLearningResponse:
    """Response from federated learning training"""
    model_updated: bool
    training_round: int
    model_accuracy: float
    participants: int