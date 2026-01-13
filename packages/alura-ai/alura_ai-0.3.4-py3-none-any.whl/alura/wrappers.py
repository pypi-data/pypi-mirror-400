"""
OpenAI wrapper for automatic signal tracking
"""
from typing import Any
from .client import Alura


class AluraOpenAI:
    """
    OpenAI client wrapper that automatically tracks all API calls to Alura.
    
    Usage:
        from alura import Alura, AluraOpenAI
        from openai import OpenAI
        
        client = Alura(api_key="your-alura-key")
        openai_client = OpenAI(api_key="your-openai-key")
        alura_openai = AluraOpenAI(openai_client, client)
        
        # Auto-tracked!
        with client.trace(customer_id="cust-123", agent_id="chatbot"):
            response = alura_openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "Hello!"}]
            )
    """
    
    def __init__(self, openai_client: Any, alura_client: Alura):
        self._openai = openai_client
        self._alura = alura_client
        self.chat = _ChatNamespace(openai_client, alura_client)
        self.embeddings = _EmbeddingsNamespace(openai_client, alura_client)
        # Pass through other attributes
        self.models = openai_client.models
        self.files = openai_client.files
        self.images = openai_client.images
        self.audio = openai_client.audio
        self.moderations = openai_client.moderations
    
    def __getattr__(self, name: str) -> Any:
        """Pass through any other attributes to the underlying client"""
        return getattr(self._openai, name)


class _ChatNamespace:
    """Wrapper for chat namespace"""
    
    def __init__(self, openai_client: Any, alura_client: Alura):
        self._openai = openai_client
        self._alura = alura_client
        self.completions = _ChatCompletions(openai_client, alura_client)


class _ChatCompletions:
    """Wrapper for chat.completions with auto-tracking"""
    
    def __init__(self, openai_client: Any, alura_client: Alura):
        self._openai = openai_client
        self._alura = alura_client
    
    def create(self, **kwargs) -> Any:
        """Create chat completion and track to Alura"""
        # Make the actual OpenAI call
        response = self._openai.chat.completions.create(**kwargs)
        
        # Track to Alura
        self._track_completion(response, kwargs)
        
        return response
    
    async def acreate(self, **kwargs) -> Any:
        """Async create chat completion and track to Alura"""
        # Make the actual OpenAI call
        response = await self._openai.chat.completions.acreate(**kwargs)
        
        # Track to Alura
        self._track_completion(response, kwargs)
        
        return response
    
    def _track_completion(self, response: Any, request_kwargs: dict) -> None:
        """Track completion to Alura"""
        try:
            trace = Alura.get_current_trace()
            if not trace or not trace.get("agent_id"):
                # No active trace, skip tracking
                return
            
            data = {
                "model": response.model,
                "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                "output_tokens": response.usage.completion_tokens if response.usage else 0,
            }
            
            # Add cached tokens if available
            if response.usage and hasattr(response.usage, 'prompt_tokens_details'):
                details = response.usage.prompt_tokens_details
                if details and hasattr(details, 'cached_tokens'):
                    data["cached_tokens"] = details.cached_tokens
            
            if trace.get("customer_id"):
                data["customer_id"] = trace["customer_id"]
            
            self._alura.signal(
                event_name="llm_call",
                agent_id=trace["agent_id"],
                data=data,
                customer_id=trace.get("customer_id"),
            )
        except Exception:
            # Don't fail the main request if tracking fails
            pass


class _EmbeddingsNamespace:
    """Wrapper for embeddings namespace"""
    
    def __init__(self, openai_client: Any, alura_client: Alura):
        self._openai = openai_client
        self._alura = alura_client
    
    def create(self, **kwargs) -> Any:
        """Create embeddings and track to Alura"""
        response = self._openai.embeddings.create(**kwargs)
        
        # Track to Alura
        self._track_embedding(response, kwargs)
        
        return response
    
    def _track_embedding(self, response: Any, request_kwargs: dict) -> None:
        """Track embedding to Alura"""
        try:
            trace = Alura.get_current_trace()
            if not trace or not trace.get("agent_id"):
                return
            
            data = {
                "model": response.model,
                "input_tokens": response.usage.total_tokens if response.usage else 0,
                "output_tokens": 0,  # Embeddings don't have output tokens
            }
            
            if trace.get("customer_id"):
                data["customer_id"] = trace["customer_id"]
            
            self._alura.signal(
                event_name="embedding_call",
                agent_id=trace["agent_id"],
                data=data,
                customer_id=trace.get("customer_id"),
            )
        except Exception:
            pass

