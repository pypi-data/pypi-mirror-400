"""Forgejo API client for fetching pull request data."""

from __future__ import annotations

import structlog
from pyforgejo import AsyncPyforgejoApi, Comment, Commit, PullRequest, PullReview, User
from pyforgejo.core import ApiError

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
from ai_code_review.utils.platform_exceptions import ForgejoAPIError

logger = structlog.get_logger(__name__)


class ForgejoClient(BasePlatformClient):
    """Client for Forgejo API operations."""

    def __init__(self, config: Config) -> None:
        """Initialize Forgejo client."""
        super().__init__(config)
        self._forgejo_client: AsyncPyforgejoApi | None = None

    @property
    def forgejo_client(self) -> AsyncPyforgejoApi:
        """Get or create Forgejo client instance."""
        baseurl = self.config.get_effective_server_url().rstrip("/")
        if not baseurl.endswith("/api/v1"):
            baseurl = f"{baseurl}/api/v1"
        if self._forgejo_client is None:
            self._forgejo_client = AsyncPyforgejoApi(
                api_key=self.config.get_platform_token(),
                base_url=baseurl,
            )
        return self._forgejo_client

    async def _get_authenticated_username_impl(self) -> str:
        """Forgejo-specific: get authenticated username.

        Returns:
            Forgejo username (login) of the authenticated user.
            Falls back to 'forgejo-actions' for Forgejo Actions tokens
            that cannot access the user endpoint.

        Raises:
            ForgejoAPIError: If getting user fails for reasons other than
                permissions (non-403 errors)
        """
        try:
            user: User = await self.forgejo_client.user.get_current()
            if user.login_name:
                # just to make type checks happy
                logger.info("Authenticated as Forgejo user", username=user.login_name)
                return user.login_name or ""
            else:
                raise ForgejoAPIError(
                    "Failed to get authenticated user: API value was empty"
                )
        except ApiError as e:
            # Forgejo Actions tokens (workflow tokens) may not have access to user endpoint
            # This is a known limitation - they return 403 "Forbidden"
            # Fall back to the well-known bot username for Forgejo Actions
            if e.status_code == 403:
                fallback_username = "forgejo-actions"
                logger.warning(
                    "Cannot get authenticated user (likely Forgejo Actions token), "
                    "using fallback",
                    fallback=fallback_username,
                    error=str(e),
                )
                return fallback_username

            raise ForgejoAPIError(f"Failed to get authenticated user: {e}") from e

    async def _get_pull_request_data_impl(
        self, project_id: str, pr_number: int
    ) -> PullRequestData:
        """Forgejo-specific: fetch PR data.

        Args:
            project_id: Forgejo repository path (e.g., 'owner/repo')
            pr_number: Pull request number

        Returns:
            Complete pull request data with diffs

        Raises:
            ForgejoAPIError: If API call fails
        """
        try:
            owner, repo = project_id.split("/")
        except ValueError as e:
            raise ForgejoAPIError(
                f"Malformed project ID: {project_id} - must contain one /"
            ) from e
        try:
            pull_request: PullRequest = (
                await self.forgejo_client.repository.repo_get_pull_request(
                    owner,
                    repo,
                    pr_number,
                )
            )

            # Create PR info (mapping Forgejo PR to platform-agnostic model)
            # The extreme defensive coding here is to make type checks happy.
            # This all relates to limitations in the forgejo API definition:
            # https://codeberg.org/forgejo/forgejo/issues/9428#issuecomment-8868930
            # which mean everything in pyforgejo is typing.Optional
            prhead = pull_request.head
            prbase = pull_request.base
            pruser = pull_request.user
            prdurl = pull_request.diff_url
            prnum = pull_request.number
            if not (prhead and prbase and pruser and prdurl and prnum):
                raise ForgejoAPIError(
                    "head, base, user, diff_url or number missing in API response!"
                )
            pr_info = PullRequestInfo(
                id=pull_request.id or 0,
                number=pull_request.number or 0,
                title=pull_request.title or "",
                description=pull_request.body or "",
                source_branch=prhead.ref or "",
                target_branch=prbase.ref or "",
                author=pruser.login or "",
                state=pull_request.state or "",
                web_url=pull_request.html_url or "",
                draft=pull_request.draft or False,
            )

            # Get diffs, commits, and reviews
            diffs = await self._fetch_pull_request_diffs(prdurl)
            commits = await self._fetch_pull_request_commits(owner, repo, prnum)
            reviews, comments = await self._fetch_pull_request_reviews_and_comments(
                owner, repo, prnum
            )

            return PullRequestData(
                info=pr_info,
                diffs=diffs,
                commits=commits,
                reviews=reviews,
                comments=comments,
            )

        except ApiError as e:
            # Forgejo library specific exceptions
            raise ForgejoAPIError(f"Failed to fetch PR data: {e}") from e
        except Exception as e:
            # Catch any other unexpected errors (should be rare)
            raise ForgejoAPIError(f"Unexpected error fetching PR data: {e}") from e

    async def _fetch_pull_request_diffs(self, diff_url: str) -> list[PullRequestDiff]:
        """Fetch diffs for a pull request."""
        diffs = await self._fetch_diff_via_http(
            diff_url=diff_url,
            headers={
                "Authorization": f"token {self.config.get_platform_token()}",
                "Accept": "text/plain",
            },
        )
        return diffs or []

    async def _fetch_pull_request_commits(
        self, owner: str, repo: str, pr_number: int
    ) -> list[PullRequestCommit]:
        """Fetch commits for a pull request."""
        commits: list[PullRequestCommit] = []

        try:
            pr_commits: list[
                Commit
            ] = await self.forgejo_client.repository.repo_get_pull_request_commits(
                owner,
                repo,
                pr_number,
            )

            for commit_data in pr_commits:
                if not (
                    commit_data.commit
                    and commit_data.commit.message
                    and commit_data.commit.author
                    and commit_data.sha
                ):
                    logger.warning(
                        "commit or sha missing in get_pull_request_commits API response "
                        f"for {owner}/{repo} {str(pr_number)}"
                    )
                    continue
                commit = PullRequestCommit(
                    id=commit_data.sha,
                    title=commit_data.commit.message.split("\n")[
                        0
                    ],  # First line as title
                    message=commit_data.commit.message,
                    author_name=commit_data.commit.author.name or "Unknown",
                    author_email=commit_data.commit.author.email
                    or "unknown@example.com",
                    committed_date=commit_data.commit.author.date or "",
                    short_id=commit_data.sha[:7],
                )
                commits.append(commit)

            return commits

        except ApiError as e:
            raise ForgejoAPIError(f"Failed to fetch commits: {e}") from e
        except Exception as e:
            # Catch any other unexpected errors (should be rare)
            raise ForgejoAPIError(f"Unexpected error fetching commits: {e}") from e

    async def _fetch_pull_request_reviews_and_comments(
        self, owner: str, repo: str, pr_number: int
    ) -> tuple[list[Review], list[ReviewComment]]:
        """Fetch ALL reviews and comments (resolved and unresolved).

        Important: Fetches all comments, not just open/unresolved ones,
        to detect previously invalidated suggestions.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number

        Returns:
            Tuple of (reviews_list, all_comments)
        """

        try:
            from itertools import islice

            reviews_list = []
            all_comments = []
            max_to_fetch = self.config.max_comments_to_fetch
            comments_fetched = 0

            # Get recent reviews - iteration happens in thread
            reviews: list[
                PullReview
            ] = await self.forgejo_client.repository.repo_list_pull_reviews(
                owner=owner, repo=repo, index=pr_number
            )
            for review in islice(reviews, max_to_fetch):
                if not (review.id and review.user and review.submitted_at):
                    logger.warning(
                        "id or user or submitted_at missing in list_pull_reviews API response "
                        f"for {owner}/{repo} {str(pr_number)}"
                    )
                    continue
                reviews_list.append(
                    Review(
                        id=review.id,
                        author=review.user.login or "unknown",
                        state=review.state or "",
                        body=review.body or "",
                        submitted_at=review.submitted_at.isoformat(),
                    )
                )
                if comments_fetched >= max_to_fetch:
                    continue
                review_comments = await (
                    self.forgejo_client.repository.repo_get_pull_review_comments(
                        owner=owner, repo=repo, index=pr_number, id=review.id
                    )
                )
                for comment in islice(review_comments, max_to_fetch - comments_fetched):
                    if not (comment.id and comment.user and comment.created_at):
                        logger.warning(
                            "id or user or created_at missing in get_pull_review_comments API "
                            f"response for {owner}/{repo} {str(pr_number)} {str(review.id)}"
                        )
                        continue
                    # Skip comments from known bot accounts
                    # FIXME Forgejo API does not flag bot accounts generically:
                    # https://codeberg.org/forgejo/forgejo/issues/1867#issuecomment-8852412
                    if (comment.user.login or "") == "forgejo-actions":
                        continue

                    all_comments.append(
                        ReviewComment(
                            id=comment.id,
                            author=comment.user.login or "unknown",
                            body=comment.body or "",
                            created_at=comment.created_at.isoformat(),
                            updated_at=comment.updated_at.isoformat()
                            if comment.updated_at
                            else None,
                            path=comment.path or "",
                            line=comment.position or 0,
                            # FIXME: Forgejo API doesn't appear to provide this
                            is_system=False,
                            resolved=comment.resolver is not None,
                        )
                    )
                    comments_fetched += 1
                    if comments_fetched >= max_to_fetch:
                        break

            # Get recent issue comments (general PR comments) - iteration in thread
            if comments_fetched < max_to_fetch:
                issue_comments: list[
                    Comment
                ] = await self.forgejo_client.issue.get_comments(
                    owner=owner, repo=repo, index=pr_number
                )
                for issue_comment in islice(
                    issue_comments, max_to_fetch - comments_fetched
                ):
                    if not (
                        issue_comment.id
                        and issue_comment.user
                        and issue_comment.created_at
                    ):
                        logger.warning(
                            "id or user or created_at missing in get_comments API "
                            f"response for {owner}/{repo} {str(pr_number)}"
                        )
                        continue
                    # Skip comments from known bot accounts
                    if issue_comment.user.login == "forgejo-actions":
                        continue

                    all_comments.append(
                        ReviewComment(
                            id=issue_comment.id,
                            author=issue_comment.user.login or "unknown",
                            body=issue_comment.body or "",
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

            logger.info(
                "Fetched PR reviews and comments",
                reviews=len(reviews_list),
                comments=len(all_comments),
                max_fetched=self.config.max_comments_to_fetch,
            )

            return reviews_list, all_comments

        except ApiError as e:
            logger.warning("Failed to fetch reviews/comments", error=str(e))
            return [], []

    async def _post_review_impl(
        self, project_id: str, pr_number: int, review_content: str
    ) -> PostReviewResponse:
        """Forgejo-specific: post review.

        Args:
            project_id: Forgejo repository path (e.g., 'owner/repo')
            pr_number: Pull request number
            review_content: The markdown content of the review to post

        Returns:
            Response containing comment information

        Raises:
            ForgejoAPIError: If posting fails
        """
        owner, repo = project_id.split("/")
        try:
            # Create the comment on the PR
            comment: Comment = await self.forgejo_client.issue.create_comment(
                owner=owner,
                repo=repo,
                index=pr_number,
                body=review_content,
            )

            # Return comment information
            return PostReviewResponse(
                id=str(comment.id),
                url=comment.html_url or "",
                created_at=comment.created_at.isoformat() if comment.created_at else "",
                author=comment.user.login or "" if comment.user else "unknown",
            )

        except ApiError as e:
            raise ForgejoAPIError(f"Failed to post review to Forgejo: {e}") from e
        except Exception as e:
            # Catch any other unexpected errors (should be rare)
            raise ForgejoAPIError(f"Unexpected error posting review: {e}") from e

    def get_platform_name(self) -> str:
        """Get the name of the platform."""
        return "forgejo"

    def format_project_url(self, project_id: str) -> str:
        """Format the project URL for Forgejo."""
        return f"{self.config.forgejo_url}/repos/{project_id}"

    # -------------------------------------------------------------------------
    # Forgejo-specific mock method overrides
    # -------------------------------------------------------------------------

    def _get_mock_state(self) -> str:
        """Forgejo uses 'open' state."""
        return "open"

    def _format_mock_pr_url(self, project_id: str, pr_number: int) -> str:
        """Forgejo PR URL format."""
        base_url = self.config.forgejo_url.rstrip("/")
        return f"{base_url}/{project_id}/pull/{pr_number}"

    def _format_mock_comment_url(self, project_id: str, pr_number: int) -> str:
        """Forgejo comment URL format."""
        return (
            f"{self._format_mock_pr_url(project_id, pr_number)}#issuecomment-mock_123"
        )
