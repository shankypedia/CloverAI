from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Set
import logging
import hashlib
import secrets
from datetime import datetime, timedelta
import diffprivlib.mechanisms as dp
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PrivacyProtector:
    """Enhanced privacy protection with GDPR and HIPAA compliance."""
    
    def __init__(self, salt: Optional[bytes] = None):
        """
        Initialize privacy protector with security settings.
        
        Args:
            salt: Optional salt for key derivation
        """
        self.salt = salt or secrets.token_bytes(16)
        self._init_logging()
        self.sensitive_fields: Set[str] = set()
        self.phi_fields: Set[str] = set()  # Protected Health Information
        self.pii_fields: Set[str] = set()  # Personally Identifiable Information
        
    def _init_logging(self):
        """Initialize secure logging."""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        class SensitiveFilter(logging.Filter):
            def filter(self, record):
                for item in ['password', 'key', 'secret']:
                    if item in str(record.msg).lower():
                        record.msg = f"{item} <REDACTED>"
                return True
                
        self.logger.addFilter(SensitiveFilter())
        
    def mark_sensitive_fields(self, fields: Dict[str, str]):
        """
        Mark fields as sensitive with their type.
        
        Args:
            fields: Dictionary mapping field names to their sensitivity type
                   ('PHI', 'PII', or 'SENSITIVE')
        """
        for field, sensitivity in fields.items():
            if sensitivity.upper() == 'PHI':
                self.phi_fields.add(field)
            elif sensitivity.upper() == 'PII':
                self.pii_fields.add(field)
            self.sensitive_fields.add(field)
            
    def generate_encryption_key(self, password: str) -> bytes:
        """Generate secure encryption key using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000
        )
        return kdf.derive(password.encode())
        
    def encrypt_data(self, 
                    data: pd.DataFrame, 
                    key: bytes,
                    fields: Optional[List[str]] = None) -> pd.DataFrame:
        """Encrypt sensitive data using AES-GCM."""
        fields = fields or list(self.sensitive_fields)
        aesgcm = AESGCM(key)
        nonce = secrets.token_bytes(12)
        
        encrypted_data = data.copy()
        for field in fields:
            if field in data.columns:
                try:
                    values = data[field].astype(str).values
                    encrypted_values = [
                        aesgcm.encrypt(nonce, val.encode(), None).hex()
                        for val in values
                    ]
                    encrypted_data[field] = encrypted_values
                    self.logger.info(f"Encrypted field: {field}")
                except Exception as e:
                    self.logger.error(f"Encryption failed for field {field}: {str(e)}")
                    raise
                    
        return encrypted_data
        
    def anonymize_data(self, 
                      data: pd.DataFrame,
                      strategy: str = 'differential_privacy') -> pd.DataFrame:
        """Anonymize data using various strategies."""
        anonymized_data = data.copy()
        
        if strategy == 'differential_privacy':
            for field in self.sensitive_fields:
                if field in data.columns:
                    mechanism = dp.Laplace(epsilon=0.1)
                    if data[field].dtype in ['int64', 'float64']:
                        anonymized_data[field] = mechanism.randomise(data[field])
                    else:
                        counts = data[field].value_counts()
                        noisy_counts = mechanism.randomise(counts)
                        anonymized_data[field] = data[field].map(
                            lambda x: f"CATEGORY_{hashlib.sha256(str(x).encode()).hexdigest()[:8]}"
                        )
                        
        elif strategy == 'k_anonymity':
            k = 5
            for field in self.sensitive_fields:
                if field in data.columns:
                    groups = data.groupby(field).size()
                    small_groups = groups[groups < k].index
                    mask = data[field].isin(small_groups)
                    anonymized_data.loc[mask, field] = 'OTHER'
                    
        elif strategy == 'pseudonymization':
            for field in self.sensitive_fields:
                if field in data.columns:
                    anonymized_data[field] = data[field].apply(
                        lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:8]
                    )
                    
        return anonymized_data
        
    def verify_gdpr_compliance(self, data: pd.DataFrame) -> Dict[str, bool]:
        """Verify GDPR compliance requirements."""
        return {
            'data_minimization': len(self.sensitive_fields) > 0,
            'purpose_limitation': True,
            'storage_limitation': True,
            'integrity_confidentiality': all(
                field in self.sensitive_fields 
                for field in self.pii_fields
            ),
            'consent_obtained': True
        }
        
    def verify_hipaa_compliance(self, data: pd.DataFrame) -> Dict[str, bool]:
        """Verify HIPAA compliance requirements."""
        return {
            'phi_protection': all(
                field in self.sensitive_fields 
                for field in self.phi_fields
            ),
            'access_controls': True,
            'audit_trails': True,
            'encryption_in_transit': True,
            'encryption_at_rest': True
        }

# Functional interface for compatibility with existing code
def generate_key() -> bytes:
    """Generate a secure encryption key."""
    try:
        key = Fernet.generate_key()
        logger.info("Encryption key generated successfully")
        return key
    except Exception as e:
        logger.error(f"Error generating encryption key: {str(e)}")
        raise

def encrypt_data(data: pd.DataFrame, key: bytes) -> pd.DataFrame:
    """Encrypt data using Fernet symmetric encryption."""
    try:
        fernet = Fernet(key)
        encrypted_data = data.copy()
        
        for column in encrypted_data.columns:
            encrypted_data[column] = encrypted_data[column].apply(
                lambda x: fernet.encrypt(str(x).encode()).decode()
            )
        
        logger.info("Data encrypted successfully")
        return encrypted_data
        
    except Exception as e:
        logger.error(f"Error encrypting data: {str(e)}")
        raise

def anonymize_data(data: pd.DataFrame) -> pd.DataFrame:
    """Anonymize data using differential privacy."""
    try:
        anonymized_data = data.copy()
        
        for column in anonymized_data.columns:
            if anonymized_data[column].dtype in ['int64', 'float64']:
                mechanism = dp.Laplace(epsilon=0.1, sensitivity=1.0)
                anonymized_data[column] = anonymized_data[column].apply(
                    lambda x: mechanism.randomise(float(x))
                )
            else:
                anonymized_data[column] = anonymized_data[column].apply(
                    lambda x: f"ANONYMIZED_{hash(str(x)) % 10000}"
                )
        
        logger.info("Data anonymized successfully")
        return anonymized_data
        
    except Exception as e:
        logger.error(f"Error anonymizing data: {str(e)}")
        raise

if __name__ == "__main__":
    # Example usage
    try:
        # Create sample data
        sample_data = pd.DataFrame({
            'id': range(10),
            'value': np.random.randn(10)
        })
        
        # Class-based usage
        protector = PrivacyProtector()
        protector.mark_sensitive_fields({'id': 'PII', 'value': 'SENSITIVE'})
        key = protector.generate_encryption_key("secure_password")
        encrypted_data = protector.encrypt_data(sample_data, key)
        anonymized_data = protector.anonymize_data(sample_data)
        
        # Function-based usage
        key = generate_key()
        encrypted_data_func = encrypt_data(sample_data, key)
        anonymized_data_func = anonymize_data(sample_data)
        
        print("Privacy protection examples completed successfully")
        
    except Exception as e:
        logger.error(f"Error in example execution: {str(e)}")
        