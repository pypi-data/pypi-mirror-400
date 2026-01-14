"""
OpenAI provider for LLM interactions.

Provides a robust interface to OpenAI's API with support for:
- Chat completions and text generation
- Streaming responses
- Token counting and usage tracking
- Retry logic with exponential backoff
- Cost tracking integration
- Multiple model support
"""

import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import (
    Any,
    AsyncIterator,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Union,
)

logger = logging.getLogger(__name__)

# Try to import openai, but allow graceful degradation
try:
    import openai
    from openai import OpenAI, AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None
    OpenAI = None
    AsyncOpenAI = None

# Try to import tiktoken for token counting
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    tiktoken = None


@dataclass
class Message:
    """Represents a chat message."""
    role: str  # "system", "user", "assistant", "function", "tool"
    content: str
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to OpenAI message format."""
        msg = {"role": self.role, "content": self.content}
        if self.name:
            msg["name"] = self.name
        if self.function_call:
            msg["function_call"] = self.function_call
        if self.tool_calls:
            msg["tool_calls"] = self.tool_calls
        return msg


@dataclass
class CompletionResponse:
    """Response from a completion request."""
    content: str
    model: str
    finish_reason: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0
    raw_response: Optional[Any] = None
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    
    @property
    def cost(self) -> float:
        """Estimate cost based on token usage."""
        from ..cost.budget import DEFAULT_MODEL_PRICING
        pricing = DEFAULT_MODEL_PRICING.get(self.model, {"input": 0.01, "output": 0.03})
        return (
            (self.input_tokens / 1000) * pricing["input"] +
            (self.output_tokens / 1000) * pricing["output"]
        )


@dataclass
class StreamChunk:
    """A chunk from a streaming response."""
    content: str
    finish_reason: Optional[str] = None
    is_complete: bool = False


@dataclass
class ProviderConfig:
    """Configuration for the OpenAI provider."""
    api_key: Optional[str] = None
    organization: Optional[str] = None
    base_url: Optional[str] = None
    default_model: str = "gpt-4o-mini"
    default_temperature: float = 0.7
    default_max_tokens: Optional[int] = None
    timeout: float = 60.0
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_multiplier: float = 2.0
    retry_max_delay: float = 60.0


@dataclass
class OpenAIConfig:
    """Configuration for OpenAI API calls (simplified interface)."""
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[Union[str, List[str]]] = None


@dataclass
class ModelConfig:
    """Model configuration with pricing information."""
    name: str
    cost_per_1k_tokens: float
    max_tokens: int
    context_window: Optional[int] = None


class ProviderError(Exception):
    """Base exception for provider errors."""
    pass


class RateLimitError(ProviderError):
    """Raised when rate limited by the API."""
    def __init__(self, message: str, retry_after: Optional[float] = None):
        super().__init__(message)
        self.retry_after = retry_after


class AuthenticationError(ProviderError):
    """Raised when authentication fails."""
    pass


class ModelNotFoundError(ProviderError):
    """Raised when the requested model is not available."""
    pass


class OpenAIProvider:
    """
    OpenAI provider for LLM interactions.
    
    Features:
    - Synchronous and asynchronous API support
    - Streaming responses
    - Automatic retry with exponential backoff
    - Token counting and cost estimation
    - Function/tool calling support
    - Conversation management
    
    Example:
        >>> provider = OpenAIProvider()
        >>> response = provider.complete("Hello, how are you?")
        >>> print(response.content)
        
        >>> # Streaming
        >>> for chunk in provider.stream("Tell me a story"):
        ...     print(chunk.content, end="")
        
        >>> # Chat conversation
        >>> messages = [
        ...     Message(role="system", content="You are helpful."),
        ...     Message(role="user", content="What's 2+2?"),
        ... ]
        >>> response = provider.chat(messages)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[Union[ProviderConfig, OpenAIConfig]] = None,
        **kwargs,
    ):
        """
        Initialize the OpenAI provider.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var).
            config: Provider configuration (ProviderConfig or OpenAIConfig).
            **kwargs: Additional configuration options.
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "openai package is required. Install with: pip install openai"
            )
        
        # Convert OpenAIConfig to ProviderConfig if needed
        if isinstance(config, OpenAIConfig):
            self.config = ProviderConfig(
                default_model=config.model,
                default_temperature=config.temperature,
                default_max_tokens=config.max_tokens,
            )
            self._openai_config = config
        else:
            self.config = config or ProviderConfig()
            self._openai_config = None
        
        # Override config with kwargs
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        # Set API key
        self._api_key = api_key or self.config.api_key or os.getenv("OPENAI_API_KEY")
        if not self._api_key:
            raise AuthenticationError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        # Initialize clients
        client_kwargs = {
            "api_key": self._api_key,
            "timeout": self.config.timeout,
            "max_retries": 0,  # We handle retries ourselves
        }
        if self.config.organization:
            client_kwargs["organization"] = self.config.organization
        if self.config.base_url:
            client_kwargs["base_url"] = self.config.base_url
        
        self._client = OpenAI(**client_kwargs)
        self._async_client = AsyncOpenAI(**client_kwargs)
        
        # Token counting
        self._encoders: Dict[str, Any] = {}
        
        # Callbacks
        self._on_request: Optional[Callable] = None
        self._on_response: Optional[Callable] = None
        self._on_error: Optional[Callable] = None
        
        logger.info(f"OpenAI provider initialized (model: {self.config.default_model})")
    
    def set_callbacks(
        self,
        on_request: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_response: Optional[Callable[[CompletionResponse], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
    ) -> None:
        """
        Set callback functions for request lifecycle events.
        
        Args:
            on_request: Called before each request with request params.
            on_response: Called after each successful response.
            on_error: Called when an error occurs.
        """
        self._on_request = on_request
        self._on_response = on_response
        self._on_error = on_error
    
    def _get_encoder(self, model: str) -> Any:
        """Get or create a tiktoken encoder for the model."""
        if not TIKTOKEN_AVAILABLE:
            return None
        
        if model not in self._encoders:
            try:
                self._encoders[model] = tiktoken.encoding_for_model(model)
            except KeyError:
                # Fall back to cl100k_base for unknown models
                self._encoders[model] = tiktoken.get_encoding("cl100k_base")
        
        return self._encoders[model]
    
    def count_tokens(
        self,
        text: Union[str, List[Message]],
        model: Optional[str] = None,
    ) -> int:
        """
        Count tokens in text or messages.
        
        Args:
            text: Text string or list of Messages.
            model: Model to use for tokenization.
        
        Returns:
            Token count.
        """
        model = model or self.config.default_model
        encoder = self._get_encoder(model)
        
        if encoder is None:
            # Rough estimate: ~4 chars per token
            if isinstance(text, str):
                return len(text) // 4
            return sum(len(m.content) // 4 for m in text)
        
        if isinstance(text, str):
            return len(encoder.encode(text))
        
        # For messages, account for message overhead
        total = 0
        for msg in text:
            total += 4  # Message overhead
            total += len(encoder.encode(msg.content))
            if msg.name:
                total += len(encoder.encode(msg.name))
        total += 2  # Priming tokens
        
        return total
    
    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: Optional[str] = None,
    ) -> float:
        """
        Estimate cost for token usage.
        
        Args:
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens.
            model: Model name.
        
        Returns:
            Estimated cost in dollars.
        """
        from ..cost.budget import DEFAULT_MODEL_PRICING
        model = model or self.config.default_model
        pricing = DEFAULT_MODEL_PRICING.get(model, {"input": 0.01, "output": 0.03})
        return (
            (input_tokens / 1000) * pricing["input"] +
            (output_tokens / 1000) * pricing["output"]
        )
    
    def _build_request_params(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        functions: Optional[List[Dict[str, Any]]] = None,
        function_call: Optional[Union[str, Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        response_format: Optional[Dict[str, str]] = None,
        seed: Optional[int] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Build request parameters for the API call."""
        params = {
            "model": model or self.config.default_model,
            "messages": [m.to_dict() for m in messages],
            "temperature": temperature if temperature is not None else self.config.default_temperature,
        }
        
        if max_tokens is not None or self.config.default_max_tokens:
            params["max_tokens"] = max_tokens or self.config.default_max_tokens
        
        if top_p is not None:
            params["top_p"] = top_p
        if frequency_penalty is not None:
            params["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            params["presence_penalty"] = presence_penalty
        if stop is not None:
            params["stop"] = stop
        if functions is not None:
            params["functions"] = functions
        if function_call is not None:
            params["function_call"] = function_call
        if tools is not None:
            params["tools"] = tools
        if tool_choice is not None:
            params["tool_choice"] = tool_choice
        if response_format is not None:
            params["response_format"] = response_format
        if seed is not None:
            params["seed"] = seed
        
        # Add any extra kwargs
        params.update(kwargs)
        
        return params
    
    def _handle_api_error(self, error: Exception) -> None:
        """Handle and convert API errors."""
        if self._on_error:
            self._on_error(error)
        
        error_str = str(error).lower()
        
        if "rate limit" in error_str or "429" in error_str:
            retry_after = None
            # Try to extract retry-after
            if hasattr(error, "response") and error.response:
                retry_after = error.response.headers.get("retry-after")
                if retry_after:
                    retry_after = float(retry_after)
            raise RateLimitError(str(error), retry_after)
        
        if "authentication" in error_str or "401" in error_str:
            raise AuthenticationError(str(error))
        
        if "model" in error_str and "not found" in error_str:
            raise ModelNotFoundError(str(error))
        
        raise ProviderError(str(error))
    
    def _execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs,
    ) -> Any:
        """Execute a function with retry logic."""
        last_error = None
        delay = self.config.retry_delay
        
        for attempt in range(self.config.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                
                # Check if we should retry
                error_str = str(e).lower()
                is_retryable = (
                    "rate limit" in error_str or
                    "timeout" in error_str or
                    "connection" in error_str or
                    "503" in error_str or
                    "502" in error_str or
                    "500" in error_str
                )
                
                if not is_retryable or attempt >= self.config.max_retries:
                    self._handle_api_error(e)
                
                # Get retry delay
                if "rate limit" in error_str and hasattr(e, "response"):
                    retry_after = e.response.headers.get("retry-after")
                    if retry_after:
                        delay = float(retry_after)
                
                logger.warning(
                    f"Request failed (attempt {attempt + 1}/{self.config.max_retries + 1}): {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                time.sleep(delay)
                delay = min(delay * self.config.retry_multiplier, self.config.retry_max_delay)
        
        self._handle_api_error(last_error)
    
    def chat(
        self,
        messages: List[Message],
        **kwargs,
    ) -> CompletionResponse:
        """
        Send a chat completion request.
        
        Args:
            messages: List of Message objects.
            **kwargs: Additional parameters for the API.
        
        Returns:
            CompletionResponse with the result.
        """
        params = self._build_request_params(messages, **kwargs)
        
        if self._on_request:
            self._on_request(params)
        
        start_time = time.time()
        
        def make_request():
            return self._client.chat.completions.create(**params)
        
        response = self._execute_with_retry(make_request)
        
        latency_ms = (time.time() - start_time) * 1000
        
        choice = response.choices[0]
        message = choice.message
        
        result = CompletionResponse(
            content=message.content or "",
            model=response.model,
            finish_reason=choice.finish_reason,
            input_tokens=response.usage.prompt_tokens if response.usage else 0,
            output_tokens=response.usage.completion_tokens if response.usage else 0,
            total_tokens=response.usage.total_tokens if response.usage else 0,
            latency_ms=latency_ms,
            raw_response=response,
            function_call=message.function_call.model_dump() if message.function_call else None,
            tool_calls=[tc.model_dump() for tc in message.tool_calls] if message.tool_calls else None,
        )
        
        if self._on_response:
            self._on_response(result)
        
        logger.debug(
            f"Chat completion: {result.total_tokens} tokens, "
            f"{result.latency_ms:.0f}ms, ${result.cost:.4f}"
        )
        
        return result
    
    def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs,
    ) -> CompletionResponse:
        """
        Simple completion with a single prompt.
        
        Args:
            prompt: The user prompt.
            system: Optional system message.
            **kwargs: Additional parameters.
        
        Returns:
            CompletionResponse with the result.
        """
        messages = []
        if system:
            messages.append(Message(role="system", content=system))
        messages.append(Message(role="user", content=prompt))
        
        return self.chat(messages, **kwargs)
    
    def run(self, prompt: str, **kwargs) -> str:
        """
        Simple interface for running a prompt (backward compatible).
        
        Args:
            prompt: The prompt to run.
            **kwargs: Additional parameters.
        
        Returns:
            The response content as a string.
        """
        response = self.complete(prompt, **kwargs)
        return response.content
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Alias for run() method - generates a completion for the given prompt.
        
        Args:
            prompt: The prompt to generate from.
            **kwargs: Additional parameters.
        
        Returns:
            The response content as a string.
        """
        return self.run(prompt, **kwargs)
    
    def stream(
        self,
        messages: Union[str, List[Message]],
        system: Optional[str] = None,
        **kwargs,
    ) -> Iterator[StreamChunk]:
        """
        Stream a completion response.
        
        Args:
            messages: Prompt string or list of Messages.
            system: Optional system message (if messages is a string).
            **kwargs: Additional parameters.
        
        Yields:
            StreamChunk objects with content.
        """
        if isinstance(messages, str):
            msg_list = []
            if system:
                msg_list.append(Message(role="system", content=system))
            msg_list.append(Message(role="user", content=messages))
            messages = msg_list
        
        params = self._build_request_params(messages, **kwargs)
        params["stream"] = True
        
        if self._on_request:
            self._on_request(params)
        
        def make_request():
            return self._client.chat.completions.create(**params)
        
        stream = self._execute_with_retry(make_request)
        
        for chunk in stream:
            if chunk.choices:
                delta = chunk.choices[0].delta
                content = delta.content or ""
                finish_reason = chunk.choices[0].finish_reason
                
                yield StreamChunk(
                    content=content,
                    finish_reason=finish_reason,
                    is_complete=finish_reason is not None,
                )
    
    def stream_to_string(
        self,
        messages: Union[str, List[Message]],
        **kwargs,
    ) -> str:
        """
        Stream a response and return the complete string.
        
        Args:
            messages: Prompt string or list of Messages.
            **kwargs: Additional parameters.
        
        Returns:
            Complete response as a string.
        """
        chunks = []
        for chunk in self.stream(messages, **kwargs):
            chunks.append(chunk.content)
        return "".join(chunks)
    
    async def achat(
        self,
        messages: List[Message],
        **kwargs,
    ) -> CompletionResponse:
        """
        Async chat completion request.
        
        Args:
            messages: List of Message objects.
            **kwargs: Additional parameters.
        
        Returns:
            CompletionResponse with the result.
        """
        params = self._build_request_params(messages, **kwargs)
        
        if self._on_request:
            self._on_request(params)
        
        start_time = time.time()
        
        response = await self._async_client.chat.completions.create(**params)
        
        latency_ms = (time.time() - start_time) * 1000
        
        choice = response.choices[0]
        message = choice.message
        
        result = CompletionResponse(
            content=message.content or "",
            model=response.model,
            finish_reason=choice.finish_reason,
            input_tokens=response.usage.prompt_tokens if response.usage else 0,
            output_tokens=response.usage.completion_tokens if response.usage else 0,
            total_tokens=response.usage.total_tokens if response.usage else 0,
            latency_ms=latency_ms,
            raw_response=response,
            function_call=message.function_call.model_dump() if message.function_call else None,
            tool_calls=[tc.model_dump() for tc in message.tool_calls] if message.tool_calls else None,
        )
        
        if self._on_response:
            self._on_response(result)
        
        return result
    
    async def acomplete(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs,
    ) -> CompletionResponse:
        """
        Async simple completion.
        
        Args:
            prompt: The user prompt.
            system: Optional system message.
            **kwargs: Additional parameters.
        
        Returns:
            CompletionResponse with the result.
        """
        messages = []
        if system:
            messages.append(Message(role="system", content=system))
        messages.append(Message(role="user", content=prompt))
        
        return await self.achat(messages, **kwargs)
    
    async def astream(
        self,
        messages: Union[str, List[Message]],
        system: Optional[str] = None,
        **kwargs,
    ) -> AsyncIterator[StreamChunk]:
        """
        Async streaming completion.
        
        Args:
            messages: Prompt string or list of Messages.
            system: Optional system message.
            **kwargs: Additional parameters.
        
        Yields:
            StreamChunk objects with content.
        """
        if isinstance(messages, str):
            msg_list = []
            if system:
                msg_list.append(Message(role="system", content=system))
            msg_list.append(Message(role="user", content=messages))
            messages = msg_list
        
        params = self._build_request_params(messages, **kwargs)
        params["stream"] = True
        
        if self._on_request:
            self._on_request(params)
        
        stream = await self._async_client.chat.completions.create(**params)
        
        async for chunk in stream:
            if chunk.choices:
                delta = chunk.choices[0].delta
                content = delta.content or ""
                finish_reason = chunk.choices[0].finish_reason
                
                yield StreamChunk(
                    content=content,
                    finish_reason=finish_reason,
                    is_complete=finish_reason is not None,
                )
    
    def with_functions(
        self,
        functions: List[Dict[str, Any]],
        messages: List[Message],
        auto_execute: bool = False,
        function_map: Optional[Dict[str, Callable]] = None,
        **kwargs,
    ) -> CompletionResponse:
        """
        Call with function definitions.
        
        Args:
            functions: List of function definitions.
            messages: Conversation messages.
            auto_execute: If True, execute the function and return result.
            function_map: Map of function names to callables (required if auto_execute).
            **kwargs: Additional parameters.
        
        Returns:
            CompletionResponse, potentially with function results.
        """
        response = self.chat(messages, functions=functions, **kwargs)
        
        if auto_execute and response.function_call and function_map:
            func_name = response.function_call.get("name")
            func_args = json.loads(response.function_call.get("arguments", "{}"))
            
            if func_name in function_map:
                result = function_map[func_name](**func_args)
                
                # Add function result to messages and continue
                messages = messages + [
                    Message(role="assistant", content="", function_call=response.function_call),
                    Message(role="function", name=func_name, content=json.dumps(result)),
                ]
                return self.chat(messages, functions=functions, **kwargs)
        
        return response
    
    def with_tools(
        self,
        tools: List[Dict[str, Any]],
        messages: List[Message],
        auto_execute: bool = False,
        tool_map: Optional[Dict[str, Callable]] = None,
        **kwargs,
    ) -> CompletionResponse:
        """
        Call with tool definitions (newer API).
        
        Args:
            tools: List of tool definitions.
            messages: Conversation messages.
            auto_execute: If True, execute tools and return result.
            tool_map: Map of tool names to callables (required if auto_execute).
            **kwargs: Additional parameters.
        
        Returns:
            CompletionResponse, potentially with tool results.
        """
        response = self.chat(messages, tools=tools, **kwargs)
        
        if auto_execute and response.tool_calls and tool_map:
            tool_results = []
            for tool_call in response.tool_calls:
                func_name = tool_call["function"]["name"]
                func_args = json.loads(tool_call["function"]["arguments"])
                
                if func_name in tool_map:
                    result = tool_map[func_name](**func_args)
                    tool_results.append({
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "content": json.dumps(result),
                    })
            
            if tool_results:
                # Add assistant message with tool calls and tool results
                new_messages = messages + [
                    Message(role="assistant", content="", tool_calls=response.tool_calls),
                ]
                for result in tool_results:
                    new_messages.append(Message(
                        role="tool",
                        content=result["content"],
                        name=result.get("tool_call_id"),
                    ))
                
                return self.chat(new_messages, tools=tools, **kwargs)
        
        return response
    
    def json_mode(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Get response in JSON format.
        
        Args:
            prompt: The prompt (should request JSON output).
            system: Optional system message.
            **kwargs: Additional parameters.
        
        Returns:
            Parsed JSON response.
        """
        if system is None:
            system = "You are a helpful assistant that responds in JSON format."
        
        response = self.complete(
            prompt,
            system=system,
            response_format={"type": "json_object"},
            **kwargs,
        )
        
        return json.loads(response.content)
    
    def batch(
        self,
        prompts: List[str],
        system: Optional[str] = None,
        **kwargs,
    ) -> List[CompletionResponse]:
        """
        Process multiple prompts (sequentially).
        
        Args:
            prompts: List of prompts.
            system: Optional system message for all.
            **kwargs: Additional parameters.
        
        Returns:
            List of CompletionResponse objects.
        """
        return [self.complete(p, system=system, **kwargs) for p in prompts]
    
    async def abatch(
        self,
        prompts: List[str],
        system: Optional[str] = None,
        max_concurrent: int = 5,
        **kwargs,
    ) -> List[CompletionResponse]:
        """
        Process multiple prompts concurrently.
        
        Args:
            prompts: List of prompts.
            system: Optional system message for all.
            max_concurrent: Maximum concurrent requests.
            **kwargs: Additional parameters.
        
        Returns:
            List of CompletionResponse objects.
        """
        import asyncio
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def limited_complete(prompt: str) -> CompletionResponse:
            async with semaphore:
                return await self.acomplete(prompt, system=system, **kwargs)
        
        tasks = [limited_complete(p) for p in prompts]
        return await asyncio.gather(*tasks)
    
    def list_models(self) -> List[str]:
        """
        List available models.
        
        Returns:
            List of model IDs.
        """
        models = self._client.models.list()
        return [m.id for m in models.data if "gpt" in m.id.lower()]
    
    def health_check(self) -> bool:
        """
        Check if the provider is working.
        
        Returns:
            True if healthy.
        """
        try:
            self.complete("Hi", max_tokens=5)
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


class Conversation:
    """
    Manage a multi-turn conversation.
    
    Example:
        >>> conv = Conversation(provider, system="You are helpful.")
        >>> response = conv.say("Hello!")
        >>> response = conv.say("What did I just say?")
        >>> print(conv.history)
    """
    
    def __init__(
        self,
        provider: OpenAIProvider,
        system: Optional[str] = None,
        max_history: Optional[int] = None,
    ):
        """
        Initialize a conversation.
        
        Args:
            provider: OpenAI provider to use.
            system: Optional system message.
            max_history: Maximum messages to keep (None for unlimited).
        """
        self.provider = provider
        self.system = system
        self.max_history = max_history
        self.messages: List[Message] = []
        
        if system:
            self.messages.append(Message(role="system", content=system))
    
    @property
    def history(self) -> List[Message]:
        """Get conversation history (excluding system message)."""
        return [m for m in self.messages if m.role != "system"]
    
    def say(self, content: str, **kwargs) -> CompletionResponse:
        """
        Send a message and get a response.
        
        Args:
            content: User message content.
            **kwargs: Additional parameters for the API.
        
        Returns:
            CompletionResponse from the assistant.
        """
        self.messages.append(Message(role="user", content=content))
        
        response = self.provider.chat(self.messages, **kwargs)
        
        self.messages.append(Message(role="assistant", content=response.content))
        
        # Trim history if needed
        if self.max_history and len(self.history) > self.max_history:
            # Keep system message and last N messages
            system_msgs = [m for m in self.messages if m.role == "system"]
            other_msgs = [m for m in self.messages if m.role != "system"]
            self.messages = system_msgs + other_msgs[-self.max_history:]
        
        return response
    
    async def asay(self, content: str, **kwargs) -> CompletionResponse:
        """Async version of say()."""
        self.messages.append(Message(role="user", content=content))
        
        response = await self.provider.achat(self.messages, **kwargs)
        
        self.messages.append(Message(role="assistant", content=response.content))
        
        return response
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to history without getting a response."""
        self.messages.append(Message(role=role, content=content))
    
    def clear(self, keep_system: bool = True) -> None:
        """Clear conversation history."""
        if keep_system and self.system:
            self.messages = [Message(role="system", content=self.system)]
        else:
            self.messages = []
    
    def fork(self) -> "Conversation":
        """Create a copy of this conversation."""
        conv = Conversation(self.provider, max_history=self.max_history)
        conv.messages = list(self.messages)
        conv.system = self.system
        return conv
    
    def get_token_count(self) -> int:
        """Get total tokens in conversation."""
        return self.provider.count_tokens(self.messages)
    
    def to_dict(self) -> List[Dict[str, Any]]:
        """Export conversation as list of dicts."""
        return [m.to_dict() for m in self.messages]
    
    @classmethod
    def from_dict(
        cls,
        provider: OpenAIProvider,
        messages: List[Dict[str, Any]],
    ) -> "Conversation":
        """Create conversation from list of message dicts."""
        conv = cls(provider)
        conv.messages = [Message(**m) for m in messages]
        # Extract system if present
        for m in conv.messages:
            if m.role == "system":
                conv.system = m.content
                break
        return conv
