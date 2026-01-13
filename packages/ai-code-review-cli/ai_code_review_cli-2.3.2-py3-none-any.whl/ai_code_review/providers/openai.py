"""OpenAI provider implementation using LangChain."""

from __future__ import annotations

from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from ai_code_review.models.config import Config
from ai_code_review.providers.base import BaseAIProvider
from ai_code_review.utils.constants import SYSTEM_PROMPT_ESTIMATED_CHARS
from ai_code_review.utils.exceptions import AIProviderError


class OpenAIProvider(BaseAIProvider):
    """OpenAI GPT AI provider implementation.

    Supports GPT-5.x family models with 1M token context windows:
    - gpt-5-mini: Balanced quality/cost (~$0.40/$1.60 per M tokens)
    - gpt-5-nano: Ultra-cheap for synthesis (~$0.10/$0.40 per M tokens)
    - gpt-4o: High capability, 128K context ($2.50/$10.00 per M tokens)
    - gpt-4o-mini: Fast and economical ($0.15/$0.60 per M tokens)

    Note: GPT-5.1 Codex models use /v1/responses API only and are NOT
    compatible with LangChain's ChatOpenAI.
    """

    def __init__(self, config: Config) -> None:
        """Initialize OpenAI provider."""
        super().__init__(config)

    def _create_client(self) -> BaseChatModel:
        """Create ChatOpenAI client instance."""
        try:
            import structlog

            logger = structlog.get_logger()

            logger.info(
                "Creating OpenAI client",
                model=self.model_name,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                timeout=self.config.llm_timeout,
                max_retries=self.config.llm_max_retries,
            )

            return ChatOpenAI(
                model=self.model_name,
                api_key=(
                    self.config.ai_api_key if self.config.ai_api_key else SecretStr("")
                ),
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,  # type: ignore[call-arg]
                timeout=self.config.llm_timeout,
                max_retries=self.config.llm_max_retries,
            )
        except Exception as e:
            raise AIProviderError(
                f"Failed to create OpenAI client: {e}", "openai"
            ) from e

    def is_available(self) -> bool:
        """Check if OpenAI API is available."""
        if self.config.dry_run:
            return True

        # For cloud providers, we assume availability if we have an API key
        # Real availability check would require an actual API call
        return bool(self.config.ai_api_key)

    def get_adaptive_context_size(
        self,
        diff_size_chars: int,
        project_context_chars: int = 0,
        system_prompt_chars: int = SYSTEM_PROMPT_ESTIMATED_CHARS,
    ) -> int:
        """Get context size adaptively based on content size and config.

        GPT-5.x models have excellent context handling:
        - Input: ~1M tokens (GPT-5, GPT-5-mini, GPT-5-nano)
        - Output: ~100K tokens

        Very generous limits, similar to Gemini.

        Args:
            diff_size_chars: Size of the diff content in characters
            project_context_chars: Size of project context content in characters
            system_prompt_chars: Estimated size of system prompt in characters

        Returns:
            Optimal context window size considering all content
        """
        # Calculate total content size
        total_content_chars = (
            diff_size_chars + project_context_chars + system_prompt_chars
        )

        # Manual override always takes precedence
        if self.config.big_diffs:
            return 400_000  # 400K - manual big-diffs flag (generous limit)

        # Auto-detect based on total content size (very generous like Gemini)
        elif total_content_chars > 200_000:  # > 200K chars (~80K tokens)
            return 400_000  # 400K - very large content
        elif total_content_chars > 100_000:  # > 100K chars (~40K tokens)
            return 256_000  # 256K - large content
        elif total_content_chars > 30_000:  # > 30K chars (~12K tokens)
            return 128_000  # 128K - medium content
        else:
            return 64_000  # 64K - standard

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on OpenAI service.

        Note: This performs a lightweight check without making actual API calls.
        API key validation is already done by Pydantic during config initialization.
        Actual API connectivity will be verified during the first real API call.
        """
        try:
            if self.config.dry_run:
                return {
                    "status": "healthy",
                    "dry_run": True,
                    "model": self.model_name,
                    "provider": "openai",
                }

            # API key validation is already done by Pydantic validators in Config
            # If we reached here, the API key is present and non-empty
            # We don't make actual API calls here to avoid:
            # 1. Unnecessary API usage/costs
            # 2. Slow health checks
            # 3. Potential rate limiting
            return {
                "status": "healthy",
                "api_key_configured": True,
                "model": self.model_name,
                "provider": "openai",
                "note": "API key validated. Connectivity will be verified on first use.",
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "provider": "openai",
            }
