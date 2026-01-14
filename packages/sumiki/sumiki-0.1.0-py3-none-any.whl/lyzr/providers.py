"""
Provider and model definitions for Lyzr Agent API using Pydantic
"""

from typing import Dict, List, Tuple, Optional, Literal, Any
from pydantic import BaseModel, Field, validator, ConfigDict
from enum import Enum


class ProviderName(str, Enum):
    """Supported provider names"""
    OPENAI = "OpenAI"
    ANTHROPIC = "Anthropic"
    GOOGLE = "Google"
    GROQ = "Groq"
    PERPLEXITY = "Perplexity"
    AWS_BEDROCK = "Aws-Bedrock"


class ModelInfo(BaseModel):
    """Information about a specific model"""
    name: str = Field(..., description="Model name")
    capability_score: int = Field(..., ge=1, le=5, description="Model capability (1-5)")
    speed_score: int = Field(..., ge=1, le=5, description="Model speed (1-5)")
    context_window: int = Field(..., gt=0, description="Context window size")
    model_type: Optional[str] = Field(None, description="Model type (e.g., 'Reasoning')")
    additional_params: Optional[Dict[str, Any]] = Field(None, description="Additional model-specific parameters")

    model_config = ConfigDict(frozen=True)


class Provider(BaseModel):
    """Provider configuration"""
    provider_id: ProviderName = Field(..., description="Provider identifier")
    credential_id: str = Field(..., description="Credential ID for API access")
    display_name: str = Field(..., description="Display name")
    models: Dict[str, ModelInfo] = Field(default_factory=dict, description="Available models")

    model_config = ConfigDict(frozen=True)


# Define all providers with Pydantic models
_PROVIDERS_DATA: Dict[ProviderName, Provider] = {
    ProviderName.OPENAI: Provider(
        provider_id=ProviderName.OPENAI,
        credential_id="lyzr_openai",
        display_name="OpenAI",
        models={
            "gpt-4o": ModelInfo(name="gpt-4o", capability_score=4, speed_score=4, context_window=128000),
            "gpt-4o-mini": ModelInfo(name="gpt-4o-mini", capability_score=2, speed_score=5, context_window=128000),
            "o4-mini": ModelInfo(name="o4-mini", capability_score=2, speed_score=5, context_window=128000, model_type="Reasoning"),
            "gpt-4.1": ModelInfo(name="gpt-4.1", capability_score=5, speed_score=3, context_window=1000000),
            "o3": ModelInfo(name="o3", capability_score=3, speed_score=4, context_window=128000, model_type="Reasoning"),
            "gpt-5": ModelInfo(name="gpt-5", capability_score=4, speed_score=2, context_window=400000, model_type="Reasoning"),
            "gpt-5-mini": ModelInfo(name="gpt-5-mini", capability_score=2, speed_score=4, context_window=400000, model_type="Reasoning"),
            "gpt-5-nano": ModelInfo(name="gpt-5-nano", capability_score=1, speed_score=5, context_window=400000, model_type="Reasoning"),
            "gpt-5.1": ModelInfo(name="gpt-5.1", capability_score=4, speed_score=2, context_window=400000, model_type="Reasoning"),
            "gpt-5.2": ModelInfo(name="gpt-5.2", capability_score=5, speed_score=2, context_window=400000, model_type="Reasoning"),
        }
    ),
    ProviderName.ANTHROPIC: Provider(
        provider_id=ProviderName.ANTHROPIC,
        credential_id="lyzr_anthropic",
        display_name="Anthropic",
        models={
            "claude-3-7-sonnet-latest": ModelInfo(name="claude-3-7-sonnet-latest", capability_score=4, speed_score=4, context_window=200000),
            "claude-3-5-haiku-latest": ModelInfo(name="claude-3-5-haiku-latest", capability_score=3, speed_score=5, context_window=200000),
            "claude-sonnet-4-0": ModelInfo(name="claude-sonnet-4-0", capability_score=4, speed_score=4, context_window=200000),
            "claude-opus-4-0": ModelInfo(name="claude-opus-4-0", capability_score=5, speed_score=3, context_window=200000, model_type="Reasoning"),
            "claude-opus-4-1": ModelInfo(name="claude-opus-4-1", capability_score=5, speed_score=3, context_window=200000, model_type="Reasoning"),
            "claude-sonnet-4-5": ModelInfo(name="claude-sonnet-4-5", capability_score=4, speed_score=4, context_window=200000),
            "claude-opus-4-5": ModelInfo(name="claude-opus-4-5", capability_score=4, speed_score=3, context_window=200000, model_type="Reasoning"),
        }
    ),
    ProviderName.GOOGLE: Provider(
        provider_id=ProviderName.GOOGLE,
        credential_id="lyzr_google",
        display_name="Google",
        models={
            "gemini-2.0-flash": ModelInfo(name="gemini-2.0-flash", capability_score=3, speed_score=5, context_window=1000000),
            "gemini-2.0-flash-lite": ModelInfo(name="gemini-2.0-flash-lite", capability_score=2, speed_score=5, context_window=1000000),
            "gemini-2.5-pro": ModelInfo(name="gemini-2.5-pro", capability_score=4, speed_score=4, context_window=1000000, model_type="Reasoning"),
            "gemini-2.5-flash": ModelInfo(name="gemini-2.5-flash", capability_score=4, speed_score=4, context_window=1000000, model_type="Reasoning"),
            "gemini-2.5-flash-lite": ModelInfo(name="gemini-2.5-flash-lite", capability_score=2, speed_score=4, context_window=1000000, model_type="Reasoning"),
            "gemini-3-pro-preview": ModelInfo(name="gemini-3-pro-preview", capability_score=5, speed_score=4, context_window=1000000, model_type="Reasoning"),
        }
    ),
    ProviderName.GROQ: Provider(
        provider_id=ProviderName.GROQ,
        credential_id="lyzr_groq",
        display_name="Groq",
        models={
            "llama-3.3-70b-versatile": ModelInfo(name="llama-3.3-70b-versatile", capability_score=2, speed_score=5, context_window=128000),
            "llama-3.1-8b-instant": ModelInfo(name="llama-3.1-8b-instant", capability_score=1, speed_score=5, context_window=128000),
            "llama-4-scout-17b-16e-instruct": ModelInfo(name="llama-4-scout-17b-16e-instruct", capability_score=3, speed_score=5, context_window=131000),
            "llama-4-maverick-17b-128e-instruct": ModelInfo(name="llama-4-maverick-17b-128e-instruct", capability_score=3, speed_score=5, context_window=1000000),
            "gpt-oss-120b": ModelInfo(name="gpt-oss-120b", capability_score=3, speed_score=5, context_window=131072, model_type="Reasoning"),
            "gpt-oss-20b": ModelInfo(name="gpt-oss-20b", capability_score=2, speed_score=5, context_window=131072, model_type="Reasoning"),
            "kimi-k2-instruct": ModelInfo(name="kimi-k2-instruct", capability_score=2, speed_score=4, context_window=256000),
        }
    ),
    ProviderName.PERPLEXITY: Provider(
        provider_id=ProviderName.PERPLEXITY,
        credential_id="lyzr_perplexity",
        display_name="Perplexity",
        models={
            "sonar": ModelInfo(name="sonar", capability_score=2, speed_score=4, context_window=128000),
            "sonar-pro": ModelInfo(name="sonar-pro", capability_score=3, speed_score=3, context_window=128000),
            "sonar-reasoning": ModelInfo(name="sonar-reasoning", capability_score=3, speed_score=4, context_window=128000, model_type="Reasoning"),
            "sonar-reasoning-pro": ModelInfo(name="sonar-reasoning-pro", capability_score=4, speed_score=3, context_window=128000, model_type="Reasoning"),
            "r1-1776": ModelInfo(name="r1-1776", capability_score=2, speed_score=4, context_window=128000),
            "sonar-deep-research": ModelInfo(name="sonar-deep-research", capability_score=4, speed_score=4, context_window=128000, model_type="Reasoning"),
        }
    ),
    ProviderName.AWS_BEDROCK: Provider(
        provider_id=ProviderName.AWS_BEDROCK,
        credential_id="lyzr_aws-bedrock",
        display_name="Amazon Bedrock",
        models={
            "amazon.nova-micro-v1:0": ModelInfo(name="amazon.nova-micro-v1:0", capability_score=1, speed_score=5, context_window=128000),
            "amazon.nova-lite-v1:0": ModelInfo(name="amazon.nova-lite-v1:0", capability_score=2, speed_score=4, context_window=300000),
            "amazon.nova-pro-v1:0": ModelInfo(name="amazon.nova-pro-v1:0", capability_score=3, speed_score=4, context_window=300000),
            "anthropic.claude-3-5-sonnet-20241022-v2:0": ModelInfo(name="anthropic.claude-3-5-sonnet-20241022-v2:0", capability_score=4, speed_score=4, context_window=200000),
            "anthropic.claude-3-7-sonnet-20250219-v1:0": ModelInfo(name="anthropic.claude-3-7-sonnet-20250219-v1:0", capability_score=4, speed_score=4, context_window=200000, model_type="Reasoning"),
            "meta.llama3-3-70b-instruct-v1:0": ModelInfo(name="meta.llama3-3-70b-instruct-v1:0", capability_score=4, speed_score=3, context_window=128000),
            "mistral.mistral-large-2402-v1:0": ModelInfo(name="mistral.mistral-large-2402-v1:0", capability_score=4, speed_score=3, context_window=64000),
        }
    ),
}


class ModelResolver:
    """Resolve model strings to provider and model information"""

    # Provider name aliases for easier parsing
    PROVIDER_ALIASES = {
        'openai': ProviderName.OPENAI,
        'anthropic': ProviderName.ANTHROPIC,
        'google': ProviderName.GOOGLE,
        'gemini': ProviderName.GOOGLE,
        'groq': ProviderName.GROQ,
        'perplexity': ProviderName.PERPLEXITY,
        'aws-bedrock': ProviderName.AWS_BEDROCK,
        'bedrock': ProviderName.AWS_BEDROCK,
        'aws': ProviderName.AWS_BEDROCK,
    }

    @classmethod
    def parse(cls, model_string: str) -> Tuple[ProviderName, str, ModelInfo]:
        """
        Parse model string and return provider, model name, and model info

        Args:
            model_string: String like 'openai/gpt-4o', 'gpt-4o', or 'OpenAI/gpt-4o'

        Returns:
            Tuple of (ProviderName, model_name, ModelInfo)

        Raises:
            ValueError: If provider or model is invalid

        Examples:
            >>> resolver = ModelResolver()
            >>> provider, model, info = resolver.parse('openai/gpt-4o')
            >>> provider
            <ProviderName.OPENAI: 'OpenAI'>
            >>> model
            'gpt-4o'
            >>> info.capability_score
            4
        """
        model_string = model_string.strip()

        if '/' in model_string:
            # Format: 'provider/model'
            provider_str, model_name = model_string.split('/', 1)
            provider_str = provider_str.strip().lower()
            model_name = model_name.strip()

            # Resolve provider
            if provider_str not in cls.PROVIDER_ALIASES:
                raise ValueError(
                    f"Unknown provider: '{provider_str}'. "
                    f"Valid providers: {', '.join(cls.PROVIDER_ALIASES.keys())}"
                )

            provider = cls.PROVIDER_ALIASES[provider_str]

            # Validate model
            provider_data = _PROVIDERS_DATA[provider]
            if model_name not in provider_data.models:
                available = ', '.join(provider_data.models.keys())
                raise ValueError(
                    f"Model '{model_name}' not found in {provider.value}. "
                    f"Available models: {available}"
                )

            return provider, model_name, provider_data.models[model_name]

        else:
            # Format: just 'model' - search all providers
            model_name = model_string

            for provider, provider_data in _PROVIDERS_DATA.items():
                if model_name in provider_data.models:
                    return provider, model_name, provider_data.models[model_name]

            raise ValueError(
                f"Model '{model_name}' not found in any provider. "
                f"Use format 'provider/model' or check available models."
            )

    @classmethod
    def get_provider(cls, provider: ProviderName) -> Provider:
        """Get provider configuration"""
        return _PROVIDERS_DATA[provider]

    @classmethod
    def get_all_providers(cls) -> Dict[ProviderName, Provider]:
        """Get all provider configurations"""
        return _PROVIDERS_DATA.copy()

    @classmethod
    def get_all_models(cls) -> Dict[str, List[str]]:
        """Get all available models grouped by provider display name"""
        return {
            provider_data.display_name: list(provider_data.models.keys())
            for provider_data in _PROVIDERS_DATA.values()
        }

    @classmethod
    def validate_model(cls, provider: ProviderName, model: str) -> bool:
        """Check if model is valid for provider"""
        return model in _PROVIDERS_DATA[provider].models

    @classmethod
    def get_credential_id(cls, provider: ProviderName) -> str:
        """Get credential ID for a provider"""
        return _PROVIDERS_DATA[provider].credential_id


# Convenience function
def parse_model(model_string: str) -> Tuple[ProviderName, str, ModelInfo]:
    """
    Parse a model string into provider, model name, and model info

    Args:
        model_string: Model string like 'openai/gpt-4o' or 'gpt-4o'

    Returns:
        Tuple of (ProviderName, model_name, ModelInfo)

    Examples:
        >>> provider, model, info = parse_model('openai/gpt-4o')
        >>> print(f"{provider.value}/{model}")
        OpenAI/gpt-4o
    """
    return ModelResolver.parse(model_string)
