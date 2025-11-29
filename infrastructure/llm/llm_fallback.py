"""LLM provider with automatic fallback."""

import os
from typing import Optional
from .llm_provider import LLMProvider, DeepSeekProvider, GeminiProvider, OpenAIProvider


class FallbackLLMProvider(LLMProvider):
    """LLM provider with automatic fallback to backup providers."""
    
    def __init__(self):
        """Initialize with fallback chain."""
        self.primary_provider: Optional[LLMProvider] = None
        self.fallback_providers: list[LLMProvider] = []
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize providers in priority order."""
        # Load from .env file explicitly
        from dotenv import load_dotenv
        load_dotenv()
        
        deepseek_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        google_key = os.getenv("GOOGLE_API_KEY", "").strip()
        openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        
        # Primary: DeepSeek (if available)
        if deepseek_key and deepseek_key != "your_deepseek_api_key_here" and len(deepseek_key) > 10:
            try:
                self.primary_provider = DeepSeekProvider()
                print(f"[LLM] Using DeepSeek as primary provider")
            except Exception as e:
                print(f"[LLM] DeepSeek initialization failed: {str(e)[:100]}")
        
        # Fallbacks
        if google_key and google_key != "your_google_api_key_here" and len(google_key) > 10:
            try:
                self.fallback_providers.append(GeminiProvider())
                print(f"[LLM] Added Google Gemini as fallback")
            except Exception as e:
                print(f"[LLM] Gemini initialization failed: {str(e)[:100]}")
        
        if openai_key and openai_key != "your_openai_api_key_here" and len(openai_key) > 10:
            try:
                self.fallback_providers.append(OpenAIProvider())
                print(f"[LLM] Added OpenAI as fallback")
            except Exception as e:
                print(f"[LLM] OpenAI initialization failed: {str(e)[:100]}")
        
        if not self.primary_provider and not self.fallback_providers:
            raise ValueError(
                f"No valid LLM provider configured. "
                f"DeepSeek: {'set' if deepseek_key else 'not set'}, "
                f"Google: {'set' if google_key else 'not set'}, "
                f"OpenAI: {'set' if openai_key else 'not set'}. "
                f"Please set at least one valid API key in .env file."
            )
    
    def get_chat_model(self):
        """Get the primary chat model."""
        if self.primary_provider:
            return self.primary_provider.get_chat_model()
        elif self.fallback_providers:
            return self.fallback_providers[0].get_chat_model()
        raise ValueError("No LLM provider available")
    
    async def generate_response(
        self,
        messages: list,
        system_prompt: Optional[str] = None,
        temperature: float = 0.8
    ) -> str:
        """Generate response with automatic fallback."""
        # Try primary provider first
        if self.primary_provider:
            try:
                return await self.primary_provider.generate_response(
                    messages, system_prompt, temperature
                )
            except Exception as e:
                error_str = str(e)
                print(f"[Fallback] Primary provider failed: {error_str[:150]}")
                
                # Try fallback providers for ANY error from primary
                if self.fallback_providers:
                    print(f"[Fallback] Trying {len(self.fallback_providers)} fallback provider(s)...")
                    for i, fallback in enumerate(self.fallback_providers):
                        try:
                            print(f"[Fallback] Attempting fallback {i+1}: {type(fallback).__name__}")
                            result = await fallback.generate_response(
                                messages, system_prompt, temperature
                            )
                            print(f"[Fallback] ✓ Fallback {i+1} succeeded!")
                            return result
                        except Exception as fallback_error:
                            print(f"[Fallback] ✗ Fallback {i+1} failed: {str(fallback_error)[:150]}")
                            continue
                    
                    # All fallbacks failed
                    raise ValueError(
                        f"Primary provider failed ({error_str[:100]}) and all {len(self.fallback_providers)} fallback(s) failed. "
                        "Please check your API keys and account balance."
                    )
                else:
                    # No fallbacks available
                    raise ValueError(
                        f"Primary provider failed ({error_str[:100]}) and no fallback available. "
                        "Please add credits or configure a fallback provider."
                    )
        
        # If no primary, try fallbacks
        for fallback in self.fallback_providers:
            try:
                return await fallback.generate_response(
                    messages, system_prompt, temperature
                )
            except:
                continue
        
        raise ValueError("All LLM providers failed")

