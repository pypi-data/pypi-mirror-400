"""GitHub API client for fetching pull request data."""

from __future__ import annotations

import asyncio

import structlog
from github import Auth, Github, GithubException
from github.PullRequest import PullRequest
from github.Repository import Repository

from ai_code_review.core.base_platform_client import BasePlatformClient
from ai_code_review.models.config import Config
from ai_code_review.models.platform import (
    PostReviewResponse,
    PullRequestCommit,
    PullRequestData,
    PullRequestDiff,
    PullRequestInfo,
    Review,
    ReviewComment,
)
from ai_code_review.utils.platform_exceptions import GitHubAPIError

logger = structlog.get_logger(__name__)


class GitHubClient(BasePlatformClient):
    """Client for GitHub API operations."""

    def __init__(self, config: Config) -> None:
        """Initialize GitHub client."""
        super().__init__(config)
        self._github_client: Github | None = None

    @property
    def github_client(self) -> Github:
        """Get or create GitHub client instance."""
        if self._github_client is None:
            self._github_client = Github(
                auth=Auth.Token(self.config.get_platform_token()),
                base_url=self.config.get_effective_server_url(),
            )
        return self._github_client

    async def _get_authenticated_username_impl(self) -> str:
        """GitHub-specific implementation to get authenticated username.

        Returns:
            GitHub username (login) of the authenticated user.
            Falls back to 'github-actions[bot]' for GitHub Actions tokens
            that cannot access the /user endpoint.

        Raises:
            GitHubAPIError: If getting user fails for reasons other than
                permissions (non-403 errors)
        """
        try:
            # Get authenticated user using thread pool for blocking call
            user = await asyncio.to_thread(self.github_client.get_user)
            logger.info("Authenticated as GitHub user", username=user.login)
            return user.login

        except GithubException as e:
            # GitHub Actions tokens (installation tokens) cannot access /user endpoint
            # This is a known limitation - they return 403 "Resource not accessible"
            # Fall back to the well-known bot username for GitHub Actions
            if e.status == 403:
                fallback_username = "github-actions[bot]"
                logger.warning(
                    "Cannot get authenticated user (likely GitHub Actions token), "
                    "using fallback",
                    fallback=fallback_username,
                    error=str(e),
                )
                return fallback_username

            raise GitHubAPIError(f"Failed to get authenticated user: {e}") from e

    async def _get_pull_request_data_impl(
        self, project_id: str, pr_number: int
    ) -> PullRequestData:
        """GitHub-specific implementation to fetch PR data.

        Args:
            project_id: GitHub repository path (e.g., 'owner/repo')
            pr_number: Pull request number

        Returns:
            Complete pull request data with diffs

        Raises:
            GitHubAPIError: If API call fails
        """
        try:
            # Get repository using thread pool for blocking call
            repo: Repository = await asyncio.to_thread(
                self.github_client.get_repo, project_id
            )

            # Get pull request using thread pool for blocking call
            pull_request: PullRequest = await asyncio.to_thread(
                repo.get_pull, pr_number
            )

            # Create PR info (mapping GitHub PR to platform-agnostic model)
            pr_info = PullRequestInfo(
                id=pull_request.id,
                number=pull_request.number,
                title=pull_request.title,
                description=pull_request.body,
                source_branch=pull_request.head.ref,
                target_branch=pull_request.base.ref,
                author=pull_request.user.login,
                state=pull_request.state,
                web_url=pull_request.html_url,
                draft=getattr(pull_request, "draft", False),  # GitHub draft status
            )

            # Get diffs, commits, and reviews
            diffs = await self._fetch_pull_request_diffs(pull_request)
            commits = await self._fetch_pull_request_commits(pull_request)
            reviews, comments = await self._fetch_pull_request_reviews_and_comments(
                pull_request
            )

            return PullRequestData(
                info=pr_info,
                diffs=diffs,
                commits=commits,
                reviews=reviews,
                comments=comments,
            )

        except GithubException as e:
            # GitHub library specific exceptions
            raise GitHubAPIError(f"Failed to fetch PR data: {e}") from e
        except Exception as e:
            # Catch any other unexpected errors (should be rare)
            raise GitHubAPIError(f"Unexpected error fetching PR data: {e}") from e

    async def _fetch_pull_request_diffs(
        self, pull_request: PullRequest
    ) -> list[PullRequestDiff]:
        """Fetch diffs for a pull request.

        Attempts to fetch complete diff via .diff URL first for maximum
        coverage (includes large files), with automatic fallback to API
        method if HTTP fetch fails.

        Args:
            pull_request: GitHub pull request object

        Returns:
            List of diffs for the pull request
        """
        # Try HTTP .diff URL first (complete, includes large files)
        diffs = await self._fetch_diff_via_http(
            diff_url=pull_request.diff_url,
            headers={
                "Authorization": f"token {self.config.get_platform_token()}",
                "Accept": "text/plain",
            },
        )

        # Fallback to API method if HTTP fetch failed
        if diffs is None:
            return await self._fetch_pull_request_diffs_via_api(pull_request)

        return diffs

    async def _fetch_pull_request_diffs_via_api(
        self, pull_request: PullRequest
    ) -> list[PullRequestDiff]:
        """Fetch diffs for a pull request via GitHub API.

        This is the original implementation, kept as a fallback method
        when HTTP .diff URL fetching fails.

        Args:
            pull_request: GitHub pull request object

        Returns:
            List of diffs from API
        """
        diffs: list[PullRequestDiff] = []
        excluded_files: list[str] = []
        excluded_chars = 0

        try:
            # Get files from the PR using thread pool for blocking call
            files = await asyncio.to_thread(pull_request.get_files)

            # Track files skipped due to missing patch content
            skipped_no_diff = []

            for file in files:
                file_path = file.filename
                patch_content = file.patch or ""

                # Skip binary files or files without patches
                if not patch_content:
                    skipped_no_diff.append(file_path)
                    continue

                # Check if file should be excluded from AI review
                if self._should_exclude_file(file_path):
                    excluded_files.append(file_path)
                    excluded_chars += len(patch_content)
                    continue  # Skip excluded files

                # Create diff object
                diff = PullRequestDiff(
                    file_path=file_path,
                    new_file=file.status == "added",
                    renamed_file=file.status == "renamed",
                    deleted_file=file.status == "removed",
                    diff=patch_content,
                )

                diffs.append(diff)

                # Check limits
                if len(diffs) >= self.config.max_files:
                    break

            # Log filtering and skipping statistics
            if excluded_files:
                logger.info(
                    "Files excluded from AI review",
                    excluded_files=len(excluded_files),
                    excluded_chars=excluded_chars,
                    included_files=len(diffs),
                    examples=excluded_files[:3],  # Show first 3 examples
                )

            if skipped_no_diff:
                logger.info(
                    "Files skipped - no diff content from GitHub API",
                    skipped_files=len(skipped_no_diff),
                    reason="GitHub omits patch content for large files (e.g., binary files)",
                    examples=skipped_no_diff[:3],  # Show first 3 examples
                )

            return self._apply_content_limits(diffs)

        except GithubException as e:
            raise GitHubAPIError(f"Failed to fetch diffs: {e}") from e
        except Exception as e:
            # Catch any other unexpected errors (should be rare)
            raise GitHubAPIError(f"Unexpected error fetching diffs: {e}") from e

    async def _fetch_pull_request_commits(
        self, pull_request: PullRequest
    ) -> list[PullRequestCommit]:
        """Fetch commits for a pull request."""
        commits: list[PullRequestCommit] = []

        try:
            # Get commits from the PR using thread pool for blocking call
            pr_commits = await asyncio.to_thread(pull_request.get_commits)

            for commit_data in pr_commits:
                commit = PullRequestCommit(
                    id=commit_data.sha,
                    title=commit_data.commit.message.split("\n")[
                        0
                    ],  # First line as title
                    message=commit_data.commit.message,
                    author_name=commit_data.commit.author.name or "Unknown",
                    author_email=commit_data.commit.author.email
                    or "unknown@example.com",
                    committed_date=commit_data.commit.author.date.isoformat(),
                    short_id=commit_data.sha[:7],
                )
                commits.append(commit)

            return commits

        except GithubException as e:
            raise GitHubAPIError(f"Failed to fetch commits: {e}") from e
        except Exception as e:
            # Catch any other unexpected errors (should be rare)
            raise GitHubAPIError(f"Unexpected error fetching commits: {e}") from e

    async def _fetch_pull_request_reviews_and_comments(
        self, pull_request: PullRequest
    ) -> tuple[list[Review], list[ReviewComment]]:
        """Fetch ALL reviews and comments (resolved and unresolved).

        Important: Fetches all comments, not just open/unresolved ones,
        to detect previously invalidated suggestions.

        Args:
            pull_request: GitHub PullRequest object

        Returns:
            Tuple of (reviews_list, all_comments)
        """

        def _fetch_all_sync() -> tuple[list[Review], list[ReviewComment]]:
            """Fetch and iterate over paginated lists in thread.

            Limits total comments fetched to max_comments_to_fetch to avoid
            performance issues on PRs with hundreds of comments.
            """
            from itertools import islice

            reviews_list_sync = []
            all_comments_sync = []
            max_to_fetch = self.config.max_comments_to_fetch
            comments_fetched = 0

            # Get recent reviews - iteration happens in thread
            reviews = pull_request.get_reviews()
            for review in islice(reviews, max_to_fetch):
                reviews_list_sync.append(
                    Review(
                        id=review.id,
                        author=review.user.login,
                        state=review.state,
                        body=review.body or "",
                        submitted_at=review.submitted_at.isoformat(),
                    )
                )

            # Get recent review comments (code-level) - iteration in thread
            review_comments = pull_request.get_review_comments()
            for comment in islice(review_comments, max_to_fetch - comments_fetched):
                # Skip comments from bots (GitHub Actions, etc.)
                if comment.user.type == "Bot":
                    continue

                all_comments_sync.append(
                    ReviewComment(
                        id=comment.id,
                        author=comment.user.login,
                        body=comment.body,
                        created_at=comment.created_at.isoformat(),
                        updated_at=comment.updated_at.isoformat()
                        if comment.updated_at
                        else None,
                        path=comment.path,
                        line=comment.line,
                        in_reply_to_id=comment.in_reply_to_id,
                        is_system=False,
                        # Note: GitHub doesn't expose resolved status directly
                    )
                )
                comments_fetched += 1
                if comments_fetched >= max_to_fetch:
                    break

            # Get recent issue comments (general PR comments) - iteration in thread
            if comments_fetched < max_to_fetch:
                issue_comments = pull_request.get_issue_comments()
                for issue_comment in islice(
                    issue_comments, max_to_fetch - comments_fetched
                ):
                    # Skip comments from bots (GitHub Actions, etc.)
                    if issue_comment.user.type == "Bot":
                        continue

                    all_comments_sync.append(
                        ReviewComment(
                            id=issue_comment.id,
                            author=issue_comment.user.login,
                            body=issue_comment.body,
                            created_at=issue_comment.created_at.isoformat(),
                            updated_at=issue_comment.updated_at.isoformat()
                            if issue_comment.updated_at
                            else None,
                            is_system=False,
                        )
                    )
                    comments_fetched += 1
                    if comments_fetched >= max_to_fetch:
                        break

            return reviews_list_sync, all_comments_sync

        try:
            # Run all blocking operations (including pagination) in thread
            reviews_list, all_comments = await asyncio.to_thread(_fetch_all_sync)

            logger.info(
                "Fetched PR reviews and comments",
                reviews=len(reviews_list),
                comments=len(all_comments),
                max_fetched=self.config.max_comments_to_fetch,
            )

            return reviews_list, all_comments

        except GithubException as e:
            logger.warning("Failed to fetch reviews/comments", error=str(e))
            return [], []

    # -------------------------------------------------------------------------
    # GitHub-specific mock method overrides
    # -------------------------------------------------------------------------

    def _get_mock_state(self) -> str:
        """GitHub uses 'open' instead of GitLab's 'opened'."""
        return "open"

    def _format_mock_pr_url(self, project_id: str, pr_number: int) -> str:
        """GitHub PR URL format: /owner/repo/pull/N."""
        return f"{self.format_project_url(project_id)}/pull/{pr_number}"

    def _format_mock_comment_url(self, project_id: str, pr_number: int) -> str:
        """GitHub comment URL format."""
        base_url = self._format_mock_pr_url(project_id, pr_number)
        return f"{base_url}#issuecomment-mock_123"

    async def _post_review_impl(
        self, project_id: str, pr_number: int, review_content: str
    ) -> PostReviewResponse:
        """GitHub-specific implementation to post review.

        Args:
            project_id: GitHub repository path (e.g., 'owner/repo')
            pr_number: Pull request number
            review_content: The markdown content of the review to post

        Returns:
            Response containing comment information

        Raises:
            GitHubAPIError: If posting fails
        """
        try:
            # Get repository using thread pool for blocking call
            repo: Repository = await asyncio.to_thread(
                self.github_client.get_repo, project_id
            )

            # Get pull request using thread pool for blocking call
            pull_request: PullRequest = await asyncio.to_thread(
                repo.get_pull, pr_number
            )

            # Create the comment on the PR using thread pool for blocking call
            comment = await asyncio.to_thread(
                pull_request.create_issue_comment, review_content
            )

            # Return comment information
            return PostReviewResponse(
                id=str(comment.id),
                url=comment.html_url,
                created_at=comment.created_at.isoformat(),
                author=comment.user.login,
            )

        except GithubException as e:
            raise GitHubAPIError(f"Failed to post review to GitHub: {e}") from e
        except Exception as e:
            # Catch any other unexpected errors (should be rare)
            raise GitHubAPIError(f"Unexpected error posting review: {e}") from e

    def get_platform_name(self) -> str:
        """Get the name of the platform."""
        return "github"

    def format_project_url(self, project_id: str) -> str:
        """Format the project URL for GitHub."""
        return f"https://github.com/{project_id}"
