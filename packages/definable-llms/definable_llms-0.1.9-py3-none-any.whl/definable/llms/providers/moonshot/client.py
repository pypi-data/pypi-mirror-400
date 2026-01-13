"""MoonshotAI provider implementation."""

from typing import Optional, Dict, Any, List, Union, AsyncGenerator
import structlog

from ...base import BaseProvider, ProviderCapabilities
from ...base.types import (
  ChatRequest,
  ChatResponse,
  StreamChunk,
  Message,
  MessageRole,
  Choice,
  Usage,
  FinishReason,
  ContentType,
  ModelCapabilities,
  ModelInfo,
)
from ...base.exceptions import (
  ProviderAuthenticationError,
  ProviderRateLimitError,
  ProviderQuotaExceededError,
  ProviderTimeoutError,
  ModelNotFoundError,
  InvalidRequestError,
  ContentFilterError,
  TokenLimitError,
)
from ...config import settings
from ...database.backend_model_loader import BackendModelLoader

try:
  from openai import AsyncOpenAI
except ImportError:
  raise ImportError("`openai` not installed. Please install it using `pip install openai`")


logger = structlog.get_logger()


class MoonshotAIProvider(BaseProvider):
  """MoonshotAI provider implementation with model management."""

  def __init__(self, api_key: Optional[str] = None, **kwargs):
    """Initialize MoonshotAI provider.

    Args:
        api_key: Moonshot API key
        **kwargs: Additional configuration
    """
    super().__init__("moonshot", api_key, **kwargs)

  def _initialize(self, **kwargs):
    """Initialize Moonshot-specific settings."""
    if not self.api_key:
      raise ProviderAuthenticationError("moonshot", "Moonshot API key is required")

      # Initialize async client with no timeout
    self.client = AsyncOpenAI(
      base_url="https://api.moonshot.ai/v1",
      api_key=self.api_key,
      timeout=None,  # No timeout
    )

    # Model configurations
    self.default_model = kwargs.get("default_model", settings.moonshot_default_model)
    self.default_temperature = kwargs.get("temperature", settings.moonshot_temperature)
    self.default_max_tokens = kwargs.get("max_tokens", settings.moonshot_max_tokens)

  def get_capabilities(self) -> ProviderCapabilities:
    """Get Moonshot provider capabilities

    Note: This method is deprecated. Use get_model_capabilities() for specific models.
    """
    # Note: This method provides general capabilities. Use get_model_capabilities() for specific models.
    return ProviderCapabilities(
      chat=True,
      streaming=True,
      function_calling=True,
      vision=True,
      audio=False,  # Not implemented yet
      embeddings=True,
      image_generation=True,
      max_context_length=256000,  # Maximum across all models
      supported_models=[],  # Use get_supported_models() for list from database (model registry)
      supported_file_types=[".png", ".jpg", ".jpeg", ".gif", ".webp"],
    )

  @staticmethod
  def is_reasoning_model(model: str) -> bool:
    """
    Checks whether the given model is thinking or not
    """
    return model in ["kimi-k2-thinking", "kimi-k2-thinking-turbo"]

  async def get_model_capabilities(self, model: str) -> ModelCapabilities:
    """Get capabilities for a specific model from backend database.

    Args:
        model: Model name

    Returns:
        Model capabilities

    Raises:
        ValueError: If model is not supported
    """
    # Use backend model loader if available
    loader = BackendModelLoader(settings.database_url)
    try:
      capabilities = await loader.get_model_capabilities("moonshot", model)
      if capabilities is None:
        raise ValueError(f"Model '{model}' is not supported by Moonshot provider")
      return capabilities
    finally:
      await loader.close()

  async def get_supported_models(self) -> List[ModelInfo]:
    """Get list of all supported models from backend database.

    Returns:
        List of model information
    """
    loader = BackendModelLoader(settings.database_url)
    try:
      return await loader.get_supported_models_info("moonshot")
    finally:
      await loader.close()

  def _get_model_description(self, model: str) -> str:
    """Get a description for a specific model."""
    descriptions = {
      "kimi-k2-0905-preview": (
        "Context length 256k, enhanced Agentic Coding capabilities, front-end code aesthetics and practicality, "
        "and context understanding capabilities based on the 0711 version"
      ),
      "kimi-k2-0711-preview": (
        "Context length 128k, MoE architecture base model with 1T total parameters, 32B activated parameters. "
        "Features powerful code and Agent capabilities"
      ),
      "kimi-k2-turbo-preview": (
        "High-speed version of K2, benchmarking against the latest version (0905). "
        "Output speed increased to 60-100 tokens per second, context length 256k"
      ),
      "kimi-k2-thinking": (
        "K2 Long-term thinking model, supports 256k context, supports multi-step tool usage and reasoning, excels at solving more complex problems"
      ),
      "kimi-k2-thinking-turbo": (
        "K2 Long-term thinking model high-speed version, supports 256k context, excels at deep reasoning, "
        "output speed increased to 60-100 tokens per second"
      ),
    }
    return descriptions.get(model, f"Moonshot {model} model")

  async def validate_model(self, model: str) -> bool:
    """Validate that a model is supported using backend database.

    Args:
        model: Model name to validate

    Returns:
        True if model is supported, False otherwise
    """
    loader = BackendModelLoader(settings.database_url)
    try:
      return await loader.validate_model("moonshot", model)
    finally:
      await loader.close()

  def _convert_message_to_moonshot(self, message: Message) -> Dict[str, Any]:
    """Convert internal message format to Moonshot format.

    Args:
        message: Internal message format

    Returns:
        Moonshot-compatible message dictionary
    """
    moonshoot_message = {
      "role": message.role.value,
    }

    if isinstance(message.content, str):
      moonshoot_message["content"] = message.content
    elif isinstance(message.content, list):
      content_parts = []

      for content in message.content:
        if content.type == ContentType.TEXT:
          content_parts.append({"type": "text", "text": content.text})
        elif content.type == ContentType.IMAGE:
          if content.image_url:
            content_parts.append({
              "type": "image_url",
              "image_url": {"url": content.image_url},  # type: ignore
            })
          elif content.image_base64:
            # Ensure proper data URL format
            if not content.image_base64.startswith("data:"):
              content.image_base64 = f"data:image/jpeg;base64,{content.image_base64}"

            content_parts.append({
              "type": "image_url",
              "image_url": {"url": content.image_base64},  # type: ignore
            })

      moonshoot_message["content"] = content_parts  # type: ignore

    # Add function call information if present
    if message.function_call:
      moonshoot_message["function_call"] = {  # type: ignore
        "name": message.function_call.name,
        "arguments": message.function_call.arguments,
      }

    if message.tool_calls:
      moonshoot_message["tool_calls"] = [  # type: ignore
        {
          "id": tool_call.id,
          "type": "function",
          "function": {
            "name": tool_call.function.name,
            "arguments": tool_call.function.arguments,
          },
        }
        for tool_call in message.tool_calls
      ]

    if message.name:
      moonshoot_message["name"] = message.name

    return moonshoot_message

  def _convert_moonshot_message(self, moonshot_message: Dict[str, Any]) -> Message:
    """Convert Moonshot message format to internal format.

    Args:
        moonshot_message: Moonshot message dictionary

    Returns:
        Internal message format
    """
    # Handle None or missing moonshot_message
    if not moonshot_message:
      raise ValueError("Moonshot message cannot be None or empty")

    # Handle missing required fields safely
    if "role" not in moonshot_message:
      raise ValueError("Moonshot message missing required 'role' field")

    role = MessageRole(moonshot_message["role"])
    content = moonshot_message.get("content", "")

    # Extract reasoning/thinking content if present (for thinking models)
    # Moonshot returns reasoning_content as a separate field, not in content array
    reasoning_content = moonshot_message.get("reasoning_content")

    message = Message(
      role=role,
      content=content,
      name=moonshot_message.get("name"),
      reasoning_content=reasoning_content,
    )

    # Handle function calls
    if "function_call" in moonshot_message and moonshot_message["function_call"]:
      from ...base.types import FunctionCall

      function_call = moonshot_message["function_call"]
      if function_call and isinstance(function_call, dict) and "name" in function_call:
        message.function_call = FunctionCall(
          name=function_call["name"],
          arguments=function_call.get("arguments", ""),
        )

    if "tool_calls" in moonshot_message and moonshot_message["tool_calls"]:
      from ...base.types import ToolCall, FunctionCall

      tool_calls = moonshot_message["tool_calls"]
      if tool_calls and isinstance(tool_calls, list):
        message.tool_calls = []
        for tool_call in tool_calls:
          if (
            tool_call
            and isinstance(tool_call, dict)
            and "id" in tool_call
            and "function" in tool_call
            and tool_call["function"]
            and isinstance(tool_call["function"], dict)
          ):
            message.tool_calls.append(
              ToolCall(
                id=tool_call["id"],
                type="function",
                function=FunctionCall(
                  name=tool_call["function"].get("name", ""),
                  arguments=tool_call["function"].get("arguments", ""),
                ),
              )
            )

    return message

  def _handle_moonshot_error(self, error: Exception) -> Exception:
    """Convert Moonshot errors to our internal error types.

    Args:
        error: Original Moonshot error

    Returns:
        Converted exception
    """
    error_str = str(error)

    if "authentication" in error_str.lower() or "api key" in error_str.lower():
      return ProviderAuthenticationError("moonshot", error_str)
    elif "rate limit" in error_str.lower():
      # Try to extract retry_after from the error
      return ProviderRateLimitError("moonshot", message=error_str)
    elif "quota" in error_str.lower() or "billing" in error_str.lower():
      return ProviderQuotaExceededError("moonshot", error_str)
    elif "timeout" in error_str.lower():
      return ProviderTimeoutError("moonshot")
    elif "model" in error_str.lower() and "not found" in error_str.lower():
      return ModelNotFoundError("moonshot", "unknown")
    elif "content policy" in error_str.lower() or "safety" in error_str.lower():
      return ContentFilterError(error_str)
    elif "token" in error_str.lower() and "limit" in error_str.lower():
      return TokenLimitError(error_str, 0, 0)  # Will be filled with actual values if available
    else:
      return InvalidRequestError(f"Moonshot API error: {error_str}")

  async def chat(self, request: ChatRequest, **kwargs) -> Union[ChatResponse, AsyncGenerator[StreamChunk, None]]:
    """Send a chat completion request to Moonshot.

    Args:
        request: Chat completion request
        **kwargs: Additional Moonshot-specific parameters

    Returns:
        Chat response or async generator for streaming
    """
    # Validate request
    self._validate_request(request)

    # Estimate tokens for rate limiting
    estimated_tokens = self._estimate_tokens(request.messages)
    await self._check_rate_limit(estimated_tokens)

    # Prepare Moonshot request
    moonshot_request = {
      "model": request.model or self.default_model,
      "messages": [self._convert_message_to_moonshot(msg) for msg in request.messages],
      "temperature": request.temperature or self.default_temperature,
      "stream": request.stream,
    }

    # Handle model-specific parameter requirements
    model = request.model or self.default_model

    # Add optional parameters
    if request.top_p is not None:
      moonshot_request["top_p"] = request.top_p
    if request.frequency_penalty is not None:
      moonshot_request["frequency_penalty"] = request.frequency_penalty
    if request.presence_penalty is not None:
      moonshot_request["presence_penalty"] = request.presence_penalty
    if request.stop:
      moonshot_request["stop"] = request.stop
    if request.functions:
      moonshot_request["functions"] = request.functions
    if request.function_call:
      moonshot_request["function_call"] = request.function_call
    if request.tools:
      moonshot_request["tools"] = request.tools
    if request.tool_choice:
      moonshot_request["tool_choice"] = request.tool_choice
    if request.user:
      moonshot_request["user"] = request.user
    if request.seed is not None:
      moonshot_request["seed"] = request.seed
    if request.response_format:
      moonshot_request["response_format"] = request.response_format
    if request.logit_bias:
      moonshot_request["logit_bias"] = request.logit_bias
    if request.logprobs is not None:
      moonshot_request["logprobs"] = request.logprobs
    if request.top_logprobs is not None:
      moonshot_request["top_logprobs"] = request.top_logprobs
    if request.n != 1:
      moonshot_request["n"] = request.n

    # Add any additional Moonshot-specific parameters
    moonshot_request.update(kwargs)

    # check whether the model is thinking or not
    if self.is_reasoning_model(model):
      moonshot_request["temperature"] = 1.0
      moonshot_request["max_tokens"] = 1024 * 32

    try:
      async with self._timed_request(
        f"chat_completion:{moonshot_request['model']}",
        timeout=kwargs.get("timeout", 30.0),
      ):
        response = await self.client.chat.completions.create(**moonshot_request)  # type: ignore[arg-type]

        if request.stream:
          return self._handle_streaming_response(response)
        else:
          return self._handle_chat_response(response)

    except Exception as e:
      self.logger.error(f"Moonshot chat completion failed: {e}")
      raise self._handle_moonshot_error(e)

  def _handle_chat_response(self, response) -> ChatResponse:
    """Convert Moonshot response to internal format.

    Args:
        response: Moonshot response object

    Returns:
        Internal chat response
    """
    # Handle None response
    if not response:
      raise ValueError("Moonshot response cannot be None")

    # Handle missing choices
    if not hasattr(response, "choices") or not response.choices:
      raise ValueError("Moonshot response missing choices")

    choices = []

    for choice in response.choices:
      # Handle missing message
      if not hasattr(choice, "message") or not choice.message:
        raise ValueError("Moonshot choice missing message")

      # Handle the message conversion more safely
      try:
        message_dict = choice.message.model_dump() if hasattr(choice.message, "model_dump") else choice.message.__dict__
      except Exception as e:
        self.logger.error(f"Failed to convert choice.message to dict: {e}")
        # Fallback - create minimal message dict
        message_dict = {
          "role": getattr(choice.message, "role", "assistant"),
          "content": getattr(choice.message, "content", ""),
        }

      internal_message = self._convert_moonshot_message(message_dict)

      finish_reason = None
      if hasattr(choice, "finish_reason") and choice.finish_reason:
        try:
          finish_reason = FinishReason(choice.finish_reason)
        except ValueError:
          # Log unknown finish reason but don't fail
          self.logger.warning(f"Unknown finish reason: {choice.finish_reason}")

      logprobs_data = None
      if hasattr(choice, "logprobs") and choice.logprobs:
        try:
          logprobs_data = choice.logprobs.model_dump() if hasattr(choice.logprobs, "model_dump") else choice.logprobs.__dict__
        except Exception as e:
          self.logger.warning(f"Failed to process logprobs: {e}")

      choices.append(
        Choice(
          index=getattr(choice, "index", 0),
          message=internal_message,
          finish_reason=finish_reason,
          logprobs=logprobs_data,
        )
      )

    usage = None
    if hasattr(response, "usage") and response.usage:
      try:
        usage = Usage(
          input_tokens=getattr(response.usage, "prompt_tokens", 0),
          output_tokens=getattr(response.usage, "completion_tokens", 0),
          total_tokens=getattr(response.usage, "total_tokens", 0),
        )
      except Exception as e:
        self.logger.warning(f"Failed to process usage data: {e}")

    try:
      return ChatResponse(
        id=getattr(response, "id", ""),
        created=getattr(response, "created", 0),
        model=getattr(response, "model", ""),
        choices=choices,
        usage=usage,
        system_fingerprint=getattr(response, "system_fingerprint", None),
      )
    except Exception as e:
      self.logger.error(f"Failed to create ChatResponse: {e}")
      raise ValueError(f"Failed to create ChatResponse: {e}")

  async def _handle_streaming_response(self, response) -> AsyncGenerator[StreamChunk, None]:
    """Handle streaming chat response.

    Args:
        response: Moonshot streaming response

    Yields:
        Stream chunks
    """
    async for chunk in response:
      # Handle None or empty chunks
      if not chunk:
        continue

      # Build choices from chunk
      choices = []

      if hasattr(chunk, "choices") and chunk.choices:
        for choice in chunk.choices:
          choice_dict: Dict[str, Any] = {
            "index": getattr(choice, "index", 0),
            "delta": {},
            "finish_reason": getattr(choice, "finish_reason", None),
          }

          # Extract delta content
          if hasattr(choice, "delta") and choice.delta:
            delta = choice.delta

            # Standard content
            if hasattr(delta, "content") and delta.content:
              choice_dict["delta"]["content"] = delta.content
              choice_dict["delta"]["type"] = "content"

            # Reasoning/thinking content for thinking models
            if hasattr(delta, "reasoning_content") and delta.reasoning_content:
              choice_dict["delta"]["content"] = delta.reasoning_content
              choice_dict["delta"]["type"] = "thinking"

            # Role information
            if hasattr(delta, "role"):
              choice_dict["delta"]["role"] = delta.role

            # Function call information
            if hasattr(delta, "function_call"):
              choice_dict["delta"]["function_call"] = delta.function_call

            # Tool calls information
            if hasattr(delta, "tool_calls"):
              choice_dict["delta"]["tool_calls"] = delta.tool_calls

          choices.append(choice_dict)

      # Extract usage information if present
      usage = None
      if hasattr(chunk, "usage") and chunk.usage:
        try:
          usage = Usage(
            input_tokens=getattr(chunk.usage, "prompt_tokens", 0),
            output_tokens=getattr(chunk.usage, "completion_tokens", 0),
            total_tokens=getattr(chunk.usage, "total_tokens", 0),
          )
        except Exception as e:
          self.logger.warning(f"Failed to process streaming usage data: {e}")

      # Yield the stream chunk
      yield StreamChunk(
        id=getattr(chunk, "id", ""),
        created=getattr(chunk, "created", 0),
        model=getattr(chunk, "model", ""),
        choices=choices,
        usage=usage,
      )

  async def generate_image(self, request, **kwargs):
    """Generate images.

    Note: Moonshot does not provide image generation models.
    This method raises NotImplementedError.
    """
    raise NotImplementedError("Moonshot does not support image generation")

  async def generate_embedding(self, request, **kwargs):
    """Generate text embeddings.

    Note: Moonshot does not provide embedding models.
    This method raises NotImplementedError.
    """
    raise NotImplementedError("Moonshot does not support embeddings")

  async def close(self):
    """Close the Moonshot client and cleanup resources."""
    if self._closed:
      return

    try:
      if hasattr(self, "client") and self.client:
        await self.client.close()
        self.logger.debug("Closed Moonshot client")
    except Exception as e:
      self.logger.error(f"Error closing Moonshot client: {e}")
    finally:
      self._closed = True
