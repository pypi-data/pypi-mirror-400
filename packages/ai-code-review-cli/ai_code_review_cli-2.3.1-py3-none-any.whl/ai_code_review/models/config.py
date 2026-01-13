"""Configuration models for AI Code Review tool."""

from __future__ import annotations

import os
import re
import string
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import (
    AliasChoices,
    BaseModel,
    Field,
    SecretStr,
    ValidationInfo,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

from ai_code_review.models.settings_sources import ConfigFileSettingsSource
from ai_code_review.utils.constants import MAX_COMMENTS_TO_FETCH

# Default file exclusion patterns - defined once to avoid duplication
_DEFAULT_EXCLUDE_PATTERNS = [
    "*.lock",  # All lockfiles (uv.lock, pdm.lock, etc.)
    "package-lock.json",  # npm lockfile
    "yarn.lock",  # Yarn lockfile
    "Pipfile.lock",  # Pipenv lockfile
    "poetry.lock",  # Poetry lockfile
    "pnpm-lock.yaml",  # PNPM lockfile
    "*.min.js",  # Minified JS files
    "*.min.css",  # Minified CSS files
    "*.map",  # Source map files
    "node_modules/**",  # Node modules (top level)
    "**/node_modules/**",  # Node modules (nested)
    "__pycache__/**",  # Python cache (top level)
    "**/__pycache__/**",  # Python cache (nested)
    "dist/**",  # Build distributions (top level)
    "**/dist/**",  # Build distributions (nested)
    "build/**",  # Build directories (top level)
    "**/build/**",  # Build directories (nested)
    "*.egg-info/**",  # Python egg info (top level)
    "**/*.egg-info/**",  # Python egg info (nested)
]


# PlatformProvider moved here to avoid circular imports
class PlatformProvider(str, Enum):
    """Supported code hosting platforms."""

    FORGEJO = "forgejo"
    GITLAB = "gitlab"
    GITHUB = "github"
    LOCAL = "local"


class AIProvider(str, Enum):
    """Supported AI providers."""

    OLLAMA = "ollama"
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


# Cloud AI providers that require API keys
CLOUD_PROVIDERS = {
    AIProvider.GEMINI,
    AIProvider.OPENAI,
    AIProvider.ANTHROPIC,
}

# Default AI provider
DEFAULT_AI_PROVIDER = AIProvider.GEMINI

# Provider-specific max_chars limits based on model capabilities
PROVIDER_DEFAULT_MAX_CHARS = {
    AIProvider.GEMINI: 350_000,  # 350K - Gemini 2.5+ (optimized for quality/performance)
    AIProvider.ANTHROPIC: 150_000,  # 150K - Claude 3.5 (200K tokens input)
    AIProvider.OLLAMA: 50_000,  # 50K - Local models (24K tokens max)
    AIProvider.OPENAI: 300_000,  # 300K - GPT-5.x (1M tokens input)
}
"""Provider-specific max_chars defaults based on model context windows.

Maps each AI provider to its optimal max_chars limit based on the model's
actual context window capabilities:

- Gemini:    200,000 chars (~80K tokens) - 2M token context window
- Anthropic: 150,000 chars (~60K tokens) - 200K token context window
- Ollama:     50,000 chars (~20K tokens) - 24K token max context
- OpenAI:    300,000 chars (~120K tokens) - 1M token context window

These limits are automatically applied by Config.set_adaptive_max_chars()
when max_chars is not explicitly configured in the config file or CLI.
"""

# Default max_chars for unknown providers
DEFAULT_MAX_CHARS = 100_000
"""Default max_chars for unknown or future AI providers.

Provides a safe fallback limit when a provider is not found in
PROVIDER_DEFAULT_MAX_CHARS mapping.
"""


class SkipReviewConfig(BaseModel):
    """Configuration for automatic review skipping."""

    enabled: bool = Field(
        default=True, description="Enable/disable automatic review skipping"
    )

    # Explicit keywords (case-insensitive, checked in title + description)
    keywords: list[str] = Field(
        default=[
            "[skip ai-review]",
            "[no-review]",
            "[bot]",
            "[skip-review]",
            "[automated]",
        ],
        description="Keywords to trigger review skipping (case-insensitive)",
    )

    # Regex patterns for automated tools (checked against title only)
    patterns: list[str] = Field(
        default=[
            # Dependency updates (comprehensive patterns)
            r"^(chore|build|ci|feat|fix)\(deps?\):",
            r"^bump\s+.*\s+from\s+[\d.]+\s+to\s+[\d.]+",
            # Version releases and bumps
            r"^(chore|release):\s*(release|version|bump)\s+v?\d+\.\d+",
            r"^bump:\s*version",
            # Auto-generated changes
            r"^\[automated\]",
            r"^auto.*update",
        ],
        description="Regex patterns for automated changes (case-insensitive matching)",
    )

    # Author patterns (for known bots)
    bot_authors: list[str] = Field(
        default=[
            "renovate[bot]",
            "dependabot[bot]",
            "github-actions[bot]",
            "gitlab-ci-token",
            "allcontributors[bot]",
            "greenkeeper[bot]",
            "snyk-bot",
            "auto-gitlab-bot",
            "forgejo-actions",
        ],
        description="Known bot author patterns for automatic skipping",
    )

    # Documentation-only patterns (only used if skip_documentation_only is True)
    documentation_patterns: list[str] = Field(
        default=[
            r"^docs?(\(.+\))?:\s+.*",  # docs: or docs(scope):
        ],
        description="Regex patterns for documentation-only changes",
    )

    # Feature flags for intelligent detection
    skip_dependency_updates: bool = Field(
        default=True, description="Skip reviews for dependency update PRs/MRs"
    )

    skip_documentation_only: bool = Field(
        default=False,  # Conservative default - can be enabled per project
        description="Skip reviews for documentation-only changes",
    )

    skip_bot_authors: bool = Field(
        default=True, description="Skip reviews from known bot authors"
    )

    skip_draft_prs: bool = Field(
        default=True, description="Skip reviews for draft/WIP pull/merge requests"
    )

    @field_validator("patterns", "documentation_patterns")
    @classmethod
    def validate_patterns(cls, v: list[str]) -> list[str]:
        """Validate regex patterns to prevent ReDoS and ensure they compile."""
        import re

        validated_patterns = []
        for pattern in v:
            try:
                # Test that pattern compiles
                re.compile(pattern)
                validated_patterns.append(pattern)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern '{pattern}': {e}") from e

        return validated_patterns


# Default models for each AI provider
_DEFAULT_MODELS = {
    AIProvider.OLLAMA: "qwen2.5-coder:14b",
    AIProvider.GEMINI: "gemini-3-pro-preview",
    AIProvider.ANTHROPIC: "claude-sonnet-4-5",
    AIProvider.OPENAI: "gpt-5-mini",  # 1M context, good quality/cost balance
}


# Default synthesis models (fast/cheap variants for preprocessing)
_DEFAULT_SYNTHESIS_MODELS = {
    AIProvider.OLLAMA: "qwen2.5-coder:14b",  # Use same model to avoid loading two models in memory
    AIProvider.GEMINI: "gemini-3-flash-preview",
    AIProvider.ANTHROPIC: "claude-haiku-4-5",
    AIProvider.OPENAI: "gpt-5-nano",  # Ultra-cheap for synthesis
}


class Config(BaseSettings):
    """Main configuration for AI Code Review tool."""

    # dry_run must come before all fields it might affect the
    # validation of - api keys etc.
    dry_run: bool = Field(default=False, description="Dry run mode (no API calls)")

    # Platform configuration
    # Must come *before* all platform-dependent fields
    platform_provider: PlatformProvider = Field(
        # this looks weird but our 'before' validator takes care of it
        default=None,
        description="Code hosting platform to use",
        validate_default=True,
    )

    # Forgejo configuration
    forgejo_token: SecretStr | None = Field(
        default=None, description="Forgejo Personal Access Token"
    )
    forgejo_url: str = Field(
        default="https://codeberg.org/api/v1", description="Forgejo API URL"
    )

    # GitLab configuration
    gitlab_token: SecretStr | None = Field(
        default=None, description="GitLab Personal Access Token"
    )
    gitlab_url: str = Field(
        default="https://gitlab.com", description="GitLab instance URL"
    )

    # GitHub configuration
    github_token: SecretStr | None = Field(
        default=None, description="GitHub Personal Access Token"
    )
    github_url: str = Field(
        default="https://api.github.com", description="GitHub API URL"
    )

    # SSL configuration
    ssl_verify: bool = Field(
        default=True,
        description="Verify SSL certificates (disable only for development)",
    )
    ssl_cert_path: str | None = Field(
        default=None,
        description="Path to SSL certificate file for custom CA or self-signed certificates",
    )
    ssl_cert_url: str | None = Field(
        default=None,
        description="URL to download SSL certificate automatically (alternative to ssl_cert_path)",
    )
    ssl_cert_cache_dir: str = Field(
        default=".ssl_cache",
        description="Directory to cache downloaded SSL certificates",
    )

    # AI provider configuration
    # ai_provider must come *before* ai_model and synthesis_model
    ai_provider: AIProvider = Field(
        default=DEFAULT_AI_PROVIDER, description="AI provider to use"
    )
    ai_model: str = Field(
        # this looks weird but our 'before' validator takes care of it
        default=None,
        description="AI model name (auto-selects default model if not specified)",
        validate_default=True,
    )
    ai_api_key: SecretStr | None = Field(
        default=None, description="API key for cloud AI providers"
    )

    # Ollama specific
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama server URL for local development",
    )
    http_timeout: float = Field(
        default=5.0,
        description="HTTP request timeout in seconds for API calls",
        gt=0.0,
    )

    # LLM API timeout and retry configuration
    llm_timeout: float = Field(
        default=90.0,
        description="Timeout in seconds for LLM API calls (cloud providers). Set to 90s to provide adequate margin for Gemini-3 with thinking_budget=512 (typically completes in ~60s).",
        gt=0.0,
    )
    gemini_thinking_budget: int | None = Field(
        default=512,
        description="Gemini thinking budget in tokens for internal reasoning (Gemini 2.5+). Lower values (256-512) reduce latency and costs, suitable for CI/CD. Higher values (1024+) enable deeper reasoning. Set to 0 to disable thinking (gemini-2.5-flash only). Note: gemini-2.5-pro has minimum of 128 tokens.",
        ge=0,
    )
    llm_max_retries: int = Field(
        default=2,
        description="Maximum number of retries for LLM API calls. Lower values fail faster in CI/CD.",
        ge=0,
    )

    # AI model parameters
    temperature: float = Field(
        default=0.0,
        description="Temperature for AI responses (0.0-2.0, lower = more deterministic)",
        ge=0.0,
        le=2.0,
    )
    max_tokens: int = Field(
        default=8000,
        description="Maximum tokens for AI response generation",
        gt=0,
    )

    # Review context preprocessing
    enable_review_context: bool = Field(
        default=True,
        description="Enable fetching previous reviews/comments for context",
    )
    enable_review_synthesis: bool = Field(
        default=True,
        description="Enable preprocessing of reviews with fast model for synthesis (reduces tokens)",
    )
    synthesis_model: str = Field(
        # this looks weird but our 'before' validator takes care of it
        default=None,
        description="Model for review synthesis (auto-selects fast model if not specified)",
        validate_default=True,
    )
    synthesis_max_tokens: int = Field(
        default=2000,
        description="Maximum tokens for synthesis output",
        gt=0,
    )
    max_comments_to_fetch: int = Field(
        default=MAX_COMMENTS_TO_FETCH,
        description="Maximum number of comments to fetch from platform API for synthesis",
        gt=0,
    )

    # Content processing
    max_chars: int | None = Field(
        default=None,
        description=(
            "Maximum characters to process from diff. "
            "If not specified, automatically adapts based on AI provider's "
            "context window capabilities (see PROVIDER_DEFAULT_MAX_CHARS)"
        ),
    )
    max_files: int = Field(
        default=100, description="Maximum number of files to process"
    )

    # CI/CD automatic variables (platform-agnostic)
    repository_path: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "GITHUB_REPOSITORY", "FORGEJO_REPOSITORY", "CI_PROJECT_PATH"
        ),
        description="Repository path (CI_PROJECT_PATH for GitLab, GITHUB_REPOSITORY for GitHub, FORGEJO_REPOSITORY for Forgejo)",
    )
    pull_request_number: int | None = Field(
        default=None,
        validation_alias=AliasChoices("CI_MERGE_REQUEST_IID"),
        description="Pull/merge request number (CI_MERGE_REQUEST_IID for GitLab, derived from GitHub or Forgejo event)",
    )
    server_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "GITHUB_API_URL", "FORGEJO_API_URL", "CI_SERVER_URL"
        ),
        description="Platform server URL (CI_SERVER_URL for GitLab, GITHUB_API_URL for GitHub, FORGEJO_API_URL for Forgejo)",
    )

    # Legacy GitLab CI/CD variables (for backward compatibility)
    ci_project_path: str | None = Field(
        default=None,
        description="GitLab CI project path (deprecated, use repository_path)",
    )
    ci_merge_request_iid: int | None = Field(
        default=None,
        description="GitLab CI merge request IID (deprecated, use pull_request_number)",
    )
    ci_server_url: str | None = Field(
        default=None, description="GitLab CI server URL (deprecated, use server_url)"
    )

    # Optional features
    language_hint: str | None = Field(
        default=None, description="Programming language hint"
    )
    enable_project_context: bool = Field(
        default=True,
        description="Enable loading project context from .ai_review/project.md file",
    )
    project_context_file: str = Field(
        default=".ai_review/project.md",
        description="Path to project context file (relative to repository root)",
    )
    team_context_file: str | None = Field(
        default=None,
        description="Team/organization context file (local path or URL, higher priority than project context)",
    )
    include_mr_summary: bool = Field(
        default=True,
        description="Include MR Summary section in reviews (disable for shorter, code-focused reviews)",
    )

    # Execution options
    big_diffs: bool = Field(
        default=False,
        description="Force larger context window - auto-activated for large diffs/content",
    )
    health_check: bool = Field(
        default=False, description="Perform health check on all components and exit"
    )
    post: bool = Field(
        default=False, description="Post review as MR comment to GitLab/GitHub/Forgejo"
    )

    # Output options
    output_file: str | None = Field(
        default=None,
        description="Save review output to file (default: display in terminal)",
    )

    # Local mode options
    target_branch: str = Field(
        default="main", description="Target branch for local comparison (default: main)"
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    # File filtering
    exclude_patterns: list[str] = Field(
        default=_DEFAULT_EXCLUDE_PATTERNS,
        description="Glob patterns for files to exclude from AI review",
    )

    # Complete diff fetching timeout (advanced option)
    diff_download_timeout: int = Field(
        default=30,
        description="Timeout for downloading complete diffs via HTTP (seconds)",
    )

    # Configuration file options
    no_config_file: bool = Field(
        default=False,
        validation_alias=AliasChoices("no_config_file", "NO_CONFIG_FILE"),
        description="Skip loading config file (auto-detected or specified)",
    )
    config_file: str | None = Field(
        default=None,
        validation_alias=AliasChoices("config_file", "CONFIG_FILE"),
        description="Custom config file path",
    )

    # Skip review configuration
    skip_review: SkipReviewConfig = Field(
        default_factory=SkipReviewConfig,
        description="Configuration for automatic review skipping",
    )

    @field_validator("gitlab_url", "github_url", "forgejo_url", "ollama_base_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format."""
        if not v:
            raise ValueError("URL cannot be empty")

        url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        if not re.match(url_pattern, v):
            raise ValueError(f"Invalid URL format: {v}")

        return v.rstrip("/")  # Remove trailing slash for consistency

    @field_validator("ssl_cert_path")
    @classmethod
    def validate_ssl_cert_path(cls, v: str | None) -> str | None:
        """Validate SSL certificate file path."""
        if v is None:
            return None

        if not v.strip():
            raise ValueError("SSL certificate path cannot be empty")

        if not os.path.isfile(v):
            raise ValueError(f"SSL certificate file not found: {v}")

        if not os.access(v, os.R_OK):
            raise ValueError(f"SSL certificate file is not readable: {v}")

        return v

    @field_validator("ssl_cert_url")
    @classmethod
    def validate_ssl_cert_url(cls, v: str | None) -> str | None:
        """Validate SSL certificate URL format."""
        if v is None:
            return None

        if not v.strip():
            raise ValueError("SSL certificate URL cannot be empty")

        url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        if not re.match(url_pattern, v):
            raise ValueError(f"Invalid SSL certificate URL format: {v}")

        return v.rstrip("/")

    @field_validator("ssl_cert_cache_dir")
    @classmethod
    def validate_ssl_cert_cache_dir(cls, v: str) -> str:
        """Validate SSL certificate cache directory."""
        if not v.strip():
            raise ValueError("SSL certificate cache directory cannot be empty")
        return v.strip()

    @field_validator("ai_provider", mode="before")
    @classmethod
    def set_ai_provider(cls, provider: Any) -> Any:
        """Force to AIProvider if string."""
        if isinstance(provider, str):
            try:
                return AIProvider(provider)
            except ValueError as err:
                raise ValueError(
                    f"ai_provider '{provider}' is not a valid choice. "
                    f"Available providers: {[prov.value for prov in AIProvider]}"
                ) from err
        return provider

    @field_validator("ai_model", "synthesis_model", mode="before")
    @classmethod
    def set_ai_model(cls, model: Any, info: ValidationInfo) -> Any:
        """Set default models for provider if not set."""
        if isinstance(model, str):
            model = model.strip()
        if model:
            return model
        # can rely on this being set because ai_provider is
        # defined before ai_model
        provider = info.data.get("ai_provider")
        if not provider:
            # this would only be encountered if ai_provider validation
            # fails, so let's just bail as we can't do anything useful
            return model
        models = _DEFAULT_MODELS
        if info.field_name == "synthesis_model":
            models = _DEFAULT_SYNTHESIS_MODELS
        if provider not in models:
            raise ValueError(
                f"No default model defined for provider '{provider.value}'. "
                f"Available models: {list(models.keys())}"
            )
        return models[provider]

    @field_validator("ai_model")
    @classmethod
    def validate_ai_model(cls, model: str, info: ValidationInfo) -> str:
        """Validate AI model name format."""
        # Basic validation: no special characters that could cause issues
        if any(char in model for char in ["\n", "\r", "\t", "\0"]):
            raise ValueError("AI model name contains invalid characters")
        # Cannot be empty
        if not (model := model.strip()):
            raise ValueError("AI model cannot be empty")

        # can rely on this being set because ai_provider is
        # defined before ai_model
        provider = info.data.get("ai_provider")

        # Check for obvious mismatches
        if provider == AIProvider.OLLAMA:
            # Ollama shouldn't use cloud provider model names
            if model.startswith(("gemini-", "gpt-", "claude-")):
                raise ValueError(
                    f"AI model '{model}' appears to be for a cloud provider, "
                    "but you selected Ollama provider. "
                    "For Ollama, try a model like 'qwen2.5-coder:7b'. "
                    "Or change ai_provider to match your model choice."
                )
        elif provider == AIProvider.GEMINI:
            # Gemini should use valid gemini models
            # Valid models based on https://ai.google.dev/gemini-api/docs/models
            valid_gemini_models = {
                # Current models
                "gemini-3-pro-preview",
                "gemini-3-flash-preview",
                "gemini-2.5-pro",
                "gemini-2.5-flash",
                "gemini-2.5-flash-lite",
                "gemini-2.0-flash",
                "gemini-2.0-flash-lite",
                # Deprecated but still available
                "gemini-1.5-pro",
                "gemini-1.5-flash",
                "gemini-1.5-flash-8b",
            }

            # Also allow versioned models (e.g., gemini-2.5-pro-001) and preview models
            is_valid_model = (
                model in valid_gemini_models
                or any(
                    model.startswith(valid_model + "-")
                    for valid_model in valid_gemini_models
                )
                or "preview" in model
                or "exp" in model  # Preview/experimental variants
            )

            if not is_valid_model:
                suggested_model = _DEFAULT_MODELS[AIProvider.GEMINI]
                raise ValueError(
                    f"AI model '{model}' is not a valid Gemini model. "
                    f"Valid models include: {', '.join(sorted(valid_gemini_models))}. "
                    f"For current recommendation, try '{suggested_model}'. "
                    f"Or change ai_provider to match your model choice."
                )
        elif provider == AIProvider.OPENAI:
            # OpenAI should use valid GPT models
            # Valid models based on https://platform.openai.com/docs/models
            # NOTE: GPT-5.x Codex models use /v1/responses API ONLY (not compatible
            # with LangChain ChatOpenAI). Regular GPT-5.x models work fine.
            valid_openai_models = {
                # GPT-5.x family (1M context, compatible with chat/completions API)
                "gpt-5-nano",
                "gpt-5-mini",
                "gpt-5",
                "gpt-5.1",
                "gpt-5.1-pro",
                "gpt-5.2",
                "gpt-5.2-pro",
                # GPT-4.x family
                "gpt-4.1",
                "gpt-4.1-mini",
                "gpt-4.1-nano",
                "gpt-4o",
                "gpt-4o-mini",
                # O-series (reasoning models)
                "o1",
                "o1-mini",
                "o1-preview",
                "o3-mini",
                "o4-mini",
                # Legacy
                "gpt-4-turbo",
                "gpt-4",
            }

            # Models that use /v1/responses API ONLY (NOT compatible with LangChain)
            # See: https://platform.openai.com/docs/models/gpt-5.1-codex
            responses_api_only_models = {
                "gpt-5.1-codex",
                "gpt-5.1-codex-mini",
            }

            # Check if model uses the incompatible /v1/responses API
            uses_responses_api = model in responses_api_only_models or any(
                model.startswith(resp_model + "-")
                for resp_model in responses_api_only_models
            )

            if uses_responses_api:
                raise ValueError(
                    f"AI model '{model}' uses OpenAI's /v1/responses API which is "
                    f"not compatible with LangChain's ChatOpenAI. "
                    f"Please use a compatible model: gpt-5-mini (recommended), "
                    f"gpt-5-nano (fast/cheap), or gpt-4o."
                )

            # Allow versioned models (e.g., gpt-4o-2024-11-20) and preview variants
            is_valid_model = (
                model in valid_openai_models
                or any(
                    model.startswith(valid_model + "-")
                    for valid_model in valid_openai_models
                )
                or "preview" in model
            )

            if not is_valid_model:
                suggested_model = _DEFAULT_MODELS[AIProvider.OPENAI]
                raise ValueError(
                    f"AI model '{model}' may not be a valid OpenAI model. "
                    f"Recommended: gpt-5-mini (quality), gpt-5-nano (cheap). "
                    f"Or try '{suggested_model}'."
                )

        return model

    @field_validator("ai_api_key")
    @classmethod
    def validate_ai_api_key(
        cls, key: SecretStr | None, info: ValidationInfo
    ) -> SecretStr | None:
        """Ensure ai_api_key is non-empty for cloud providers, except
        in dry_run mode.
        """
        if info.data.get("dry_run", False):
            return key
        # can rely on this being set because ai_provider is
        # defined before ai_api_key
        provider = info.data.get("ai_provider")
        if provider and provider in CLOUD_PROVIDERS:
            # Check if API key is empty
            if not key or not key.get_secret_value().strip():
                provider_urls = {
                    AIProvider.GEMINI: "https://makersuite.google.com/app/apikey",
                    AIProvider.OPENAI: "https://platform.openai.com/api-keys",
                    AIProvider.ANTHROPIC: "https://console.anthropic.com/",
                }
                url = provider_urls.get(provider, "provider website")
                raise ValueError(
                    f"API key is required for cloud provider '{provider.value}'. "
                    f"Get one at: {url} "
                    f"Set it as AI_API_KEY environment variable or in .env file."
                )
        return key

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate logging level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v.upper()

    @field_validator("team_context_file")
    @classmethod
    def validate_team_context_file(cls, v: str | None) -> str | None:
        """Validate team context file path or URL."""
        if v is None:
            return None

        if not v.strip():
            return None

        # If it's a URL, validate format
        if v.startswith(("http://", "https://")):
            url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
            if not re.match(url_pattern, v):
                raise ValueError(f"Invalid team context URL format: {v}")
            return v.strip()

        # If it's a local path, don't validate existence (file might not exist yet)
        return v.strip()

    @field_validator("platform_provider", mode="before")
    @classmethod
    def set_platform_provider(cls, value: Any) -> Any:
        """Auto-detect platform from environment if it is not set. If
        set as a string, force it to a PlatformProvider.
        """
        if isinstance(value, str):
            value = value.strip()
            try:
                return PlatformProvider(value)
            except ValueError as err:
                raise ValueError(
                    f"platform '{value}' is not a valid choice. "
                    f"Available platforms: {[prov.value for prov in PlatformProvider]}"
                ) from err
        if not value:
            # GitLab CI detection (require both GITLAB_CI and data availability)
            if os.getenv("GITLAB_CI") == "true" and os.getenv("CI_PROJECT_PATH"):
                return PlatformProvider.GITLAB

            # Forgejo Actions detection (require both FORGEJO_ACTIONS and data availability)
            # must come before GitHub because Forgejo also sets GitHub variables for
            # compatibility
            if os.getenv("FORGEJO_ACTIONS") == "true" and os.getenv(
                "FORGEJO_REPOSITORY"
            ):
                return PlatformProvider.FORGEJO

            # GitHub Actions detection (require both GITHUB_ACTIONS and data availability)
            if os.getenv("GITHUB_ACTIONS") == "true" and os.getenv("GITHUB_REPOSITORY"):
                return PlatformProvider.GITHUB

            # Fallback: detect by data availability only (safer for edge cases)
            if os.getenv("FORGEJO_REPOSITORY"):
                return PlatformProvider.FORGEJO
            if os.getenv("GITHUB_REPOSITORY"):
                return PlatformProvider.GITHUB
            if os.getenv("CI_PROJECT_PATH"):
                return PlatformProvider.GITLAB

            # Default to GitLab for backward compatibility
            return PlatformProvider.GITLAB
        else:
            # Rely on pydantic type validation
            return value

    @field_validator("platform_provider")
    @classmethod
    def validate_platform_environment(cls, value: PlatformProvider) -> PlatformProvider:
        if value != PlatformProvider.LOCAL:
            # no requirements
            return value
        # Check if we're in a git repository (only when not testing)
        current_dir = Path.cwd()
        git_dir = current_dir / ".git"
        is_git_repo = git_dir.exists() or any(
            (parent / ".git").exists() for parent in current_dir.parents
        )

        if not is_git_repo and not os.getenv("PYTEST_CURRENT_TEST"):
            raise ValueError(
                "LOCAL platform requires running from within a git repository. "
                "Please run the command from a directory that contains a .git folder."
            )
        return value

    @field_validator("gitlab_token")
    @classmethod
    def validate_gitlab_token(
        cls, token: SecretStr | None, info: ValidationInfo
    ) -> SecretStr | None:
        """Validate GitLab token format and provide helpful error message."""
        required = (
            "GitLab Personal Access Token is required and cannot be empty. "
            "Get one at: https://gitlab.com/-/profile/personal_access_tokens "
            "with scopes: api, read_user, read_repository. "
            "Set it as GITLAB_TOKEN environment variable or in .env file."
        )
        if token is None:
            pp = info.data.get("platform_provider")
            # can rely on this being set because platform_provider is
            # defined before all tokens
            if pp == PlatformProvider.GITLAB:
                raise ValueError(required)
            return None

        if not (token_value := token.get_secret_value().strip()):
            raise ValueError(required)

        return SecretStr(token_value)

    @field_validator("github_token")
    @classmethod
    def validate_github_token(
        cls, token: SecretStr | None, info: ValidationInfo
    ) -> SecretStr | None:
        """Validate GitHub token format and provide helpful error message."""
        required = (
            "GitHub Personal Access Token is required and cannot be empty. "
            "Get one at: https://github.com/settings/tokens "
            "with scopes: repo, read:org. "
            "Set it as GITHUB_TOKEN environment variable or in .env file."
        )
        pp = info.data.get("platform_provider")
        if pp == PlatformProvider.FORGEJO:
            # bail as Forgejo sets its own token as GITHUB_TOKEN for
            # compatibility; we will validate it as FORGEJO_TOKEN
            return token
        if token is None:
            # can rely on this being set because platform_provider is
            # defined before all tokens
            if pp == PlatformProvider.GITHUB:
                raise ValueError(required)
            return None

        if not (token_value := token.get_secret_value().strip()):
            raise ValueError(required)

        # Allow test tokens (common patterns used in testing)
        test_patterns = ("test", "mock", "fake", "dummy", "example")
        if any(pattern in token_value.lower() for pattern in test_patterns):
            return SecretStr(token_value)

        # Validate format for real GitHub tokens
        # GitHub classic tokens start with 'ghp_', fine-grained tokens start with 'github_pat_'
        if len(token_value) > 20:
            if not token_value.startswith(
                ("ghp_", "github_pat_", "gho_", "ghu_", "ghs_", "ghr_")
            ):
                raise ValueError(
                    "GitHub token format appears invalid. "
                    "GitHub tokens typically start with: ghp_ (personal), "
                    "github_pat_ (fine-grained), gho_ (OAuth), ghu_ (user), "
                    "ghs_ (server), or ghr_ (refresh). "
                    "Get a valid token at: https://github.com/settings/tokens"
                )

        return SecretStr(token_value)

    @field_validator("forgejo_token")
    @classmethod
    def validate_forgejo_token(
        cls, token: SecretStr | None, info: ValidationInfo
    ) -> SecretStr | None:
        """Validate Forgejo token format and provide helpful error message."""
        required = (
            "Forgejo token is required and cannot be empty. "
            "Get one at: https://codeberg.org/user/settings/applications "
            "with scopes: issue, read:repository, read:organization. "
            "Set it as FORGEJO_TOKEN environment variable or in .env file."
        )
        if token is None:
            pp = info.data.get("platform_provider")
            # can rely on this being set because platform_provider is
            # defined before all tokens
            if pp == PlatformProvider.FORGEJO:
                raise ValueError(required)
            return None

        if not (token_value := token.get_secret_value().strip()):
            raise ValueError(required)

        # Allow test tokens (common patterns used in testing)
        test_patterns = ("test", "mock", "fake", "dummy", "example")
        if any(pattern in token_value.lower() for pattern in test_patterns):
            return SecretStr(token_value)

        # Validate format for real Forgejo tokens
        # They are 40-character long hex strings
        if len(token_value) != 40 or any(
            char not in string.hexdigits for char in token_value
        ):
            raise ValueError(
                "Forgejo token format appears invalid. "
                "Forgejo API tokens are 40-character hexadecimal strings."
                "Get a valid token at: https://codeberg.org/user/settings/applications"
            )

        return SecretStr(token_value)

    @field_validator("gemini_thinking_budget")
    @classmethod
    def validate_gemini_thinking_budget(
        cls, v: int | None, info: ValidationInfo
    ) -> int | None:
        """Validate thinking budget against known model minimums.

        Note: gemini-2.5-pro requires minimum 128 tokens, but gemini-2.5-flash
        can use 0 to disable thinking completely.
        """
        if v is not None and 0 < v < 128:
            import structlog

            logger = structlog.get_logger()

            # Try to get model name from validation context
            model = info.data.get("ai_model", "unknown") if info.data else "unknown"

            logger.warning(
                "gemini_thinking_budget below minimum for some models",
                value=v,
                model=model,
                minimum_pro=128,
                note="gemini-2.5-pro requires >= 128 tokens. gemini-2.5-flash supports 0 to disable thinking.",
            )
        return v

    @model_validator(mode="after")
    def set_adaptive_max_chars(self) -> Config:
        """Set adaptive max_chars based on AI provider if not explicitly set."""
        if self.max_chars is None:
            # Use provider-specific default
            self.max_chars = PROVIDER_DEFAULT_MAX_CHARS.get(
                self.ai_provider, DEFAULT_MAX_CHARS
            )

        return self

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "env_prefix": "",
        "env_nested_delimiter": "__",  # Support nested models via PARENT__CHILD env vars
        "extra": "ignore",  # Ignore unknown environment variables
    }

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Customise settings sources priority.

        Priority order (highest to lowest) - OPTIMIZED FOR CI/CD:
        1. init_settings - CLI arguments passed to constructor (highest priority)
        2. env_settings - Environment variables (CI/CD configuration)
        3. dotenv_settings - .env file (local development)
        4. config_file_settings - YAML config file (.ai_review/config.yml)
        5. field defaults (implicit, not in tuple)

        This order ensures that:
        - CLI arguments always win (manual override)
        - Environment variables override config files (CI/CD friendly)
        - Config files provide project-level defaults
        - Field defaults are the fallback

        Args:
            settings_cls: The settings class
            init_settings: Source for constructor arguments
            env_settings: Source for environment variables
            dotenv_settings: Source for .env file
            file_secret_settings: Source for secrets (not used)

        Returns:
            Tuple of settings sources in priority order
        """
        # Get config file path from init_settings (CLI) or env_settings (env var)
        # Priority: CLI --config-file > CONFIG_FILE env var > auto-detect
        # Note: Safe to call these sources - they just return dicts, no side effects
        init_data = init_settings()
        env_data = env_settings()

        config_path = init_data.get("config_file") or env_data.get("config_file")
        no_config_file = init_data.get("no_config_file") or env_data.get(
            "no_config_file", False
        )

        sources: list[PydanticBaseSettingsSource] = [
            init_settings,
            env_settings,
            dotenv_settings,
        ]

        # Add config file source unless disabled
        if not no_config_file:
            sources.append(
                ConfigFileSettingsSource(
                    settings_cls,
                    config_path=config_path,
                    require_exists=config_path
                    is not None,  # Require if explicitly specified
                )
            )

        return tuple(sources)

    def get_effective_repository_path(self) -> str | None:
        """Get effective repository path from CI environment or explicit config."""
        # Priority: new fields -> legacy GitLab fields -> None
        return self.repository_path or self.ci_project_path

    def get_effective_pull_request_number(self) -> int | None:
        """Get effective pull/merge request number from CI environment or explicit config."""
        # Priority: new fields -> legacy GitLab fields -> None
        return self.pull_request_number or self.ci_merge_request_iid

    def get_effective_server_url(self) -> str:
        """Get effective server URL prioritizing CI environment."""
        # Priority: new fields -> legacy GitLab fields -> platform defaults
        if self.server_url:
            return self.server_url
        if self.ci_server_url:
            return self.ci_server_url

        # Return platform-specific default
        if self.platform_provider == PlatformProvider.GITHUB:
            return self.github_url
        elif self.platform_provider == PlatformProvider.FORGEJO:
            return self.forgejo_url
        else:
            return self.gitlab_url

    def get_platform_token(self) -> str:
        """Get the appropriate token for the configured platform."""
        if self.platform_provider == PlatformProvider.GITLAB:
            if not self.gitlab_token:
                raise ValueError("GitLab token is required for GitLab platform")
            return self.gitlab_token.get_secret_value()
        elif self.platform_provider == PlatformProvider.GITHUB:
            if not self.github_token:
                raise ValueError("GitHub token is required for GitHub platform")
            return self.github_token.get_secret_value()
        elif self.platform_provider == PlatformProvider.FORGEJO:
            if not self.forgejo_token:
                raise ValueError("Forgejo token is required for Forgejo platform")
            return self.forgejo_token.get_secret_value()
        else:
            raise ValueError(f"Unsupported platform: {self.platform_provider}")

    def is_ci_mode(self) -> bool:
        """Check if running in CI/CD environment."""
        return bool(
            self.get_effective_repository_path()
            and self.get_effective_pull_request_number()
        )

    # =========================================================================
    # CLI Argument Handling
    # =========================================================================

    @classmethod
    def from_cli_args(cls, cli_args: dict[str, Any]) -> Config:
        """Create Config from CLI arguments with automatic name mapping.

        This method maps Click CLI parameter names to Config field names,
        handles special flags (--local, --no-mr-summary, etc.), and creates
        a Config instance using Pydantic's native priority system.

        Priority order (handled by settings_customise_sources):
        1. CLI arguments (passed here)
        2. Environment variables
        3. .env file
        4. Config file (.ai_review/config.yml)
        5. Field defaults

        Args:
            cli_args: Raw CLI arguments from Click (kwargs from main function)

        Returns:
            Config: Fully configured Config object
        """
        mapped_args = cls._map_cli_args_to_config(cli_args)
        return cls(**mapped_args)

    @classmethod
    def _map_cli_args_to_config(cls, cli_args: dict[str, Any]) -> dict[str, Any]:
        """Map CLI arguments to Config fields.

        CLI parameter names now match Config field names directly (with legacy
        aliases for backward compatibility), so most args pass through unchanged.
        Only special flags and positional argument conflicts require transformation.

        Args:
            cli_args: Raw CLI arguments from Click

        Returns:
            Dict with Config-compatible field names and values
        """
        # Get all non-None CLI args that correspond directly to Config fields
        config_fields = set(cls.model_fields.keys())
        mapped_args = {
            k: v for k, v in cli_args.items() if v is not None and k in config_fields
        }

        # Handle CLI options that conflict with positional arguments
        # (these need different names in Click to avoid conflicts)
        if cli_args.get("project_id_option"):
            mapped_args["project_id"] = cli_args["project_id_option"]
        if cli_args.get("pr_number_option"):
            mapped_args["pr_number"] = cli_args["pr_number_option"]

        # Handle special flag transformations
        if cli_args.get("local"):
            mapped_args["platform_provider"] = PlatformProvider.LOCAL

        if cli_args.get("no_mr_summary"):
            mapped_args["include_mr_summary"] = False

        if cli_args.get("no_skip_detection"):
            mapped_args["skip_review"] = {"enabled": False}

        if cli_args.get("no_file_filtering"):
            mapped_args["exclude_patterns"] = []
        elif cli_args.get("exclude_files"):
            mapped_args["exclude_patterns"] = _DEFAULT_EXCLUDE_PATTERNS + list(
                cli_args["exclude_files"]
            )

        return mapped_args
