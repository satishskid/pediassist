"""
LLM Provider Management for BYOK Support

Manages multiple LLM providers and API configurations for Bring Your Own Key model.
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import structlog

from ..config import settings

logger = structlog.get_logger()

@dataclass
class ProviderConfig:
    """Configuration for an LLM provider"""
    name: str
    display_name: str
    models: List[str]
    api_key_env_var: str
    base_url_env_var: Optional[str] = None
    supports_streaming: bool = True
    supports_json_mode: bool = True
    cost_per_1k_tokens: float = 0.01  # Default cost estimate

class ProviderManager:
    """Manages LLM provider configurations and API keys"""
    
    def __init__(self, config=None):
        self.config = config or settings
        self._providers = self._initialize_providers()
        self._active_provider = settings.llm_provider
    
    def _initialize_providers(self) -> Dict[str, ProviderConfig]:
        """Initialize supported providers with their configurations"""
        providers = {
            "openai": ProviderConfig(
                name="openai",
                display_name="OpenAI",
                models=["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                api_key_env_var="OPENAI_API_KEY",
                cost_per_1k_tokens=0.03
            ),
            "anthropic": ProviderConfig(
                name="anthropic",
                display_name="Anthropic",
                models=["claude-3-sonnet", "claude-3-haiku", "claude-3-opus"],
                api_key_env_var="ANTHROPIC_API_KEY",
                cost_per_1k_tokens=0.025
            ),
            "azure_openai": ProviderConfig(
                name="azure_openai",
                display_name="Azure OpenAI",
                models=["gpt-4", "gpt-35-turbo"],
                api_key_env_var="AZURE_OPENAI_API_KEY",
                base_url_env_var="AZURE_OPENAI_ENDPOINT",
                cost_per_1k_tokens=0.035
            ),
            "google": ProviderConfig(
                name="google",
                display_name="Google AI",
                models=["gemini-pro", "gemini-pro-vision"],
                api_key_env_var="GOOGLE_API_KEY",
                cost_per_1k_tokens=0.02
            ),
            "ollama": ProviderConfig(
                name="ollama",
                display_name="Ollama (Local)",
                models=["llama2", "mistral", "codellama", "phi"],
                api_key_env_var="OLLAMA_API_KEY",  # Usually not required for local
                base_url_env_var="OLLAMA_BASE_URL",
                cost_per_1k_tokens=0.0,  # Free local model
                supports_streaming=True,
                supports_json_mode=False  # Some local models may not support JSON mode
            ),
            "local": ProviderConfig(
                name="local",
                display_name="Local LLM",
                models=["local-model"],
                api_key_env_var="LOCAL_LLM_API_KEY",
                base_url_env_var="LOCAL_LLM_BASE_URL",
                cost_per_1k_tokens=0.0,
                supports_streaming=True,
                supports_json_mode=False
            )
        }
        
        return providers
    
    def get_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """Get configuration for a specific provider"""
        if provider_name not in self._providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        provider = self._providers[provider_name]
        
        # Build configuration dictionary
        config = {
            "name": provider.name,
            "display_name": provider.display_name,
            "models": provider.models,
            "supports_streaming": provider.supports_streaming,
            "supports_json_mode": provider.supports_json_mode,
            "cost_per_1k_tokens": provider.cost_per_1k_tokens
        }
        
        # Add API key if available
        api_key = self._get_api_key(provider.api_key_env_var)
        if api_key:
            config["api_key"] = api_key
        
        # Add base URL if available
        if provider.base_url_env_var:
            base_url = os.getenv(provider.base_url_env_var)
            if base_url:
                config["base_url"] = base_url
        
        # Add provider-specific configurations
        if provider_name == "azure_openai":
            config.update(self._get_azure_config())
        elif provider_name == "ollama":
            config.update(self._get_ollama_config())
        
        return config
    
    def _get_api_key(self, env_var: str) -> Optional[str]:
        """Get API key from environment or config"""
        # Try environment variable first
        api_key = os.getenv(env_var)
        if api_key:
            return api_key
        
        # Try config's encrypted API key
        if hasattr(self.config.llm, 'api_key') and self.config.llm.api_key:
            try:
                # Decrypt API key if encrypted
                if hasattr(self.config, 'decrypt_api_key'):
                    return self.config.decrypt_api_key(self.config.llm.api_key)
                return self.config.llm.api_key
            except Exception as e:
                logger.warning(f"Failed to decrypt API key for {env_var}: {e}")
        
        return None
    
    def _get_azure_config(self) -> Dict[str, Any]:
        """Get Azure OpenAI specific configuration"""
        return {
            "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview"),
            "deployment_name": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
            "api_type": "azure"
        }
    
    def _get_ollama_config(self) -> Dict[str, Any]:
        """Get Ollama specific configuration"""
        return {
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            "default_model": os.getenv("OLLAMA_DEFAULT_MODEL", "llama2")
        }
    
    def validate_provider(self, provider_name: str) -> bool:
        """Validate that a provider is properly configured"""
        if provider_name not in self._providers:
            return False
        
        provider = self._providers[provider_name]
        
        # Check if API key is available (not required for local providers)
        if provider_name not in ["ollama", "local"]:
            api_key = self._get_api_key(provider.api_key_env_var)
            if not api_key:
                logger.warning(f"No API key configured for {provider_name}")
                return False
        
        return True
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of available providers with their status"""
        available = []
        
        for provider_name, provider in self._providers.items():
            is_configured = self.validate_provider(provider_name)
            
            available.append({
                "name": provider.name,
                "display_name": provider.display_name,
                "models": provider.models,
                "is_configured": is_configured,
                "supports_streaming": provider.supports_streaming,
                "supports_json_mode": provider.supports_json_mode,
                "cost_per_1k_tokens": provider.cost_per_1k_tokens,
                "api_key_status": "configured" if is_configured else "missing",
                "base_url": self._get_base_url(provider)
            })
        
        return available
    
    def _get_base_url(self, provider: ProviderConfig) -> Optional[str]:
        """Get base URL for provider"""
        if provider.base_url_env_var:
            return os.getenv(provider.base_url_env_var)
        return None
    
    def set_active_provider(self, provider_name: str) -> bool:
        """Set the active provider"""
        if not self.validate_provider(provider_name):
            logger.error(f"Cannot set active provider - {provider_name} not configured")
            return False
        
        self._active_provider = provider_name
        logger.info(f"Active provider set to {provider_name}")
        return True
    
    def get_active_provider(self) -> str:
        """Get currently active provider"""
        return self._active_provider
    
    def get_provider_cost_estimate(self, provider_name: str, tokens: int) -> float:
        """Get cost estimate for using a provider"""
        if provider_name not in self._providers:
            return 0.0
        
        provider = self._providers[provider_name]
        return (tokens / 1000) * provider.cost_per_1k_tokens
    
    def get_cheapest_provider_for_model(self, model: str) -> Optional[str]:
        """Get the cheapest provider that supports a specific model"""
        cheapest_provider = None
        lowest_cost = float('inf')
        
        for provider_name, provider in self._providers.items():
            if model in provider.models and provider.cost_per_1k_tokens < lowest_cost:
                if self.validate_provider(provider_name):
                    cheapest_provider = provider_name
                    lowest_cost = provider.cost_per_1k_tokens
        
        return cheapest_provider
    
    def test_provider_connection(self, provider_name: str) -> Dict[str, Any]:
        """Test connection to a specific provider"""
        if provider_name not in self._providers:
            return {
                "status": "error",
                "message": f"Unknown provider: {provider_name}"
            }
        
        if not self.validate_provider(provider_name):
            return {
                "status": "error",
                "message": f"Provider {provider_name} not properly configured"
            }
        
        # For local providers, just check if service is running
        if provider_name in ["ollama", "local"]:
            import requests
            try:
                config = self.get_provider_config(provider_name)
                base_url = config.get("base_url", "http://localhost:11434")
                
                if provider_name == "ollama":
                    response = requests.get(f"{base_url}/api/tags", timeout=5)
                    if response.status_code == 200:
                        return {
                            "status": "success",
                            "message": f"{provider_name} service is running",
                            "models": response.json().get("models", [])
                        }
                
                return {
                    "status": "success",
                    "message": f"{provider_name} configured successfully"
                }
                
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to connect to {provider_name}: {str(e)}"
                }
        
        # For cloud providers, we'll need to make an actual API call
        return {
            "status": "warning",
            "message": f"Connection test for {provider_name} requires API call (not implemented)"
        }
    
    def get_setup_instructions(self, provider_name: str) -> str:
        """Get setup instructions for a provider"""
        if provider_name not in self._providers:
            return f"Unknown provider: {provider_name}"
        
        provider = self._providers[provider_name]
        
        instructions = f"""
Setup Instructions for {provider.display_name}:

1. API Key Configuration:
   Set the environment variable: {provider.api_key_env_var}
   Example: export {provider.api_key_env_var}=your-api-key-here

2. Supported Models:
   {', '.join(provider.models)}

3. Cost Estimate:
   ${provider.cost_per_1k_tokens:.3f} per 1,000 tokens
"""
        
        if provider.base_url_env_var:
            instructions += f"""
4. Base URL (if using custom endpoint):
   Set the environment variable: {provider.base_url_env_var}
   Example: export {provider.base_url_env_var}=https://your-custom-endpoint.com
"""
        
        if provider_name == "azure_openai":
            instructions += """
5. Azure Specific:
   - AZURE_OPENAI_API_VERSION: API version (default: 2023-12-01-preview)
   - AZURE_OPENAI_DEPLOYMENT_NAME: Your deployment name
"""
        elif provider_name == "ollama":
            instructions += """
5. Ollama Setup:
   - Install Ollama: https://ollama.ai
   - Start Ollama service: ollama serve
   - Pull models: ollama pull llama2
   - Default URL: http://localhost:11434
"""
        
        return instructions.strip()