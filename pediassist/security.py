"""
Security and License Management for PediAssist
"""

import hashlib
import hmac
import json
import time
import secrets
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import structlog
import jwt
from cryptography.fernet import Fernet
import os

logger = structlog.get_logger(__name__)

class LicenseType(Enum):
    """License types for PediAssist"""
    TRIAL = "trial"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class LicenseStatus(Enum):
    """License status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    INVALID = "invalid"

@dataclass
class LicenseInfo:
    """License information structure"""
    license_key: str
    license_type: LicenseType
    organization_name: str
    user_email: str
    max_users: int
    features: List[str]
    valid_until: datetime
    issued_at: datetime
    status: LicenseStatus
    metadata: Dict[str, Any]

@dataclass
class SecurityConfig:
    """Security configuration"""
    encryption_key: str
    jwt_secret: str
    api_rate_limit: int
    max_login_attempts: int
    session_timeout: int  # minutes
    password_policy: Dict[str, Any]
    audit_log_retention_days: int
    enable_encryption: bool

class LicenseManager:
    """Manages PediAssist licensing and feature access"""
    
    def __init__(self):
        self.license_key = None
        self.license_info = None
        self.security_config = self._load_security_config()
        self.encryption_key = None
        self._initialize_encryption()
    
    def _load_security_config(self) -> SecurityConfig:
        """Load security configuration from environment or defaults"""
        return SecurityConfig(
            encryption_key=os.getenv("PEDIASIST_ENCRYPTION_KEY", self._generate_key()),
            jwt_secret=os.getenv("PEDIASIST_JWT_SECRET", secrets.token_urlsafe(32)),
            api_rate_limit=int(os.getenv("PEDIASIST_API_RATE_LIMIT", "100")),
            max_login_attempts=int(os.getenv("PEDIASIST_MAX_LOGIN_ATTEMPTS", "5")),
            session_timeout=int(os.getenv("PEDIASIST_SESSION_TIMEOUT", "60")),
            password_policy={
                "min_length": 8,
                "require_uppercase": True,
                "require_lowercase": True,
                "require_numbers": True,
                "require_special_chars": True,
                "expiration_days": 90
            },
            audit_log_retention_days=int(os.getenv("PEDIASIST_AUDIT_RETENTION", "365")),
            enable_encryption=os.getenv("PEDIASIST_ENABLE_ENCRYPTION", "true").lower() == "true"
        )
    
    def _generate_key(self) -> str:
        """Generate a secure encryption key"""
        return Fernet.generate_key().decode()
    
    def _initialize_encryption(self):
        """Initialize encryption system"""
        if self.security_config.enable_encryption:
            try:
                self.encryption_key = self.security_config.encryption_key.encode()
                self.cipher_suite = Fernet(self.encryption_key)
            except Exception as e:
                logger.error("Failed to initialize encryption", error=str(e))
                raise
    
    def validate_license_key(self, license_key: str) -> bool:
        """Validate license key format and basic structure"""
        if not license_key:
            return False
        
        # Basic format validation (example format: PA-BASIC-2024-DEMO-KEY or PA-BASIC-XXXX)
        if not license_key.startswith("PA-"):
            return False
        
        parts = license_key.split("-")
        if len(parts) < 2:  # At least "PA" and one more part
            return False
        
        # Check that parts after "PA" are alphanumeric (allowing variable lengths)
        for part in parts[1:]:  # Skip "PA" prefix
            if not part.isalnum():
                return False
        
        return True
    
    def verify_license(self, license_key: str) -> Dict[str, Any]:
        """Verify license key and return license information"""
        try:
            if not self.validate_license_key(license_key):
                return {
                    "valid": False,
                    "status": LicenseStatus.INVALID,
                    "error": "Invalid license key format"
                }
            
            # For BYOK model, validate against provider API keys
            license_info = self._check_byok_license(license_key)
            
            if not license_info:
                return {
                    "valid": False,
                    "status": LicenseStatus.INVALID,
                    "error": "License key not found or invalid"
                }
            
            # Check expiration
            if datetime.utcnow() > license_info.valid_until:
                return {
                    "valid": False,
                    "status": LicenseStatus.EXPIRED,
                    "error": "License has expired",
                    "expired_at": license_info.valid_until.isoformat()
                }
            
            # Check if suspended
            if license_info.status == LicenseStatus.SUSPENDED:
                return {
                    "valid": False,
                    "status": LicenseStatus.SUSPENDED,
                    "error": "License has been suspended"
                }
            
            return {
                "valid": True,
                "status": license_info.status,
                "license_info": asdict(license_info),
                "features": license_info.features
            }
            
        except Exception as e:
            logger.error("License verification failed", error=str(e))
            return {
                "valid": False,
                "status": LicenseStatus.INVALID,
                "error": f"Verification failed: {str(e)}"
            }
    
    def _check_byok_license(self, license_key: str) -> Optional[LicenseInfo]:
        """Check BYOK (Bring Your Own Key) license"""
        # For BYOK model, the license key represents the user's API keys
        # We'll validate that they have configured at least one LLM provider
        
        try:
            # In a real implementation, this would validate against a license server
            # For now, we'll create a basic license info based on the key format
            
            # Parse license key to determine type and features
            license_type = self._determine_license_type(license_key)
            features = self._get_features_for_license_type(license_type)
            
            # Create license info
            license_info = LicenseInfo(
                license_key=license_key,
                license_type=license_type,
                organization_name="BYOK User",
                user_email="user@example.com",
                max_users=self._get_max_users_for_license_type(license_type),
                features=features,
                valid_until=datetime.utcnow() + timedelta(days=365),  # 1 year validity
                issued_at=datetime.utcnow(),
                status=LicenseStatus.ACTIVE,
                metadata={
                    "byok_model": True,
                    "providers_configured": [],
                    "last_validation": datetime.utcnow().isoformat()
                }
            )
            
            return license_info
            
        except Exception as e:
            logger.error("BYOK license check failed", error=str(e))
            return None
    
    def _determine_license_type(self, license_key: str) -> LicenseType:
        """Determine license type from key"""
        # Simple heuristic based on key format
        # In a real system, this would check against a license database
        
        if license_key.startswith("PA-TRIAL"):
            return LicenseType.TRIAL
        elif license_key.startswith("PA-BASIC"):
            return LicenseType.BASIC
        elif license_key.startswith("PA-PRO"):
            return LicenseType.PROFESSIONAL
        elif license_key.startswith("PA-ENT"):
            return LicenseType.ENTERPRISE
        else:
            # Default to basic for BYOK model
            return LicenseType.BASIC
    
    def _get_features_for_license_type(self, license_type: LicenseType) -> List[str]:
        """Get features available for license type"""
        features = {
            LicenseType.TRIAL: [
                "basic_diagnosis",
                "basic_treatment_plans",
                "limited_llm_queries",
                "basic_communication"
            ],
            LicenseType.BASIC: [
                "basic_diagnosis",
                "basic_treatment_plans",
                "limited_llm_queries",
                "basic_communication",
                "patient_education"
            ],
            LicenseType.PROFESSIONAL: [
                "advanced_diagnosis",
                "comprehensive_treatment_plans",
                "unlimited_llm_queries",
                "advanced_communication",
                "patient_education",
                "clinical_decision_support",
                "audit_logging",
                "multi_provider_support"
            ],
            LicenseType.ENTERPRISE: [
                "advanced_diagnosis",
                "comprehensive_treatment_plans",
                "unlimited_llm_queries",
                "advanced_communication",
                "patient_education",
                "clinical_decision_support",
                "audit_logging",
                "multi_provider_support",
                "custom_protocols",
                "integration_apis",
                "priority_support",
                "custom_training"
            ]
        }
        
        return features.get(license_type, features[LicenseType.BASIC])
    
    def _get_max_users_for_license_type(self, license_type: LicenseType) -> int:
        """Get maximum users allowed for license type"""
        limits = {
            LicenseType.TRIAL: 1,
            LicenseType.BASIC: 5,
            LicenseType.PROFESSIONAL: 25,
            LicenseType.ENTERPRISE: -1  # Unlimited
        }
        
        return limits.get(license_type, 1)
    
    def has_feature(self, feature: str) -> bool:
        """Check if current license has specific feature"""
        if not self.license_info:
            return False
        
        return feature in self.license_info.features
    
    def get_usage_limits(self) -> Dict[str, Any]:
        """Get usage limits for current license"""
        if not self.license_info:
            return {
                "llm_queries_daily": 0,
                "patients_daily": 0,
                "users_max": 0,
                "api_calls_daily": 0
            }
        
        limits = {
            LicenseType.TRIAL: {
                "llm_queries_daily": 50,
                "patients_daily": 10,
                "users_max": 1,
                "api_calls_daily": 100
            },
            LicenseType.BASIC: {
                "llm_queries_daily": 200,
                "patients_daily": 50,
                "users_max": 5,
                "api_calls_daily": 500
            },
            LicenseType.PROFESSIONAL: {
                "llm_queries_daily": -1,  # Unlimited
                "patients_daily": -1,     # Unlimited
                "users_max": 25,
                "api_calls_daily": -1    # Unlimited
            },
            LicenseType.ENTERPRISE: {
                "llm_queries_daily": -1,  # Unlimited
                "patients_daily": -1,     # Unlimited
                "users_max": -1,          # Unlimited
                "api_calls_daily": -1    # Unlimited
            }
        }
        
        return limits.get(self.license_info.license_type, limits[LicenseType.BASIC])
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not self.security_config.enable_encryption:
            return data
        
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return encrypted_data.decode()
        except Exception as e:
            logger.error("Encryption failed", error=str(e))
            raise
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not self.security_config.enable_encryption:
            return encrypted_data
        
        try:
            decrypted_data = self.cipher_suite.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
        except Exception as e:
            logger.error("Decryption failed", error=str(e))
            raise
    
    def generate_jwt_token(self, user_id: str, expires_in: int = None) -> str:
        """Generate JWT token for authentication"""
        if expires_in is None:
            expires_in = self.security_config.session_timeout * 60  # Convert minutes to seconds
        
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(seconds=expires_in),
            "iat": datetime.utcnow(),
            "license_type": self.license_info.license_type.value if self.license_info else "trial"
        }
        
        return jwt.encode(payload, self.security_config.jwt_secret, algorithm="HS256")
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.security_config.jwt_secret, algorithms=["HS256"])
            return {
                "valid": True,
                "user_id": payload["user_id"],
                "license_type": payload.get("license_type", "trial")
            }
        except jwt.ExpiredSignatureError:
            return {"valid": False, "error": "Token has expired"}
        except jwt.InvalidTokenError as e:
            return {"valid": False, "error": str(e)}
    
    def create_api_key(self, name: str, user_id: str, expires_days: int = 365) -> str:
        """Create API key for external access"""
        api_key = secrets.token_urlsafe(32)
        
        # Store API key information (in a real system, this would go to a database)
        api_key_info = {
            "key": api_key,
            "name": name,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=expires_days)).isoformat(),
            "last_used": None,
            "active": True
        }
        
        # In a real system, store this in database
        logger.info("API key created", name=name, user_id=user_id)
        
        return api_key
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for HTTP responses"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
    
    def audit_log(self, action: str, user_id: str, details: Dict[str, Any] = None):
        """Log security audit event"""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "user_id": user_id,
            "license_key": self.license_key,
            "details": details or {},
            "ip_address": None,  # Would be passed from request
            "user_agent": None     # Would be passed from request
        }
        
        logger.info("Security audit", **audit_entry)
        
        # In a real system, store this in an audit log database
        # with appropriate retention policies

# Global license manager instance
license_manager = LicenseManager()

def validate_license(license_key: str) -> Dict[str, Any]:
    """Validate license key"""
    return license_manager.verify_license(license_key)

def has_feature(feature: str) -> bool:
    """Check if current license has feature"""
    return license_manager.has_feature(feature)

def get_usage_limits() -> Dict[str, Any]:
    """Get usage limits for current license"""
    return license_manager.get_usage_limits()