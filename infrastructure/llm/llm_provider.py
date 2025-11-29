"""LLM provider interface and implementations."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
import os


class LLMProvider(ABC):
    """LLM provider interface."""
    
    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """Generate response from LLM."""
        pass
    
    @abstractmethod
    def get_chat_model(self) -> BaseChatModel:
        """Get LangChain chat model instance."""
        pass


class DeepSeekProvider(LLMProvider):
    """DeepSeek LLM provider."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize DeepSeek provider."""
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment")
        
        self.base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self._model = None
    
    def get_chat_model(self) -> BaseChatModel:
        """Get DeepSeek chat model."""
        if self._model is None:
            from langchain_openai import ChatOpenAI
            self._model = ChatOpenAI(
                model="deepseek-chat",
                api_key=self.api_key,
                base_url=self.base_url,
                temperature=0.8  # Higher for more natural, conversational responses
            )
        return self._model
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.8
    ) -> str:
        """Generate response using DeepSeek."""
        model = self.get_chat_model()
        if hasattr(model, 'temperature'):
            model.temperature = temperature
        
        langchain_messages = []
        if system_prompt:
            langchain_messages.append(SystemMessage(content=system_prompt))
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
        
        try:
            response = await model.ainvoke(langchain_messages)
            return response.content
        except Exception as e:
            error_str = str(e)
            # If DeepSeek fails due to balance, suggest fallback
            if "402" in error_str or "Insufficient" in error_str or "Balance" in error_str:
                raise ValueError(
                    "DeepSeek API has insufficient balance. Please add credits or use GOOGLE_API_KEY as fallback."
                )
            raise


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini provider."""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        self._model = None
    
    def get_chat_model(self) -> BaseChatModel:
        """Get Gemini chat model."""
        if self._model is None:
            from langchain_google_genai import ChatGoogleGenerativeAI
            # Try different model names that work with the API
            # Based on available models: gemini-2.0-flash, gemini-2.5-flash, gemini-2.5-pro
            model_names_to_try = [
                "gemini-2.0-flash",  # Stable and fast
                "gemini-2.5-flash",  # Latest flash model
                "gemini-2.5-pro",    # Latest pro model
                "gemini-pro",        # Fallback to older name
            ]
            
            last_error = None
            for model_name in model_names_to_try:
                try:
                    self._model = ChatGoogleGenerativeAI(
                        google_api_key=self.api_key,
                        temperature=0.8,
                        model=model_name
                    )
                    # Test if it works by checking if we can get the model
                    print(f"[Gemini] Using model: {model_name}")
                    return self._model
                except Exception as e:
                    last_error = e
                    continue
            
            # If all specific models fail, try without model name (uses default)
            try:
                self._model = ChatGoogleGenerativeAI(
                    google_api_key=self.api_key,
                    temperature=0.8
                )
                print(f"[Gemini] Using default model")
                return self._model
            except Exception as e:
                raise ValueError(f"Could not initialize Gemini model. Last error: {str(e)[:200]}")
        
        return self._model
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """Generate response using Gemini."""
        model = self.get_chat_model()
        model.temperature = temperature
        
        langchain_messages = []
        if system_prompt:
            langchain_messages.append(SystemMessage(content=system_prompt))
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
        
        response = await model.ainvoke(langchain_messages)
        return response.content


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI provider."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        self._model = None
    
    def get_chat_model(self) -> BaseChatModel:
        """Get OpenAI chat model."""
        if self._model is None:
            from langchain_openai import ChatOpenAI
            self._model = ChatOpenAI(
                model="gpt-3.5-turbo",
                api_key=self.api_key,
                temperature=0.7
            )
        return self._model
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """Generate response using OpenAI."""
        model = self.get_chat_model()
        model.temperature = temperature
        
        langchain_messages = []
        if system_prompt:
            langchain_messages.append(SystemMessage(content=system_prompt))
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
        
        response = await model.ainvoke(langchain_messages)
        return response.content

