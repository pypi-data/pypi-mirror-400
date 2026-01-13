# -*- coding: UTF-8 -*-
# @Time : 2025/12/15 23:18 
# @Author : 刘洪波

from __future__ import annotations
import httpx
from typing import List, Optional
from functools import lru_cache
from openai import OpenAI, APIError, RateLimitError, APIConnectionError, InternalServerError, AsyncOpenAI
from tenacity import retry, AsyncRetrying, stop_after_attempt, wait_random_exponential, retry_if_exception_type, before_sleep_log, retry_if_exception
import logging


__all__ = ["OpenAIEmbeddings", "AsyncOpenAIEmbeddings"]


def _should_retry(exc: Exception) -> bool:
    # Explicitly non-retryable errors (even if they are APIError)
    if isinstance(exc, APIError):
        err_code = getattr(exc, 'code', None) or ""
        err_type = getattr(exc, 'type', "") or ""
        # E.g., context_length_exceeded / invalid_request_error / auth error should not be retried
        if err_code in ("context_length_exceeded", "invalid_request_error") or "auth" in err_type:
            return False
    # Fallback: retry known recoverable errors
    return isinstance(exc, (RateLimitError, APIConnectionError, InternalServerError, httpx.TimeoutException, httpx.NetworkError))


class OpenAIEmbeddings:
    """OpenAI-compatible embedding model wrapper class (supports vLLM / LocalAI / Ollama / other OpenAI-compatible services).

    Features:
      - Batch processing + exponential backoff retry
      - Input truncation with warnings
      - Dimension detection caching
      - Supports sync/async extension (this version is synchronous)
    """

    def __init__(self, base_url: str, model_name: str, api_key: str = None, batch_size: int = 32, max_retries: int = 3,
        retry_delay: float = 1.0, max_retry_delay: int = 10, *, client: Optional[OpenAI] = None,
        max_input_length: int = 8191,  logger: Optional[logging.Logger] = None):
        """Initialize OpenAI-compatible embeddings instance.
        
        Args:
            base_url: API endpoint URL.
            api_key: API key.
            model_name: Model name.
            batch_size: Batch size for processing.
            max_retries: Maximum number of retries.
            retry_delay: Retry delay in seconds (supports float), uses exponential backoff strategy.
            max_retry_delay: Maximum retry delay in seconds (must be integer).
            client: External client injection (allows injecting existing client for better testability).
            max_input_length: Maximum input length for the model, used for truncation.
                             OpenAI official limit is 8191 tokens, but character-based truncation is safer.
            logger: Optional custom logger.
        
        Raises:
            ValueError: If base_url is empty.
        """
        if not base_url:
            raise ValueError("base_url cannot be empty")

        self.base_url = base_url.rstrip("/")
        self.api_key = api_key if api_key else ""
        self.model_name = model_name
        self.batch_size = max(1, batch_size)
        self.max_retries = max(0, max_retries)
        self.retry_delay = max(0.1, retry_delay)  # At least 0.1s
        self.max_retry_delay = max(1, max_retry_delay)  # At least 1s
        self.max_input_length = max_input_length

        self.logger = logger or logging.getLogger(__name__)
        # Client injection or create new
        self.client = client or OpenAI(base_url=self.base_url, api_key=self.api_key)

        self.logger.info(f"✅ Initialized OpenAIEmbeddings: model={model_name!r}, endpoint={self.base_url}")

        # Define retry strategy
        self.retry_policy = {
                "stop": stop_after_attempt(self.max_retries),
                "wait": wait_random_exponential(multiplier=self.retry_delay, max=self.max_retry_delay),
                "retry": retry_if_exception(_should_retry),
                "before_sleep": before_sleep_log(self.logger, logging.INFO),
                "reraise": True,
            }
        self.logger.info(f'Retry policy: {self.retry_policy}')


    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents (synchronous).
        
        Args:
            texts: List of texts to embed.
        
        Returns:
            List[List[float]]: List of embedding vectors, each text corresponds to a float vector.
        
        Raises:
            TypeError: If texts is not a list.
        """
        if not texts:
            return []
        if not isinstance(texts, list):
            raise TypeError("texts must be a list")
        return self.batch_embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query text.
        
        Args:
            text: Query text to embed.
        
        Returns:
            List[float]: Embedding vector as a list of floats.
        
        Raises:
            TypeError: If text is not a string.
        """
        if not text:
            text = ""
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        return self.batch_embed_documents([text])[0]

    def _request_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Embedding request with professional retry, core: decorated with @retry.
        
        Args:
            texts: List of texts to embed.
        
        Returns:
            List[List[float]]: List of embedding vectors, each text corresponds to a float vector.
        
        Raises:
            ValueError: If response length does not match input length.
            Exception: If retry still fails.
        """
        @retry(**self.retry_policy)
        def cell():
            if not texts:
                return []
            response = self.client.embeddings.create(
                model=self.model_name,
                input=texts
            )
            if len(response.data) != len(texts):
                raise ValueError(f"Response length {len(response.data)} ≠ input {len(texts)}")

            return [[float(x) for x in item.embedding] for item in response.data]
        return cell()

    def batch_embed_documents(self, texts: List[str], *, batch_size: Optional[int] = None) -> List[List[float]]:
        """Batch embed document list with automatic batching.
        
        Args:
            texts: List of texts to embed.
            batch_size: Optional batch size, if not provided uses the batch_size from initialization.
        
        Returns:
            List[List[float]]: List of embedding vectors, each text corresponds to a float vector.
        """
        if not texts:
            return []

        batch_size = batch_size or self.batch_size
        all_embeddings: List[List[float]] = []

        self.logger.info(f"📦 Starting embedding {len(texts)} texts (batch_size={batch_size})")

        for i in range(0, len(texts), batch_size):
            batch = texts[i: i + batch_size]
            safe_batch = self._prepare_texts(batch)
            batch_embeddings = self._request_embeddings(safe_batch)
            all_embeddings.extend(batch_embeddings)

            processed = min(i + len(batch), len(texts))
            self.logger.info(f"📈 Progress: {processed}/{len(texts)} ({processed / len(texts) * 100:.1f}%)")

        self.logger.info(f"✅ Batch embedding completed: {len(all_embeddings)} vectors")
        return all_embeddings

    def _prepare_texts(self, texts: List[str]) -> List[str]:
        """Preprocess texts: truncation + warning.
        
        If text length exceeds max_input_length, it will be truncated and a warning will be logged.
        
        Args:
            texts: List of texts to preprocess.
        
        Returns:
            List[str]: Preprocessed text list.
        """
        prepared = []
        for text in texts:
            if not isinstance(text, str):
                text = str(text)
            if len(text) > self.max_input_length:
                self.logger.warning(f"Text length ({len(text)}) > max_input_length ({self.max_input_length}), truncated")
                text = text[: self.max_input_length]
            prepared.append(text)
        return prepared

    @lru_cache(maxsize=1)
    def get_embedding_dimension(self) -> int:
        """Detect and cache embedding dimension (thread-safe).
        
        Gets embedding vector dimension by sending a test request.
        
        Returns:
            int: Dimension of the embedding vector.
        
        Raises:
            RuntimeError: If dimension detection fails.
        """
        try:
            test_emb = self.embed_query("dimension detection text")
            dim = len(test_emb)
            self.logger.info(f"🔍 Detected embedding dimension: {dim}")
            return dim
        except Exception as e:
            self.logger.error(f"Dimension detection failed: {e}")
            raise RuntimeError("Unable to determine embedding dimension") from e


    def __repr__(self) -> str:
        return (
            f"OpenAIEmbeddings(model={self.model_name!r}, "
            f"endpoint={self.base_url}, batch_size={self.batch_size})"
        )


class AsyncOpenAIEmbeddings:
    """Fully asynchronous OpenAI-compatible Embeddings wrapper.
    
    - Supports vLLM / LocalAI / Ollama / OpenAI
    - Batch processing
    - Asynchronous exponential backoff retry
    """

    def __init__(
        self,
        base_url: str,
        model_name: str,
        api_key: str | None = None,
        batch_size: int = 32,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        max_retry_delay: int = 10,
        *,
        client: Optional[AsyncOpenAI] = None,
        max_input_length: int = 8191,
        logger: Optional[logging.Logger] = None,
    ):
        """Initialize async OpenAI-compatible embeddings instance.
        
        Args:
            base_url: API endpoint URL.
            api_key: API key.
            model_name: Model name.
            batch_size: Batch size for processing.
            max_retries: Maximum number of retries.
            retry_delay: Retry delay in seconds (supports float), uses exponential backoff strategy.
            max_retry_delay: Maximum retry delay in seconds (must be integer).
            client: External client injection (allows injecting existing client for better testability).
            max_input_length: Maximum input length for the model, used for truncation.
                             OpenAI official limit is 8191 tokens, but character-based truncation is safer.
            logger: Optional custom logger.
        
        Raises:
            ValueError: If base_url is empty.
        """
        if not base_url:
            raise ValueError("base_url cannot be empty")

        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or ""
        self.model_name = model_name
        self.batch_size = max(1, batch_size)
        self.max_retries = max(0, max_retries)
        self.retry_delay = max(0.1, retry_delay)
        self.max_retry_delay = max(1, max_retry_delay)
        self.max_input_length = max_input_length

        self.logger = logger or logging.getLogger(__name__)

        self.client = client or AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )

        self.logger.info(
            f"✅ Initialized AsyncOpenAIEmbeddings: model={model_name!r}, endpoint={self.base_url}"
        )

        # Define retry strategy
        self.retry_policy = {
            "stop": stop_after_attempt(self.max_retries),
            "wait": wait_random_exponential(multiplier=self.retry_delay, max=self.max_retry_delay),
            "retry": retry_if_exception(_should_retry),
            "before_sleep": before_sleep_log(self.logger, logging.INFO),
            "reraise": True,
        }
        self.logger.info(f'Retry policy: {self.retry_policy}')

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents (asynchronous).
        
        Args:
            texts: List of texts to embed.
        
        Returns:
            List[List[float]]: List of embedding vectors, each text corresponds to a float vector.
        
        Raises:
            TypeError: If texts is not a list.
        """
        if not texts:
            return []
        if not isinstance(texts, list):
            raise TypeError("texts must be a list")
        return await self.batch_embed_documents(texts)

    async def embed_query(self, text: str) -> List[float]:
        """Embed a single query text (asynchronous).
        
        Args:
            text: Query text to embed.
        
        Returns:
            List[float]: Embedding vector as a list of floats.
        
        Raises:
            TypeError: If text is not a string.
        """
        if not text:
            text = ""
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        return (await self.batch_embed_documents([text]))[0]

    async def _request_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Asynchronous embedding request with professional retry.
        
        Args:
            texts: List of texts to embed.
        
        Returns:
            List[List[float]]: List of embedding vectors, each text corresponds to a float vector.
        
        Raises:
            ValueError: If response length does not match input length.
            Exception: If retry still fails.
        """
        if not texts:
            return []

        async for attempt in AsyncRetrying(**self.retry_policy):
            with attempt:
                response = await self.client.embeddings.create(
                    model=self.model_name,
                    input=texts,
                )

                if len(response.data) != len(texts):
                    raise ValueError(
                        f"Response length {len(response.data)} ≠ input {len(texts)}"
                    )

                return [
                    [float(x) for x in item.embedding]
                    for item in response.data
                ]

        return []

    async def batch_embed_documents(
        self, texts: List[str], *, batch_size: Optional[int] = None
    ) -> List[List[float]]:
        """Batch embed document list with automatic batching (asynchronous).
        
        Args:
            texts: List of texts to embed.
            batch_size: Optional batch size, if not provided uses the batch_size from initialization.
        
        Returns:
            List[List[float]]: List of embedding vectors, each text corresponds to a float vector.
        """
        if not texts:
            return []

        batch_size = batch_size or self.batch_size
        all_embeddings: List[List[float]] = []

        self.logger.info(
            f"📦 Starting embedding {len(texts)} texts (batch_size={batch_size})"
        )

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            safe_batch = self._prepare_texts(batch)

            batch_embeddings = await self._request_embeddings(safe_batch)
            all_embeddings.extend(batch_embeddings)

            processed = min(i + len(batch), len(texts))
            self.logger.info(
                f"📈 Progress: {processed}/{len(texts)} "
                f"({processed / len(texts) * 100:.1f}%)"
            )

        self.logger.info(f"✅ Batch embedding completed: {len(all_embeddings)} vectors")
        return all_embeddings

    def _prepare_texts(self, texts: List[str]) -> List[str]:
        """Preprocess texts: truncation + warning (async version).
        
        If text length exceeds max_input_length, it will be truncated and a warning will be logged.
        
        Args:
            texts: List of texts to preprocess.
        
        Returns:
            List[str]: Preprocessed text list.
        """
        prepared = []
        for text in texts:
            if not isinstance(text, str):
                text = str(text)
            if len(text) > self.max_input_length:
                self.logger.warning(
                    f"Text length ({len(text)}) > max_input_length "
                    f"({self.max_input_length}), truncated"
                )
                text = text[: self.max_input_length]
            prepared.append(text)
        return prepared

    @lru_cache(maxsize=1)
    async def get_embedding_dimension(self) -> int:
        """Detect and cache embedding dimension (asynchronous + cached).
        
        Gets embedding vector dimension by sending a test request.
        
        Returns:
            int: Dimension of the embedding vector.
        
        Raises:
            RuntimeError: If dimension detection fails.
        """
        try:
            emb = await self.embed_query("dimension detection text")
            dim = len(emb)
            self.logger.info(f"🔍 Detected embedding dimension: {dim}")
            return dim
        except Exception as e:
            self.logger.error(f"Dimension detection failed: {e}")
            raise RuntimeError("Unable to determine embedding dimension") from e

    def __repr__(self) -> str:
        return (
            f"AsyncOpenAIEmbeddings(model={self.model_name!r}, "
            f"endpoint={self.base_url}, batch_size={self.batch_size})"
        )
