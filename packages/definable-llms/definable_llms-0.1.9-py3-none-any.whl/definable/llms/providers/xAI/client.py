"""xAI provider implementation."""

from typing import Optional, Dict, Any, List, Union, AsyncGenerator
import structlog
import base64
import asyncio
import time

from ...base import BaseProvider, ProviderCapabilities
from ...base.types import (
  ChatRequest,
  ChatResponse,
  StreamChunk,
  ImageRequest,
  ImageResponse,
  EmbeddingRequest,
  EmbeddingResponse,
  Message,
  MessageRole,
  Choice,
  Usage,
  ImageData,
  FinishReason,
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
from ...utils import get_gcp_client

try:
  from xai_sdk import AsyncClient
  from xai_sdk.chat import user, system, assistant, Response

except ImportError:
  raise ImportError("`xai_sdk` not installed. Please install it using `pip install xai_sdk`")


logger = structlog.get_logger()


class xAIProvider(BaseProvider):
  """xAI provider implementation."""

  def __init__(self, api_key: Optional[str] = None, **kwargs):
    """Initialize xAI provider.

    Args:
        api_key: xAI API key
        **kwargs: Additional configuration
    """
    super().__init__("xai", api_key, **kwargs)

  def _initialize(self, **kwargs):
    """Initialize xAI-specific settings."""
    if not self.api_key:
      raise ProviderAuthenticationError("xai", "xAI API key is required")

    # Initialize async client with 60 min timeout for reasoning models
    self.client = AsyncClient(
      api_key=self.api_key,
      timeout=3600,
    )

    # Model configurations
    self.default_model = kwargs.get("default_model", settings.xai_default_model)
    self.default_temperature = kwargs.get("temperature", settings.xai_temperature)
    self.default_max_tokens = kwargs.get("max_tokens", settings.xai_max_tokens)

    # Semaphore for concurrency control
    max_concurrent_requests = kwargs.get("max_concurrent_requests", 75)
    self._semaphore = asyncio.Semaphore(max_concurrent_requests)

  def get_capabilities(self) -> ProviderCapabilities:
    """Get xAI provider capabilities

    Note: This method is deprecated. Use get_model_capabilities() for specific models.
    """
    # Note: This method provides general capabilities. Use get_model_capabilities() for specific models.
    return ProviderCapabilities(
      chat=True,
      streaming=True,
      function_calling=True,
      vision=True,
      audio=False,  # Not implemented yet
      embeddings=False,
      image_generation=True,
      max_context_length=256000,  # Maximum across all models
      supported_models=[],  # Use get_supported_models() for list from database (model registry)
      supported_file_types=[".png", ".jpg", ".jpeg", ".gif", ".webp"],
    )

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
      capabilities = await loader.get_model_capabilities("xai", model)
      if capabilities is None:
        raise ValueError(f"Model '{model}' is not supported by xAI provider")
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
      return await loader.get_supported_models_info("xai")
    finally:
      await loader.close()

  def _get_model_description(self, model: str) -> str:
    """Get a description for a specific model."""
    descriptions = {
      "grok-4-1-fast-reasoning": "A xAI frontier multimodal model optimized specifically for high-performance agentic tool calling",
      "grok-4-1-fast-non-reasoning": "A xAI non reasoning frontier multimodal model optimized specifically for high-performance agentic tool calling",
      "grok-code-fast-1": "A speedy and economical reasoning model that excels at agentic coding",
      "grok-4-fast-reasoning": "A cost efficient model optimized specifically for high-performance agentic tool calling",
      "grok-4-fast-non-reasoning": "A cost efficient, non reasoning model optimized specifically for high-performance agentic tool calling",
      "grok-4-0709": (
        "xAI's latest and greatest flagship model, offering unparalleled performance in natural language, "
        "math and reasoning - the perfect jack of all trades"
      ),
      "grok-3-mini": (
        "A lightweight model that thinks before responding. Fast, smart, and great for logic-based tasks that "
        "do not require deep domain knowledge. The raw thinking traces are accessible"
      ),
      "grok-2-vision-1212": "A multimodal model that processes documents, diagrams, charts, screenshots, and photographs",
      "grok-2-image-1212": (
        "xAI's latest image generation model that can generate vivid, realistic images based on a text prompt. "
        "Excels at generating images for marketing, social media, and entertainment."
      ),
    }
    return descriptions.get(model, f"xAI {model} model")

  async def validate_model(self, model: str) -> bool:
    """Validate that a model is supported using backend database.

    Args:
        model: Model name to validate

    Returns:
        True if model is supported, False otherwise
    """
    loader = BackendModelLoader(settings.database_url)
    try:
      return await loader.validate_model("xai", model)
    finally:
      await loader.close()

  def _convert_message_to_xAI(self, message: Message) -> Dict[str, Any]:
    """Convert internal message format to xAI format.

    Args:
        message: Internal message format

    Returns:
        xAI-compatible message dictionary
    """
    raise NotImplementedError("_convert_message_to_xAI is not used by xAI SDK integration")

  def _convert_xAI_message(self, xAI_message: Dict[str, Any]) -> Message:
    """Convert xAI message format to internal format.

    Args:
        xAI_message: xAI message dictionary

    Returns:
        Internal message format
    """
    raise NotImplementedError("_convert_xAI_message is not used by xAI SDK integration")

  def _handle_xAI_error(self, error: Exception) -> Exception:
    """Convert xAI errors to our internal error types.

    Args:
        error: Original xAI error

    Returns:
        Converted exception
    """
    error_str = str(error)

    if "authentication" in error_str.lower() or "api key" in error_str.lower():
      return ProviderAuthenticationError("xAI", error_str)
    elif "rate limit" in error_str.lower():
      # Try to extract retry_after from the error
      return ProviderRateLimitError("xAI", message=error_str)
    elif "quota" in error_str.lower() or "billing" in error_str.lower():
      return ProviderQuotaExceededError("xAI", error_str)
    elif "timeout" in error_str.lower():
      return ProviderTimeoutError("xAI")
    elif "model" in error_str.lower() and "not found" in error_str.lower():
      return ModelNotFoundError("xAI", "unknown")
    elif "content policy" in error_str.lower() or "safety" in error_str.lower():
      return ContentFilterError(error_str)
    elif "token" in error_str.lower() and "limit" in error_str.lower():
      return TokenLimitError(error_str, 0, 0)  # Will be filled with actual values if available
    else:
      return InvalidRequestError(f"xAI API error: {error_str}")

  async def chat(self, request: ChatRequest, **kwargs) -> Union[ChatResponse, AsyncGenerator[StreamChunk, None]]:
    """Send a chat completion request to xAI.

    Args:
        request: Chat completion request
        **kwargs: Additional xAI-specific parameters

    Returns:
        Chat response or async generator for streaming
    """
    # Validate request
    self._validate_request(request)

    # Use semaphore for rate limiting
    async with self._semaphore:
      try:
        # Get model
        model = request.model or self.default_model

        logger.info("Starting xAI chat completion", model=model, reasoning=request.reasoning)

        # Prepare chat.create() parameters
        create_params = {
          "model": model,
          "max_tokens": request.max_tokens or self.default_max_tokens,
          "temperature": request.temperature,
        }

        if request.reasoning:
          create_params.pop("temperature")

        # Add grok-3-high, make reasoning effort high and for grok-3-low, make reasoning effort low
        if model == "grok-3-low" or model == "grok-3-high":
          reasoning_effort = model.split("-")[-1]
          # Replace the low or high model with mini
          create_params["model"] = "grok-3-mini"
          create_params["reasoning_effort"] = reasoning_effort

        # Add reasoning to grok 4 fast if requested
        # Note: grok-4-fast-non-reasoning variant is based on grok-4-fast-reasoning with reasoning disabled
        if model == "grok-4-fast":
          if request.reasoning:
            create_params["model"] = "grok-4-fast-reasoning"
          else:
            create_params["model"] = "grok-4-fast-non-reasoning"

        # Add reasoning to grok 4.1
        if model == "grok-4-1-fast":
          if request.reasoning:
            create_params["model"] = "grok-4-1-fast-reasoning"
          else:
            create_params["model"] = "grok-4-1-fast-non-reasoning"

        # Create chat with xAI SDK
        chat = self.client.chat.create(**create_params)

        # Append messages using xAI SDK's message format
        for msg in request.messages:
          if msg.role == MessageRole.SYSTEM:
            chat.append(system(msg.content if isinstance(msg.content, str) else str(msg.content)))
          elif msg.role == MessageRole.USER:
            chat.append(user(msg.content if isinstance(msg.content, str) else str(msg.content)))
          elif msg.role == MessageRole.ASSISTANT:
            chat.append(assistant(msg.content if isinstance(msg.content, str) else str(msg.content)))

        # Handle streaming vs non-streaming
        if request.stream:
          return self._handle_streaming_response(chat, model)
        else:
          response = await chat.sample()
          return self._handle_chat_response(response, model)

      except Exception as e:
        logger.error(f"xAI chat completion failed: {e}")
        raise self._handle_xAI_error(e)

  def _handle_chat_response(self, response: Response, model: str) -> ChatResponse:
    """Convert xAI response to internal format.

    Args:
        response: xAI SDK Response object
        model: Model name used for the request

    Returns:
        Internal chat response
    """
    # Handle None response
    if not response:
      raise ValueError("xAI response cannot be None")

    # Extract content from xAI Response
    content = response.message.content if hasattr(response, "message") and hasattr(response.message, "content") else ""

    # Extract reasoning_content for grok-3-mini (if available)
    reasoning_content = None
    if hasattr(response, "message") and hasattr(response.message, "reasoning_content"):
      reasoning_content = response.message.reasoning_content

    # Create internal message
    internal_message = Message(
      role=MessageRole.ASSISTANT,
      content=content,
      reasoning_content=reasoning_content,
    )

    # Create choice
    choices = [
      Choice(
        index=0,
        message=internal_message,
        finish_reason=FinishReason.STOP,
      )
    ]

    # Extract usage information
    usage = None
    if hasattr(response, "usage") and response.usage:
      try:
        # Extract reasoning_tokens if available (for reasoning models)
        reasoning_tokens = getattr(response.usage, "reasoning_tokens", None)

        usage = Usage(
          input_tokens=getattr(response.usage, "prompt_tokens", 0),
          output_tokens=getattr(response.usage, "completion_tokens", 0),
          total_tokens=getattr(response.usage, "total_tokens", 0),
          cached_tokens=getattr(response.usage, "cached_prompt_text_tokens", 0),
          reasoning_tokens=reasoning_tokens,
        )
      except Exception as e:
        logger.warning(f"Failed to process usage data: {e}")

    try:
      return ChatResponse(
        id=getattr(response, "id", ""),
        created=int(time.time()),
        model=model,
        choices=choices,
        usage=usage,
      )
    except Exception as e:
      logger.error(f"Failed to create ChatResponse: {e}")
      raise ValueError(f"Failed to create ChatResponse: {e}")

  async def _handle_streaming_response(self, chat, model: str) -> AsyncGenerator[StreamChunk, None]:
    """Handle streaming chat response using xAI SDK with reasoning support.

    Args:
        chat: xAI SDK chat object
        model: Model name

    Yields:
        Stream chunks (reasoning/thinking chunks followed by content chunks)
    """
    # xAI SDK streaming pattern: for response, chunk in chat.stream()
    # response: auto-accumulated response object
    # chunk: individual delta chunk
    async for response, chunk in chat.stream():
      # Extract reasoning/thinking content from chunk (for reasoning models)
      reasoning_delta = getattr(chunk, "reasoning_content", None)

      if reasoning_delta:
        # Yield thinking chunk
        yield StreamChunk(
          id=getattr(response, "id", ""),
          created=int(time.time()),
          model=model,
          choices=[
            {
              "index": 0,
              "delta": {"type": "thinking", "content": reasoning_delta},
              "finish_reason": None,
            }
          ],
        )

      # Extract regular content from chunk
      delta_content = getattr(chunk, "content", "")

      if delta_content:
        # Yield content chunk
        yield StreamChunk(
          id=getattr(response, "id", ""),
          created=int(time.time()),
          model=model,
          choices=[
            {
              "index": 0,
              "delta": {"type": "content", "content": delta_content},
              "finish_reason": None,
            }
          ],
        )

    # After streaming completes, yield usage information if available
    if hasattr(response, "usage") and response.usage:
      try:
        # Extract reasoning_tokens if available (for reasoning models)
        reasoning_tokens = getattr(response.usage, "reasoning_tokens", None)

        usage = Usage(
          input_tokens=getattr(response.usage, "prompt_tokens", 0),
          output_tokens=getattr(response.usage, "completion_tokens", 0),
          total_tokens=getattr(response.usage, "total_tokens", 0),
          cached_tokens=getattr(response.usage, "cached_prompt_text_tokens", 0),
          reasoning_tokens=reasoning_tokens,
        )
        yield StreamChunk(
          id="usage",
          created=int(time.time()),
          model=model,
          choices=[],
          usage=usage,
        )
      except Exception as e:
        logger.warning(f"Failed to process streaming usage data: {e}")

  async def generate_image(self, request: ImageRequest, **kwargs: Any) -> Union[ImageResponse, AsyncGenerator[Any, None]]:
    """Generate images using xAI native SDK (grok-2-image).

    Args:
        request: Image generation request

    Returns:
        ImageResponse

    Note:
        xAI does not support quality, size, or style parameters.
        Streaming is not supported for image generation.
    """
    # Use semaphore for rate limiting
    async with self._semaphore:
      try:
        model = request.model or "grok-2-image-1212"

        logger.info(
          "Starting xAI image generation",
          model=model,
          n=request.n,
        )

        # Determine image format (xAI uses "url" or "base64")
        image_format = "url"
        if request.response_format == "b64_json":
          image_format = "base64"

        # Check if GCP upload is requested
        gcp = None
        if request.upload_to_gcp:
          gcp = get_gcp_client()
          if not gcp:
            logger.warning("GCP upload requested but GCP is not configured properly")

        image_data = []
        timestamp = int(time.time())

        # Generate single or multiple images
        if request.n == 1:
          # Single image generation
          response = await self.client.image.sample(
            model=model,
            prompt=request.prompt,
            image_format=image_format,
          )

          # Process single response
          single_url: Optional[str] = None
          single_b64_json: Optional[str] = None

          if image_format == "url":
            single_url = response.url
            # Upload to GCP if requested
            if gcp and single_url:
              try:
                import aiohttp

                async with aiohttp.ClientSession() as session:
                  async with session.get(single_url) as img_response:
                    if img_response.status == 200:
                      image_bytes = await img_response.read()
                      gcp_key = f"images/xai_{model.replace('-', '_')}_{timestamp}_0.jpg"
                      gcp_url = await gcp.upload_file(
                        file=image_bytes,
                        key=gcp_key,
                        content_type="image/jpeg",
                      )
                      if gcp_url:
                        single_url = gcp_url
                      else:
                        logger.warning("GCP upload returned empty URL, keeping original")
                    else:
                      logger.warning(f"Failed to download xAI image: HTTP {img_response.status}")
              except Exception as e:
                logger.error(f"GCP upload failed: {e}")
          else:
            # base64 format
            image_bytes = response.image  # raw bytes
            # Upload to GCP if requested
            if gcp:
              try:
                gcp_key = f"images/xai_{model.replace('-', '_')}_{timestamp}_0.jpg"
                single_url = await gcp.upload_file(
                  file=image_bytes,
                  key=gcp_key,
                  content_type="image/jpeg",
                )
                if not single_url:
                  # Keep as base64 fallback
                  single_b64_json = base64.b64encode(image_bytes).decode("utf-8")
              except Exception as e:
                logger.error(f"GCP upload failed: {e}")
                # Keep as base64 fallback
                single_b64_json = base64.b64encode(image_bytes).decode("utf-8")
            else:
              # No GCP, use base64
              single_b64_json = base64.b64encode(image_bytes).decode("utf-8")

          image_data.append(
            ImageData(
              url=single_url,
              b64_json=single_b64_json,
              revised_prompt=response.prompt,  # xAI returns revised prompt here
            )
          )

        else:
          # Batch image generation (n > 1)
          responses = await self.client.image.sample_batch(
            model=model,
            prompt=request.prompt,
            n=request.n,
            image_format=image_format,
          )

          for idx, response in enumerate(responses):
            url: Optional[str] = None
            b64_json: Optional[str] = None

            if image_format == "url":
              url = response.url
              # Upload to GCP if requested
              if gcp and url:
                try:
                  import aiohttp

                  async with aiohttp.ClientSession() as session:
                    async with session.get(url) as img_response:
                      if img_response.status == 200:
                        image_bytes = await img_response.read()
                        gcp_key = f"images/xai_{model.replace('-', '_')}_{timestamp}_{idx}.jpg"
                        gcp_url = await gcp.upload_file(
                          file=image_bytes,
                          key=gcp_key,
                          content_type="image/jpeg",
                        )
                        if gcp_url:
                          url = gcp_url
                        else:
                          logger.warning(f"GCP upload returned empty URL for image {idx}, keeping original")
                      else:
                        logger.warning(f"Failed to download xAI image {idx}: HTTP {img_response.status}")
                except Exception as e:
                  logger.error(f"GCP upload failed for image {idx}: {e}")
            else:
              # base64 format
              image_bytes = response.image  # raw bytes
              # Upload to GCP if requested
              if gcp:
                try:
                  gcp_key = f"images/xai_{model.replace('-', '_')}_{timestamp}_{idx}.jpg"
                  url = await gcp.upload_file(
                    file=image_bytes,
                    key=gcp_key,
                    content_type="image/jpeg",
                  )
                  if not url:
                    # Keep as base64 fallback
                    b64_json = base64.b64encode(image_bytes).decode("utf-8")
                except Exception as e:
                  logger.error(f"GCP upload failed for image {idx}: {e}")
                  # Keep as base64 fallback
                  b64_json = base64.b64encode(image_bytes).decode("utf-8")
              else:
                # No GCP, use base64
                b64_json = base64.b64encode(image_bytes).decode("utf-8")

            image_data.append(
              ImageData(
                url=url,
                b64_json=b64_json,
                revised_prompt=response.prompt,  # xAI returns revised prompt here
              )
            )

        return ImageResponse(created=timestamp, data=image_data)

      except Exception as e:
        logger.error(f"xAI image generation failed: {e}")
        raise self._handle_xAI_error(e)

  async def generate_embedding(self, request: EmbeddingRequest, **kwargs) -> EmbeddingResponse:
    """Generate text embeddings.

    Note: xAI does not currently provide embedding models.
    This method raises NotImplementedError.
    """
    raise NotImplementedError("xAI does not support embeddings")

  async def close(self):
    """Close the xAI client and cleanup resources."""
    if self._closed:
      return

    try:
      if hasattr(self, "client") and self.client:
        await self.client.close()
        logger.debug("Closed xAI client")
    except Exception as e:
      logger.error(f"Error closing xAI client: {e}")
    finally:
      self._closed = True
