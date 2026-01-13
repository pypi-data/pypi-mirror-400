# Oneliac Python SDK

[![PyPI version](https://badge.fury.io/py/oneliac.svg)](https://badge.fury.io/py/oneliac)
[![Python Support](https://img.shields.io/pypi/pyversions/oneliac.svg)](https://pypi.org/project/oneliac/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A Python client library for the Privacy-Preserving Healthcare Agents API. Enables secure medical data analysis with zero-knowledge proofs and federated learning.

## 🚀 Features

- **🔐 Zero-Knowledge Proofs**: Patient privacy guaranteed mathematically
- **🏥 Eligibility Verification**: Check insurance coverage without exposing data
- **💊 Prescription Validation**: Verify drug safety with encrypted medical history
- **🤖 Federated Learning**: Participate in collaborative AI training
- **⛓️ Blockchain Integration**: Solana-based proof verification
- **🔒 HIPAA Compliant**: Meets healthcare privacy standards

## 📦 Installation

```bash
pip install oneliac
```

## 🔧 Quick Start

### Async Usage (Recommended)

```python
import asyncio
from oneliac import HealthcareAgentsClient, PatientData, EligibilityRequest

async def main():
    # Initialize client
    async with HealthcareAgentsClient("https://healthcare-agents-api.onrender.com") as client:
        
        # Check API health
        health = await client.health_check()
        print(f"API Status: {health['status']}")
        
        # Create patient data
        patient_data = PatientData.create(
            patient_id="PATIENT_001",
            raw_data={
                "age": 45,
                "insurance_id": "INS123456",
                "medical_conditions": ["diabetes", "hypertension"]
            }
        )
        
        # Check eligibility
        eligibility_request = EligibilityRequest(
            patient_data=patient_data,
            procedure_code="PROC001"
        )
        
        result = await client.verify_eligibility(eligibility_request)
        print(f"Eligible: {result['eligible']}")
        print(f"Coverage: {result['coverage_percentage']}%")

# Run async function
asyncio.run(main())
```

### Synchronous Usage

```python
from oneliac import HealthcareAgentsClientSync, PatientData, EligibilityRequest

# Initialize sync client
client = HealthcareAgentsClientSync("https://healthcare-agents-api.onrender.com")

# Check API health
health = client.health_check()
print(f"API Status: {health['status']}")

# Create patient data
patient_data = PatientData.create(
    patient_id="PATIENT_001",
    raw_data={
        "age": 45,
        "insurance_id": "INS123456",
        "medical_conditions": ["diabetes", "hypertension"]
    }
)

# Check eligibility
eligibility_request = EligibilityRequest(
    patient_data=patient_data,
    procedure_code="PROC001"
)

result = client.verify_eligibility(eligibility_request)
print(f"Eligible: {result['eligible']}")
```

## 📚 API Reference

### Client Initialization

```python
# Async client
client = HealthcareAgentsClient(
    base_url="https://healthcare-agents-api.onrender.com",
    api_key="your-api-key",  # Optional
    timeout=30  # Request timeout in seconds
)

# Sync client
client = HealthcareAgentsClientSync(
    base_url="https://healthcare-agents-api.onrender.com",
    api_key="your-api-key",  # Optional
    timeout=30
)
```

### Eligibility Verification

```python
from healthcare_agents import EligibilityRequest, PatientData

# Create request
request = EligibilityRequest(
    patient_data=patient_data,
    procedure_code="PROC001"  # Medical procedure code
)

# Verify eligibility
result = await client.verify_eligibility(request)
# Returns: {"eligible": bool, "coverage_percentage": float, "zk_proof_hash": str}
```

### Prescription Validation

```python
from healthcare_agents import PrescriptionRequest

# Create request
request = PrescriptionRequest(
    patient_data=patient_data,
    drug_code="DRUG001"  # Drug identifier
)

# Validate prescription
result = await client.validate_prescription(request)
# Returns: {"safe": bool, "interactions": list, "confidence": float}
```

### Federated Learning

```python
from healthcare_agents import FederatedLearningRequest

# Create request with multiple patient datasets
request = FederatedLearningRequest(
    patient_datasets=[patient_data1, patient_data2, patient_data3]
)

# Participate in training
result = await client.federated_learning_train(request)
# Returns: {"model_updated": bool, "training_round": int, "model_accuracy": float}

# Check FL status
status = await client.federated_learning_status()
# Returns: {"active_agents": int, "training_rounds": int, "model_accuracy": float}
```

## 🔐 Privacy & Security

### Data Encryption

```python
# Patient data is automatically encrypted
patient_data = PatientData.create(
    patient_id="PATIENT_001",
    raw_data={
        "ssn": "123-45-6789",  # Sensitive data
        "medical_history": ["surgery_2020", "allergy_penicillin"]
    }
)

# Raw data is encrypted before API calls
print(patient_data.encrypted_data)  # Base64 encoded encrypted data
print(patient_data.data_hash)       # SHA256 hash for verification
```

### Zero-Knowledge Proofs

All eligibility and prescription validations use zero-knowledge proofs:

```python
result = await client.verify_eligibility(request)

# ZK proof hash verifies the computation without revealing data
zk_proof = result['zk_proof_hash']
print(f"ZK Proof: {zk_proof}")  # Cryptographic proof of eligibility
```

## 🏥 Healthcare Use Cases

### Hospital Integration

```python
class HospitalSystem:
    def __init__(self):
        self.client = HealthcareAgentsClientSync("https://your-api.onrender.com")
    
    def check_patient_eligibility(self, patient_id: str, procedure: str):
        """Check if patient is eligible for procedure"""
        patient_data = self.get_patient_data(patient_id)
        request = EligibilityRequest(patient_data, procedure)
        return self.client.verify_eligibility(request)
    
    def validate_prescription(self, patient_id: str, drug_code: str):
        """Validate prescription safety"""
        patient_data = self.get_patient_data(patient_id)
        request = PrescriptionRequest(patient_data, drug_code)
        return self.client.validate_prescription(request)
```

### Pharmacy Integration

```python
class PharmacySystem:
    def __init__(self):
        self.client = HealthcareAgentsClientSync("https://your-api.onrender.com")
    
    def dispense_medication(self, patient_id: str, drug_code: str):
        """Check safety before dispensing"""
        patient_data = self.get_patient_data(patient_id)
        request = PrescriptionRequest(patient_data, drug_code)
        
        result = self.client.validate_prescription(request)
        
        if result['safe']:
            return self.dispense_drug(drug_code)
        else:
            return {"error": "Prescription validation failed", "warnings": result['warnings']}
```

## 🔧 Error Handling

```python
from healthcare_agents.exceptions import APIError, ValidationError

try:
    result = await client.verify_eligibility(request)
except APIError as e:
    print(f"API Error: {e}")
    print(f"Status Code: {e.status_code}")
except ValidationError as e:
    print(f"Validation Error: {e}")
except Exception as e:
    print(f"Unexpected Error: {e}")
```

## 🧪 Testing

```bash
# Install development dependencies
pip install healthcare-agents[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=healthcare_agents
```

## 📖 Documentation

- **API Documentation**: [https://healthcare-agents-api.onrender.com/docs](https://healthcare-agents-api.onrender.com/docs)
- **SDK Documentation**: [https://healthcare-agents-sdk.readthedocs.io/](https://healthcare-agents-sdk.readthedocs.io/)
- **GitHub Repository**: [https://github.com/razaahmad9222/healthcare-agents-sdk-python](https://github.com/razaahmad9222/healthcare-agents-sdk-python)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Run tests: `pytest`
5. Submit a pull request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/razaahmad9222/healthcare-agents-sdk-python/issues)
- **Discussions**: [GitHub Discussions](https://github.com/razaahmad9222/healthcare-agents-sdk-python/discussions)
- **Email**: raza@healthcare-agents.com

---

**Built with ❤️ for privacy-preserving healthcare**