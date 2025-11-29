"""LLM provider factory (Factory Pattern)."""

import os
from typing import Optional

from .llm_provider import LLMProvider, DeepSeekProvider, GeminiProvider, OpenAIProvider
from .llm_fallback import FallbackLLMProvider


def create_llm_provider(provider_name: Optional[str] = None, use_fallback: bool = True) -> LLMProvider:
    """
    Create LLM provider based on environment or parameter.
    
    Priority:
    1. provider_name parameter
    2. LLM_PROVIDER env var
    3. Auto-detect with fallback (if use_fallback=True)
    4. Auto-detect without fallback
    
    Args:
        provider_name: Specific provider to use ("deepseek", "gemini", "openai")
        use_fallback: If True, use FallbackLLMProvider for automatic fallback
    """
    provider_name = provider_name or os.getenv("LLM_PROVIDER", "").lower()
    
    # If use_fallback and no specific provider, use fallback system
    if use_fallback and not provider_name:
        try:
            return FallbackLLMProvider()
        except Exception as e:
            # If fallback fails, continue to single provider selection
            pass
    
    # Try to auto-detect if not specified
    if not provider_name:
        deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")
        google_key = os.getenv("GOOGLE_API_KEY", "")
        openai_key = os.getenv("OPENAI_API_KEY", "")
        
        # Check for valid keys (not placeholders)
        # Priority: DeepSeek > Google > OpenAI
        if deepseek_key and deepseek_key != "your_deepseek_api_key_here" and len(deepseek_key) > 10:
            provider_name = "deepseek"
        elif google_key and google_key != "your_google_api_key_here" and len(google_key) > 10:
            provider_name = "gemini"
        elif openai_key and openai_key != "your_openai_api_key_here" and len(openai_key) > 10:
            provider_name = "openai"
        else:
            raise ValueError(
                "No valid LLM provider configured. Please set one of: "
                "DEEPSEEK_API_KEY, GOOGLE_API_KEY, or OPENAI_API_KEY in .env file"
            )
    
    provider_name = provider_name.lower()
    
    if provider_name == "deepseek":
        return DeepSeekProvider()
    elif provider_name == "gemini":
        return GeminiProvider()
    elif provider_name == "openai":
        return OpenAIProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}")

