import asyncio
from typing import Any, Optional, Union, AsyncIterable
from loguru import logger

from primfunctions.completions.request import (
    CompletionsProvider,
    ChatCompletionRequest,
    StreamOptions,
    ToolChoice,
    ToolDefinition,
    normalize_tools,
)
from primfunctions.completions.messages import ConversationHistory, normalize_messages
from primfunctions.completions.streaming import ChatCompletionChunk
from primfunctions.completions.response import ChatCompletionResponse

from .providers.base import CompletionClient
from .providers.openai.openai_client import OpenAiCompletionClient
from .providers.anthropic.anthropic_client import AnthropicCompletionClient
from .providers.google.google_client import GoogleCompletionClient
from .retry import retry_with_backoff


async def generate_chat_completion(
    provider: Union[str, CompletionsProvider],
    api_key: str,
    model: str,
    messages: Union[ConversationHistory, list[dict]],
    *,
    tools: Optional[list[Union[ToolDefinition, dict[str, Any]]]] = None,
    tool_choice: Optional[ToolChoice] = None,
    temperature: Optional[float] = None,
    timeout: Optional[float] = None,
    max_tokens: Optional[int] = None,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    backoff_multiplier: float = 2.0,
    retry_enabled: bool = False,
    **kwargs: Any,
) -> ChatCompletionResponse:
    """
    Generate chat completion.

    Args:
        provider: LLM provider ("openai", "anthropic", or "google")
        api_key: API key for the provider
        model: Model identifier (provider-specific)
        messages: Conversation history or list of message dicts
        tools: Optional list of tool/function definitions
        tool_choice: Tool choice strategy ("none", "auto", "required", or tool name)
        temperature: Sampling temperature (0.0-2.0)
        timeout: Request timeout in seconds
        max_tokens: Maximum tokens to generate
        max_retries: Maximum number of retry attempts (default: 3)
        retry_delay: Initial delay between retries in seconds (default: 1.0)
        backoff_multiplier: Multiplier for exponential backoff (default: 2.0)
        retry_enabled: Whether to enable retry logic with exponential backoff (default: False)
        **kwargs: Vendor-specific keyword arguments (e.g., service_tier for OpenAI)

    Returns:
        ChatCompletionResponse with the complete response

    Note:
        Retry logic follows OpenAI's recommended exponential backoff pattern.
        Set retry_enabled=True to enable automatic retries on transient failures.
    """

    # Normalize string input to enum
    if isinstance(provider, str):
        try:
            provider = CompletionsProvider(provider.lower())
        except ValueError:
            raise ValueError(f"Invalid provider: {provider}.")

    # Normalize messages to proper message objects
    normalized_messages = normalize_messages(messages)

    # Normalize tools to proper tool objects
    normalized_tools = normalize_tools(tools) if tools else None

    client: CompletionClient
    if provider == CompletionsProvider.OPENAI:
        client = OpenAiCompletionClient()
    elif provider == CompletionsProvider.ANTHROPIC:
        client = AnthropicCompletionClient()
    elif provider == CompletionsProvider.GOOGLE:
        client = GoogleCompletionClient()
    else:
        raise ValueError(f"Invalid provider: {provider}")

    request = ChatCompletionRequest(
        provider=provider,
        api_key=api_key,
        model=model,
        messages=normalized_messages,
        tools=normalized_tools,
        tool_choice=tool_choice,
        temperature=temperature,
        timeout=timeout,
        max_tokens=max_tokens,
        streaming=False,
        vendor_kwargs=kwargs if kwargs else None,
    )

    return await retry_with_backoff(
        client.generate_chat_completion,
        max_retries=max_retries,
        retry_delay=retry_delay,
        backoff_multiplier=backoff_multiplier,
        retry_enabled=retry_enabled,
        request=request
    )


async def generate_chat_completion_stream(
    provider: Union[str, CompletionsProvider],
    api_key: str,
    model: str,
    messages: Union[ConversationHistory, list[dict]],
    *,
    tools: Optional[list[Union[ToolDefinition, dict[str, Any]]]] = None,
    tool_choice: Optional[ToolChoice] = None,
    temperature: Optional[float] = None,
    timeout: Optional[float] = None,
    max_tokens: Optional[int] = None,
    stream_options: Optional[Union[StreamOptions, dict[str, Any]]] = None,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    backoff_multiplier: float = 2.0,
    retry_enabled: bool = False,
    **kwargs: Any,
) -> AsyncIterable[ChatCompletionChunk]:
    """
    Generate streaming chat completion.

    Args:
        provider: LLM provider ("openai", "anthropic", or "google")
        api_key: API key for the provider
        model: Model identifier (provider-specific)
        messages: Conversation history or list of message dicts
        tools: Optional list of tool/function definitions
        tool_choice: Tool choice strategy ("none", "auto", "required", or tool name)
        temperature: Sampling temperature (0.0-2.0)
        timeout: Request timeout in seconds
        max_tokens: Maximum tokens to generate
        stream_options: Options for configuring streaming behavior
        max_retries: Maximum number of retry attempts for initial connection (default: 3)
        retry_delay: Initial delay between retries in seconds (default: 1.0)
        backoff_multiplier: Multiplier for exponential backoff (default: 2.0)
        retry_enabled: Whether to enable retry logic for initial connection (default: False)
        **kwargs: Vendor-specific keyword arguments (e.g., service_tier for OpenAI)

    Returns:
        AsyncIterable of ChatCompletionChunk objects (typed chunks)

    Retry Behavior:
        When retry_enabled=True, the function will retry ONLY the initial connection
        (before streaming starts). Retries use exponential backoff (1s, 2s, 4s, etc.).

        ✅ RETRIES (Initial Connection Failures):
           - Network errors before streaming starts
           - Rate limits (429)
           - Server errors (500, 502, 503)
           - Authentication errors (401)
           - Timeout errors

        ❌ NO RETRY (Mid-Stream Failures):
           - Once streaming begins, failures are NOT retried
           - This prevents duplicate content in real-time applications
           - Mid-stream failures raise exceptions immediately

        Example:
            # Connection retry attempt 1: ❌ Timeout
            # Wait 1 second...
            # Connection retry attempt 2: ✅ Success!
            # Stream chunk 1: "Hello..." ✅
            # Stream chunk 2: "world..."  ✅
            # [If chunk 3 fails → raises exception immediately, no retry]

        For voice/chat agents, this ensures reliability without duplicate audio/messages.
    """

    # Normalize string input to enum
    if isinstance(provider, str):
        try:
            provider = CompletionsProvider(provider.lower())
        except ValueError:
            raise ValueError(f"Invalid provider: {provider}.")

    # Normalize messages to proper message objects
    normalized_messages = normalize_messages(messages)

    # Normalize tools to proper tool objects
    normalized_tools = normalize_tools(tools) if tools else None

    # Normalize stream options if provided as dict
    if stream_options and isinstance(stream_options, dict):
        stream_options = StreamOptions.deserialize(stream_options)

    client: CompletionClient
    if provider == CompletionsProvider.OPENAI:
        client = OpenAiCompletionClient()
    elif provider == CompletionsProvider.ANTHROPIC:
        client = AnthropicCompletionClient()
    elif provider == CompletionsProvider.GOOGLE:
        client = GoogleCompletionClient()
    else:
        raise ValueError(f"Invalid provider: {provider}")

    request = ChatCompletionRequest(
        provider=provider,
        api_key=api_key,
        model=model,
        messages=normalized_messages,
        tools=normalized_tools,
        tool_choice=tool_choice,
        temperature=temperature,
        timeout=timeout,
        max_tokens=max_tokens,
        streaming=True,
        stream_options=stream_options,
        vendor_kwargs=kwargs if kwargs else None,
    )

    # ============================================================================
    # RETRY BEHAVIOR FOR STREAMING
    # ============================================================================
    # Retry ONLY the initial connection (before streaming starts).
    # Once streaming begins, failures are NOT retried to prevent duplicate content.
    #
    # ✅ RETRIED: Connection failures (network errors, rate limits, timeouts)
    # ❌ NOT RETRIED: Mid-stream failures (after chunks start flowing)
    #
    # This ensures reliability for connection issues while avoiding duplicate
    # audio/messages in real-time applications like voice agents.
    # ============================================================================

    if not retry_enabled:
        # No retry - return stream directly
        try:
            return client.generate_chat_completion_stream(request=request)
        except Exception as e:
            logger.error(f"Completion stream failed: {e}")
            raise

    # WITH RETRY - retry establishing the initial connection
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            # Attempt to establish connection and get stream
            # If this succeeds, streaming begins and no further retries occur
            return client.generate_chat_completion_stream(request=request)

        except Exception as e:
            last_exception = e

            # Don't retry on last attempt
            if attempt == max_retries:
                logger.error(f"Failed to start stream after {max_retries + 1} attempts: {str(e)}")
                raise

            # Calculate delay with exponential backoff and retry
            delay = retry_delay * (backoff_multiplier ** attempt)
            logger.warning(f"Stream connection attempt {attempt + 1} failed: {str(e)}. Retrying in {delay}s...")
            await asyncio.sleep(delay)

    raise last_exception or Exception("Failed to start stream with unknown error")

