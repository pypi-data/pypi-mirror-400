"""Base platform client implementation."""

from __future__ import annotations

import asyncio
import fnmatch
import ssl
from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta
from pathlib import PurePath
from typing import Any

import httpx
import structlog
import unidiff  # type: ignore

from ai_code_review.models.config import Config
from ai_code_review.models.platform import (
    PlatformClientInterface,
    PostReviewResponse,
    PullRequestCommit,
    PullRequestData,
    PullRequestDiff,
    PullRequestInfo,
    ReviewComment,
)

logger = structlog.get_logger(__name__)


class BasePlatformClient(PlatformClientInterface, ABC):
    """Base implementation for platform clients with common functionality."""

    def __init__(self, config: Config) -> None:
        """Initialize platform client."""
        self.config = config
        self._authenticated_username: str | None = None

    def _should_exclude_file(self, file_path: str) -> bool:
        """Check if file should be excluded from AI review based on patterns.

        Args:
            file_path: Path of the file to check

        Returns:
            True if file should be excluded, False otherwise
        """
        path = PurePath(file_path)
        for pattern in self.config.exclude_patterns:
            try:
                # Use PurePath.match() for glob patterns with ** support
                if path.match(pattern):
                    return True
                # Also try fnmatch for simple patterns (fallback)
                if fnmatch.fnmatch(file_path, pattern):
                    return True
            except (ValueError, TypeError):
                # If pattern is invalid, try fnmatch as fallback
                if fnmatch.fnmatch(file_path, pattern):
                    return True
        return False

    def _apply_content_limits(
        self, diffs: list[PullRequestDiff]
    ) -> list[PullRequestDiff]:
        """Apply content size limits to diffs."""
        # max_chars should never be None after Config initialization
        # (set by adaptive validator if not explicitly provided)
        if self.config.max_chars is None:
            raise ValueError(
                "max_chars must be set. This indicates a configuration error."
            )

        total_chars = 0
        limited_diffs: list[PullRequestDiff] = []

        for diff in diffs:
            # Check if adding this diff exceeds the limit
            diff_chars = len(diff.diff)
            if total_chars + diff_chars > self.config.max_chars:
                # Try to truncate this diff
                remaining_chars = self.config.max_chars - total_chars
                if remaining_chars > 20:  # Only include if we have meaningful content
                    truncated_diff = PullRequestDiff(
                        file_path=diff.file_path,
                        new_file=diff.new_file,
                        renamed_file=diff.renamed_file,
                        deleted_file=diff.deleted_file,
                        diff=diff.diff[:remaining_chars] + "\n... (diff truncated)",
                    )
                    limited_diffs.append(truncated_diff)
                break

            limited_diffs.append(diff)
            total_chars += diff_chars

        return limited_diffs

    def _convert_patchset_to_diffs(self, patch_set: Any) -> list[PullRequestDiff]:
        """Convert unidiff PatchSet to our PullRequestDiff format.

        Applies filtering for binary files and excluded patterns,
        and enforces max_files limit.

        Args:
            patch_set: unidiff.PatchSet object with parsed diffs

        Returns:
            List of filtered and converted PullRequestDiff objects
        """
        diffs: list[PullRequestDiff] = []
        binary_skipped = 0
        excluded_by_pattern = 0

        for patched_file in patch_set:
            file_path = patched_file.path

            # Skip binaries (unidiff detects via "Binary files differ")
            if patched_file.is_binary_file:
                binary_skipped += 1
                continue

            # Apply user exclusion patterns
            if self._should_exclude_file(file_path):
                excluded_by_pattern += 1
                continue

            diffs.append(
                PullRequestDiff(
                    file_path=file_path,
                    new_file=patched_file.is_added_file,
                    renamed_file=patched_file.is_rename,
                    deleted_file=patched_file.is_removed_file,
                    diff=str(patched_file),
                )
            )

            if len(diffs) >= self.config.max_files:
                logger.info(
                    "Reached max_files limit",
                    max_files=self.config.max_files,
                )
                break

        logger.info(
            "Complete diff fetched via HTTP",
            total_files=len(patch_set),
            included=len(diffs),
            binary_skipped=binary_skipped,
            excluded_by_pattern=excluded_by_pattern,
        )

        return diffs

    async def _fetch_diff_via_http(
        self,
        diff_url: str,
        headers: dict[str, str],
        ssl_context: bool | ssl.SSLContext = True,
    ) -> list[PullRequestDiff] | None:
        """Fetch and parse diff via HTTP .diff URL.

        This method provides a common implementation for fetching complete diffs
        via HTTP, which is more reliable than API endpoints for large files.

        Args:
            diff_url: The URL to fetch the diff from
            headers: HTTP headers (authentication, etc.)
            ssl_context: SSL context for verification (True, False, or ssl.SSLContext)

        Returns:
            List of PullRequestDiff objects if successful, None if fetch fails
        """
        try:
            timeout = httpx.Timeout(self.config.diff_download_timeout)
            async with httpx.AsyncClient(verify=ssl_context, timeout=timeout) as client:
                response = await client.get(diff_url, headers=headers)

                if response.status_code == 200:
                    # Parse with unidiff - it handles binary detection automatically
                    # Use to_thread for CPU-bound parsing to avoid blocking event loop
                    patch_set = await asyncio.to_thread(unidiff.PatchSet, response.text)

                    # Convert to our format (shared logic)
                    diffs = self._convert_patchset_to_diffs(patch_set)

                    return self._apply_content_limits(diffs)

        except Exception as e:
            logger.info(
                "HTTP diff fetch failed, using API fallback",
                error=str(e),
            )

        return None

    # -------------------------------------------------------------------------
    # Template Method pattern: Public methods handle dry-run, call _impl
    # -------------------------------------------------------------------------

    async def get_authenticated_username(self) -> str:
        """Get username of authenticated user (bot).

        This is used to identify which comments/reviews were made by this bot
        to prioritize author responses to previous AI reviews.

        Returns:
            Username/login of the authenticated user

        Raises:
            PlatformAPIError: If API call fails
        """
        if self._authenticated_username is not None:
            return self._authenticated_username

        if self.config.dry_run:
            self._authenticated_username = "ai-code-review-bot-dry-run"
            return self._authenticated_username

        self._authenticated_username = await self._get_authenticated_username_impl()
        return self._authenticated_username

    async def get_pull_request_data(
        self, project_id: str, pr_number: int
    ) -> PullRequestData:
        """Fetch complete pull/merge request data including diffs.

        Handles dry-run mode automatically, returning mock data.
        Subclasses implement _get_pull_request_data_impl for real API calls.

        Args:
            project_id: Platform-specific project identifier
            pr_number: Pull/merge request number

        Returns:
            Complete pull request data with diffs
        """
        if self.config.dry_run:
            return self._create_mock_pr_data(project_id, pr_number)

        return await self._get_pull_request_data_impl(project_id, pr_number)

    async def post_review(
        self, project_id: str, pr_number: int, review_content: str
    ) -> PostReviewResponse:
        """Post review as a comment on the pull/merge request.

        Handles dry-run mode automatically, returning mock response.
        Subclasses implement _post_review_impl for real API calls.

        Args:
            project_id: Platform-specific project identifier
            pr_number: Pull/merge request number
            review_content: The markdown content of the review to post

        Returns:
            Response containing comment information
        """
        if self.config.dry_run:
            return self._create_mock_post_response(
                project_id, pr_number, review_content
            )

        return await self._post_review_impl(project_id, pr_number, review_content)

    @abstractmethod
    def get_platform_name(self) -> str:
        """Get the name of the platform."""
        pass

    @abstractmethod
    def format_project_url(self, project_id: str) -> str:
        """Format the project URL for this platform."""
        pass

    # -------------------------------------------------------------------------
    # Abstract implementation methods (subclasses must implement)
    # -------------------------------------------------------------------------

    @abstractmethod
    async def _get_authenticated_username_impl(self) -> str:
        """Platform-specific: get authenticated username. Called when not dry-run."""
        pass

    @abstractmethod
    async def _get_pull_request_data_impl(
        self, project_id: str, pr_number: int
    ) -> PullRequestData:
        """Platform-specific: fetch PR data. Called when not dry-run."""
        pass

    @abstractmethod
    async def _post_review_impl(
        self, project_id: str, pr_number: int, review_content: str
    ) -> PostReviewResponse:
        """Platform-specific: post review. Called when not dry-run."""
        pass

    # -------------------------------------------------------------------------
    # Dry-run mock data methods (centralized to avoid duplication)
    # Override _get_mock_state, _format_mock_pr_url, _format_mock_comment_url
    # in subclasses for platform-specific behavior.
    # -------------------------------------------------------------------------

    def _get_mock_state(self) -> str:
        """Mock PR state. Default: 'opened' (GitLab). Override for other platforms."""
        return "opened"

    def _format_mock_pr_url(self, project_id: str, pr_number: int) -> str:
        """Mock PR URL. Default: GitLab style. Override for other platforms."""
        return f"{self.format_project_url(project_id)}/-/merge_requests/{pr_number}"

    def _format_mock_comment_url(self, project_id: str, pr_number: int) -> str:
        """Mock comment URL. Default: GitLab style. Override for other platforms."""
        return f"{self._format_mock_pr_url(project_id, pr_number)}#note_mock_123"

    def _create_mock_pr_data(self, project_id: str, pr_number: int) -> PullRequestData:
        """Create mock PR data for dry-run mode."""
        # Use dynamic dates to prevent issues with time-based filtering logic
        now = datetime.now(UTC)
        commit_date = (now - timedelta(hours=2)).isoformat()
        comment_date = (now - timedelta(hours=4)).isoformat()

        mock_info = PullRequestInfo(
            id=12345,
            number=pr_number,
            title=f"Mock PR {pr_number} for project {project_id}",
            description="Mock pull request for testing",
            source_branch="feature/mock-branch",
            target_branch="main",
            author="mock_user",
            state=self._get_mock_state(),
            web_url=self._format_mock_pr_url(project_id, pr_number),
        )

        mock_diffs = [
            PullRequestDiff(
                file_path="src/mock_file.py",
                new_file=False,
                diff="@@ -1,3 +1,3 @@\n def mock_function():\n-    return 'old'\n+    return 'new'",
            )
        ]

        mock_commits = [
            PullRequestCommit(
                id="abc123456789",
                title="Add mock feature",
                message="Add mock feature\n\nImplements mock functionality for dry-run testing.",
                author_name="Mock Author",
                author_email="author@example.com",
                committed_date=commit_date,
                short_id="abc1234",
            )
        ]

        # Include mock comments to enable Review Synthesis testing in dry-run mode
        mock_comments = [
            ReviewComment(
                id=1,
                author="mock_reviewer",
                body="Mock comment for synthesis testing - previous review feedback",
                created_at=comment_date,
                resolved=False,
            )
        ]

        return PullRequestData(
            info=mock_info,
            diffs=mock_diffs,
            commits=mock_commits,
            reviews=[],
            comments=mock_comments,
        )

    def _create_mock_post_response(
        self, project_id: str, pr_number: int, review_content: str
    ) -> PostReviewResponse:
        """Create mock post response for dry-run mode."""
        now = datetime.now(UTC).isoformat()
        return PostReviewResponse(
            id="mock_comment_123",
            url=self._format_mock_comment_url(project_id, pr_number),
            created_at=now,
            author="AI Code Review (DRY RUN)",
            content_preview=review_content[:100] + "..."
            if len(review_content) > 100
            else review_content,
        )
