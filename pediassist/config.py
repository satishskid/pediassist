"""
Configuration management for PediAssist
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    app_name: str = "PediAssist"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://pediassist:password@localhost:5432/pediassist",
        env="DATABASE_URL"
    )
    
    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    
    # LLM Configuration
    llm_provider: str = Field(default="openai", env="LLM_PROVIDER")
    api_key: Optional[str] = Field(default=None, env="API_KEY")
    model: str = Field(default="gpt-4-turbo", env="MODEL")
    max_tokens: int = Field(default=4000, env="MAX_TOKENS")
    temperature: float = Field(default=0.3, env="TEMPERATURE")
    
    # Local LLM (Ollama)
    ollama_url: str = Field(default="http://localhost:11434", env="OLLAMA_URL")
    local_model: str = Field(default="llama3:70b", env="LOCAL_MODEL")
    
    # Security
    secret_key: str = Field(default="your-secret-key-change-this", env="SECRET_KEY")
    encryption_key: Optional[str] = Field(default=None, env="ENCRYPTION_KEY")
    pediasist_encryption_key: Optional[str] = Field(default=None, env="PEDIASIST_ENCRYPTION_KEY")
    pediasist_jwt_secret: Optional[str] = Field(default=None, env="PEDIASIST_JWT_SECRET")
    
    # License
    license_key: Optional[str] = Field(default=None, env="pediasist_license_key")
    
    # Cost Control
    monthly_budget: float = Field(default=100.0, env="MONTHLY_BUDGET")
    token_usage_tracking: bool = Field(default=True, env="TOKEN_USAGE_TRACKING")
    
    # Features
    enable_caching: bool = Field(default=True, env="ENABLE_CACHING")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")  # 1 hour
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Paths
    data_dir: Path = Field(default=Path("data"), env="DATA_DIR")
    logs_dir: Path = Field(default=Path("logs"), env="LOGS_DIR")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"  # Allow extra environment variables

# Global settings instance
settings = Settings()

# Manually set license key if available
import os
if os.getenv('PEDIASIST_LICENSE_KEY'):
    settings.license_key = os.getenv('PEDIASIST_LICENSE_KEY')

def validate_settings() -> bool:
    """Validate critical settings"""
    errors = []
    
    # Check required settings
    if not settings.database_url:
        errors.append("DATABASE_URL is required")
    
    if settings.llm_provider != "local" and not settings.api_key:
        errors.append(f"API_KEY is required for {settings.llm_provider} provider")
    
    if settings.secret_key == "your-secret-key-change-this":
        errors.append("Please change the default SECRET_KEY")
    
    # Create directories
    settings.data_dir.mkdir(exist_ok=True)
    settings.logs_dir.mkdir(exist_ok=True)
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    return True

def get_llm_config() -> Dict[str, Any]:
    """Get LLM configuration based on provider"""
    base_config = {
        "max_tokens": settings.max_tokens,
        "temperature": settings.temperature,
    }
    
    if settings.llm_provider == "local":
        return {
            **base_config,
            "api_base": settings.ollama_url,
            "model": settings.local_model,
        }
    else:
        return {
            **base_config,
            "api_key": settings.api_key,
            "model": settings.model,
        }