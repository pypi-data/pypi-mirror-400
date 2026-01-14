"""
LLM Provider implementations for promptops.

This module provides interfaces to various LLM providers with support for:
- Synchronous and asynchronous operations
- Streaming responses
- Token counting and cost estimation
- Retry logic with exponential backoff
- Function/tool calling
- Conversation management
"""

from .openai_provider import (
    # Main provider
    OpenAIProvider,
    # Conversation management
    Conversation,
    # Data classes
    Message,
    CompletionResponse,
    StreamChunk,
    ProviderConfig,
    # Exceptions
    ProviderError,
    RateLimitError,
    AuthenticationError,
    ModelNotFoundError,
    # Constants
    OPENAI_AVAILABLE,
    TIKTOKEN_AVAILABLE,
)

__all__ = [
    # Provider
    "OpenAIProvider",
    # Conversation
    "Conversation",
    # Data classes
    "Message",
    "CompletionResponse",
    "StreamChunk",
    "ProviderConfig",
    # Exceptions
    "ProviderError",
    "RateLimitError",
    "AuthenticationError",
    "ModelNotFoundError",
    # Feature flags
    "OPENAI_AVAILABLE",
    "TIKTOKEN_AVAILABLE",
]
