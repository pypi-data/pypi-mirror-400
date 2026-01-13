"""Product Hunt API client."""

import logging
from datetime import datetime
from typing import Any, cast

import httpx
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from . import queries
from .exceptions import AuthenticationError, GraphQLError, MutationError
from .models import (
    Collection,
    CollectionConnection,
    CollectionsOrder,
    Comment,
    CommentConnection,
    CommentsOrder,
    Post,
    PostConnection,
    PostsOrder,
    Topic,
    TopicConnection,
    TopicsOrder,
    User,
    UserConnection,
    UserPayload,
    Viewer,
    VoteConnection,
)
from .rate_limiter import RateLimiter, RateLimitInfo

logger = logging.getLogger(__name__)


# Retry configuration
DEFAULT_MAX_RETRIES = 3


def _is_retriable_error(exception: BaseException) -> bool:
    """Check if an exception should trigger a retry."""
    if isinstance(exception, (AuthenticationError, GraphQLError)):
        return False
    if isinstance(exception, (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError)):
        return True
    if isinstance(exception, httpx.HTTPStatusError):
        # 429 is retriable after rate limiter waits
        return exception.response.status_code in (429, 500, 502, 503, 504)
    return False


def _build_pagination_vars(
    first: int | None = None,
    after: str | None = None,
    last: int | None = None,
    before: str | None = None,
) -> dict[str, Any]:
    """Build pagination variables."""
    variables: dict[str, Any] = {}
    if first is not None:
        variables["first"] = first
    if after is not None:
        variables["after"] = after
    if last is not None:
        variables["last"] = last
    if before is not None:
        variables["before"] = before
    return variables


def _build_id_or_slug_vars(
    id: str | None = None,
    slug: str | None = None,
    *,
    id_key: str = "id",
    slug_key: str = "slug",
) -> dict[str, Any]:
    """Build ID or slug variables with validation."""
    if not id and not slug:
        raise ValueError(f"Either {id_key} or {slug_key} must be provided")
    return {id_key: id, slug_key: slug}


def _add_datetime_var(
    variables: dict[str, Any],
    key: str,
    value: datetime | None,
) -> None:
    """Add datetime variable as ISO format if not None."""
    if value is not None:
        variables[key] = value.isoformat()


class _BaseProductHuntClient:
    """Base class with shared logic for sync and async clients."""

    API_URL = "https://api.producthunt.com/v2/api/graphql"

    def __init__(
        self,
        auth: httpx.Auth,
        *,
        auto_wait_on_rate_limit: bool = True,
        max_wait_seconds: float = 900,
        timeout: float = 30.0,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        """Initialize the client.

        Args:
            auth: An httpx.Auth instance for authentication. Use BearerAuth for
                  developer tokens or OAuth access tokens.
            auto_wait_on_rate_limit: If True, automatically wait when rate limited.
            max_wait_seconds: Maximum seconds to wait for rate limit reset.
            timeout: HTTP request timeout in seconds.
            max_retries: Maximum number of retry attempts for transient failures.
        """
        self.auth = auth
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limiter = RateLimiter(
            auto_wait=auto_wait_on_rate_limit,
            max_wait_seconds=max_wait_seconds,
        )

    @property
    def rate_limit_info(self) -> RateLimitInfo:
        """Get current rate limit information."""
        return self.rate_limiter.rate_limit_info


class ProductHuntClient(_BaseProductHuntClient):
    """Synchronous client for the Product Hunt API v2.

    Example:
        ```python
        from producthunt_sdk import ProductHuntClient, BearerAuth

        client = ProductHuntClient(auth=BearerAuth("your_token"))

        posts = client.get_posts(featured=True, first=10)
        for post in posts.nodes:
            print(f"{post.name}: {post.tagline}")
        ```
    """

    def __init__(
        self,
        auth: httpx.Auth,
        *,
        auto_wait_on_rate_limit: bool = True,
        max_wait_seconds: float = 900,
        timeout: float = 30.0,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        super().__init__(
            auth,
            auto_wait_on_rate_limit=auto_wait_on_rate_limit,
            max_wait_seconds=max_wait_seconds,
            timeout=timeout,
            max_retries=max_retries,
        )
        self._client: httpx.Client | None = None

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                timeout=self.timeout,
                headers={"Content-Type": "application/json"},
                auth=self.auth,
            )
        return self._client

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> 'ProductHuntClient':
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def graphql(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute a GraphQL query with automatic retries."""
        query_name = query.split()[0] if query else "unknown"
        logger.debug("Executing GraphQL query", extra={"query_type": query_name, "variables": variables})

        def _log_retry(retry_state: RetryCallState) -> None:
            if retry_state.attempt_number > 1:
                logger.warning(
                    "Retrying request after transient failure",
                    extra={"attempt": retry_state.attempt_number, "exception": str(retry_state.outcome.exception())},
                )

        retry_decorator = retry(
            retry=retry_if_exception(_is_retriable_error),
            stop=stop_after_attempt(self.max_retries + 1),
            wait=wait_exponential(multiplier=1, min=1, max=60),
            before_sleep=_log_retry,
            reraise=True,
        )

        @retry_decorator
        def _make_request() -> dict[str, Any]:
            self.rate_limiter.sync_wait_if_needed()
            client = self._get_client()
            response = client.post(self.API_URL, json={"query": query, "variables": variables or {}})
            rate_info = self.rate_limiter.sync_handle_response(response)

            if rate_info.remaining > 0:
                remaining_pct = (rate_info.remaining / rate_info.limit * 100) if rate_info.limit > 0 else 100
                if remaining_pct < 20:
                    logger.warning(
                        "Rate limit running low",
                        extra={"remaining": rate_info.remaining, "limit": rate_info.limit},
                    )

            if response.status_code == 401:
                raise AuthenticationError("Invalid or expired API token")

            response.raise_for_status()  # 429 handled by tenacity retry after rate limiter waits
            result = response.json()
            if "errors" in result:
                raise GraphQLError(result["errors"])
            return result.get("data", {})

        return _make_request()

    # Posts
    def get_post(self, *, id: str | None = None, slug: str | None = None) -> Post | None:
        """Get a single post by ID or slug."""
        variables = _build_id_or_slug_vars(id, slug)
        data = self.graphql(queries.GET_POST, variables)
        post_data = data.get("post")
        return Post.model_validate(post_data) if post_data else None

    def get_posts(
        self,
        *,
        first: int | None = 20,
        after: str | None = None,
        last: int | None = None,
        before: str | None = None,
        featured: bool | None = None,
        order: PostsOrder = PostsOrder.RANKING,
        posted_after: datetime | None = None,
        posted_before: datetime | None = None,
        topic: str | None = None,
        twitter_url: str | None = None,
    ) -> PostConnection:
        """Get posts with filtering and pagination."""
        variables = _build_pagination_vars(first, after, last, before)
        variables["order"] = order.value
        if featured is not None:
            variables["featured"] = featured
        if topic is not None:
            variables["topic"] = topic
        if twitter_url is not None:
            variables["twitterUrl"] = twitter_url
        _add_datetime_var(variables, "postedAfter", posted_after)
        _add_datetime_var(variables, "postedBefore", posted_before)
        data = self.graphql(queries.GET_POSTS, variables)
        return PostConnection.model_validate(data["posts"])

    def get_post_comments(
        self,
        *,
        post_id: str | None = None,
        post_slug: str | None = None,
        first: int | None = 20,
        after: str | None = None,
        order: CommentsOrder = CommentsOrder.NEWEST,
    ) -> CommentConnection:
        """Get comments for a post."""
        if not post_id and not post_slug:
            raise ValueError("Either post_id or post_slug must be provided")
        variables = _build_pagination_vars(first, after)
        variables["order"] = order.value
        if post_id is not None:
            variables["postId"] = post_id
        if post_slug is not None:
            variables["postSlug"] = post_slug
        data = self.graphql(queries.GET_POST_COMMENTS, variables)
        return CommentConnection.model_validate(data["post"]["comments"])

    def get_post_votes(
        self,
        *,
        post_id: str | None = None,
        post_slug: str | None = None,
        first: int | None = 20,
        after: str | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
    ) -> VoteConnection:
        """Get votes for a post."""
        if not post_id and not post_slug:
            raise ValueError("Either post_id or post_slug must be provided")
        variables = _build_pagination_vars(first, after)
        if post_id is not None:
            variables["postId"] = post_id
        if post_slug is not None:
            variables["postSlug"] = post_slug
        _add_datetime_var(variables, "createdAfter", created_after)
        _add_datetime_var(variables, "createdBefore", created_before)
        data = self.graphql(queries.GET_POST_VOTES, variables)
        return VoteConnection.model_validate(data["post"]["votes"])

    # Users
    def get_user(self, *, id: str | None = None, username: str | None = None) -> User | None:
        """Get a user by ID or username."""
        variables = _build_id_or_slug_vars(id, username, id_key="id", slug_key="username")
        data = self.graphql(queries.GET_USER, variables)
        user_data = data.get("user")
        return User.model_validate(user_data) if user_data else None

    def get_user_posts(
        self,
        *,
        user_id: str | None = None,
        username: str | None = None,
        first: int | None = 20,
        after: str | None = None,
    ) -> PostConnection:
        """Get posts made by a user."""
        if not user_id and not username:
            raise ValueError("Either user_id or username must be provided")
        variables = _build_pagination_vars(first, after)
        if user_id is not None:
            variables["userId"] = user_id
        if username is not None:
            variables["username"] = username
        data = self.graphql(queries.GET_USER_POSTS, variables)
        return PostConnection.model_validate(data["user"]["madePosts"])

    def get_user_voted_posts(
        self,
        *,
        user_id: str | None = None,
        username: str | None = None,
        first: int | None = 20,
        after: str | None = None,
    ) -> PostConnection:
        """Get posts voted by a user."""
        if not user_id and not username:
            raise ValueError("Either user_id or username must be provided")
        variables = _build_pagination_vars(first, after)
        if user_id is not None:
            variables["userId"] = user_id
        if username is not None:
            variables["username"] = username
        data = self.graphql(queries.GET_USER_VOTED_POSTS, variables)
        return PostConnection.model_validate(data["user"]["votedPosts"])

    def get_user_followers(
        self,
        *,
        user_id: str | None = None,
        username: str | None = None,
        first: int | None = 20,
        after: str | None = None,
    ) -> UserConnection:
        """Get followers of a user."""
        if not user_id and not username:
            raise ValueError("Either user_id or username must be provided")
        variables = _build_pagination_vars(first, after)
        if user_id is not None:
            variables["userId"] = user_id
        if username is not None:
            variables["username"] = username
        data = self.graphql(queries.GET_USER_FOLLOWERS, variables)
        return UserConnection.model_validate(data["user"]["followers"])

    def get_user_following(
        self,
        *,
        user_id: str | None = None,
        username: str | None = None,
        first: int | None = 20,
        after: str | None = None,
    ) -> UserConnection:
        """Get users that a user is following."""
        if not user_id and not username:
            raise ValueError("Either user_id or username must be provided")
        variables = _build_pagination_vars(first, after)
        if user_id is not None:
            variables["userId"] = user_id
        if username is not None:
            variables["username"] = username
        data = self.graphql(queries.GET_USER_FOLLOWING, variables)
        return UserConnection.model_validate(data["user"]["following"])

    # Collections
    def get_collection(self, *, id: str | None = None, slug: str | None = None) -> Collection | None:
        """Get a collection by ID or slug."""
        variables = _build_id_or_slug_vars(id, slug)
        data = self.graphql(queries.GET_COLLECTION, variables)
        collection_data = data.get("collection")
        return Collection.model_validate(collection_data) if collection_data else None

    def get_collections(
        self,
        *,
        first: int | None = 20,
        after: str | None = None,
        featured: bool | None = None,
        order: CollectionsOrder = CollectionsOrder.FOLLOWERS_COUNT,
        post_id: str | None = None,
        user_id: str | None = None,
    ) -> CollectionConnection:
        """Get collections with filtering and pagination."""
        variables = _build_pagination_vars(first, after)
        variables["order"] = order.value
        if featured is not None:
            variables["featured"] = featured
        if post_id is not None:
            variables["postId"] = post_id
        if user_id is not None:
            variables["userId"] = user_id
        data = self.graphql(queries.GET_COLLECTIONS, variables)
        return CollectionConnection.model_validate(data["collections"])

    def get_collection_posts(
        self,
        *,
        collection_id: str | None = None,
        collection_slug: str | None = None,
        first: int | None = 20,
        after: str | None = None,
    ) -> PostConnection:
        """Get posts in a collection."""
        if not collection_id and not collection_slug:
            raise ValueError("Either collection_id or collection_slug must be provided")
        variables = _build_pagination_vars(first, after)
        if collection_id is not None:
            variables["collectionId"] = collection_id
        if collection_slug is not None:
            variables["collectionSlug"] = collection_slug
        data = self.graphql(queries.GET_COLLECTION_POSTS, variables)
        return PostConnection.model_validate(data["collection"]["posts"])

    # Topics
    def get_topic(self, *, id: str | None = None, slug: str | None = None) -> Topic | None:
        """Get a topic by ID or slug."""
        variables = _build_id_or_slug_vars(id, slug)
        data = self.graphql(queries.GET_TOPIC, variables)
        topic_data = data.get("topic")
        return Topic.model_validate(topic_data) if topic_data else None

    def get_topics(
        self,
        *,
        first: int | None = 20,
        after: str | None = None,
        order: TopicsOrder = TopicsOrder.FOLLOWERS_COUNT,
        query: str | None = None,
        followed_by_user_id: str | None = None,
    ) -> TopicConnection:
        """Get topics with filtering and pagination."""
        variables = _build_pagination_vars(first, after)
        variables["order"] = order.value
        if query is not None:
            variables["query"] = query
        if followed_by_user_id is not None:
            variables["followedByUserid"] = followed_by_user_id
        data = self.graphql(queries.GET_TOPICS, variables)
        return TopicConnection.model_validate(data["topics"])

    # Comments
    def get_comment(self, id: str) -> Comment | None:
        """Get a comment by ID."""
        data = self.graphql(queries.GET_COMMENT, {"id": id})
        comment_data = data.get("comment")
        return Comment.model_validate(comment_data) if comment_data else None

    # Viewer
    def get_viewer(self) -> Viewer | None:
        """Get the authenticated user's context."""
        data = self.graphql(queries.GET_VIEWER)
        viewer_data = data.get("viewer")
        return Viewer.model_validate(viewer_data) if viewer_data else None

    # Mutations
    def follow_user(self, user_id: str) -> User:
        """Follow a user."""
        data = self.graphql(queries.USER_FOLLOW, {"input": {"userId": user_id}})
        payload = UserPayload.model_validate(data["userFollow"])
        if payload.errors:
            raise MutationError([e.model_dump() for e in payload.errors])
        return cast(User, payload.node)

    def unfollow_user(self, user_id: str) -> User:
        """Unfollow a user."""
        data = self.graphql(queries.USER_FOLLOW_UNDO, {"input": {"userId": user_id}})
        payload = UserPayload.model_validate(data["userFollowUndo"])
        if payload.errors:
            raise MutationError([e.model_dump() for e in payload.errors])
        return cast(User, payload.node)


class AsyncProductHuntClient(_BaseProductHuntClient):
    """Async client for the Product Hunt API v2.

    Example:
        ```python
        from producthunt_sdk import AsyncProductHuntClient, BearerAuth

        async with AsyncProductHuntClient(auth=BearerAuth("your_token")) as client:
            posts = await client.get_posts(featured=True, first=10)
            for post in posts.nodes:
                print(f"{post.name}: {post.tagline}")
        ```
    """

    def __init__(
        self,
        auth: httpx.Auth,
        *,
        auto_wait_on_rate_limit: bool = True,
        max_wait_seconds: float = 900,
        timeout: float = 30.0,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        super().__init__(
            auth,
            auto_wait_on_rate_limit=auto_wait_on_rate_limit,
            max_wait_seconds=max_wait_seconds,
            timeout=timeout,
            max_retries=max_retries,
        )
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={"Content-Type": "application/json"},
                auth=self.auth,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> 'AsyncProductHuntClient':
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def graphql(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute a GraphQL query asynchronously with automatic retries."""
        query_name = query.split()[0] if query else "unknown"
        logger.debug("Executing async GraphQL query", extra={"query_type": query_name, "variables": variables})

        def _log_retry(retry_state: RetryCallState) -> None:
            if retry_state.attempt_number > 1:
                logger.warning(
                    "Retrying async request after transient failure",
                    extra={"attempt": retry_state.attempt_number, "exception": str(retry_state.outcome.exception())},
                )

        async for attempt in AsyncRetrying(
            retry=retry_if_exception(_is_retriable_error),
            stop=stop_after_attempt(self.max_retries + 1),
            wait=wait_exponential(multiplier=1, min=1, max=60),
            before_sleep=_log_retry,
            reraise=True,
        ):
            with attempt:
                await self.rate_limiter.wait_if_needed()
                client = await self._get_client()
                response = await client.post(self.API_URL, json={"query": query, "variables": variables or {}})
                rate_info = await self.rate_limiter.handle_response(response)

                if rate_info.remaining > 0:
                    remaining_pct = (rate_info.remaining / rate_info.limit * 100) if rate_info.limit > 0 else 100
                    if remaining_pct < 20:
                        logger.warning(
                            "Rate limit running low",
                            extra={"remaining": rate_info.remaining, "limit": rate_info.limit},
                        )

                if response.status_code == 401:
                    raise AuthenticationError("Invalid or expired API token")

                response.raise_for_status()  # 429 handled by tenacity retry after rate limiter waits
                result = response.json()
                if "errors" in result:
                    raise GraphQLError(result["errors"])
                return result.get("data", {})

    # Posts
    async def get_post(self, *, id: str | None = None, slug: str | None = None) -> Post | None:
        """Get a single post by ID or slug."""
        variables = _build_id_or_slug_vars(id, slug)
        data = await self.graphql(queries.GET_POST, variables)
        post_data = data.get("post")
        return Post.model_validate(post_data) if post_data else None

    async def get_posts(
        self,
        *,
        first: int | None = 20,
        after: str | None = None,
        last: int | None = None,
        before: str | None = None,
        featured: bool | None = None,
        order: PostsOrder = PostsOrder.RANKING,
        posted_after: datetime | None = None,
        posted_before: datetime | None = None,
        topic: str | None = None,
        twitter_url: str | None = None,
    ) -> PostConnection:
        """Get posts with filtering and pagination."""
        variables = _build_pagination_vars(first, after, last, before)
        variables["order"] = order.value
        if featured is not None:
            variables["featured"] = featured
        if topic is not None:
            variables["topic"] = topic
        if twitter_url is not None:
            variables["twitterUrl"] = twitter_url
        _add_datetime_var(variables, "postedAfter", posted_after)
        _add_datetime_var(variables, "postedBefore", posted_before)
        data = await self.graphql(queries.GET_POSTS, variables)
        return PostConnection.model_validate(data["posts"])

    async def get_post_comments(
        self,
        *,
        post_id: str | None = None,
        post_slug: str | None = None,
        first: int | None = 20,
        after: str | None = None,
        order: CommentsOrder = CommentsOrder.NEWEST,
    ) -> CommentConnection:
        """Get comments for a post."""
        if not post_id and not post_slug:
            raise ValueError("Either post_id or post_slug must be provided")
        variables = _build_pagination_vars(first, after)
        variables["order"] = order.value
        if post_id is not None:
            variables["postId"] = post_id
        if post_slug is not None:
            variables["postSlug"] = post_slug
        data = await self.graphql(queries.GET_POST_COMMENTS, variables)
        return CommentConnection.model_validate(data["post"]["comments"])

    async def get_post_votes(
        self,
        *,
        post_id: str | None = None,
        post_slug: str | None = None,
        first: int | None = 20,
        after: str | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
    ) -> VoteConnection:
        """Get votes for a post."""
        if not post_id and not post_slug:
            raise ValueError("Either post_id or post_slug must be provided")
        variables = _build_pagination_vars(first, after)
        if post_id is not None:
            variables["postId"] = post_id
        if post_slug is not None:
            variables["postSlug"] = post_slug
        _add_datetime_var(variables, "createdAfter", created_after)
        _add_datetime_var(variables, "createdBefore", created_before)
        data = await self.graphql(queries.GET_POST_VOTES, variables)
        return VoteConnection.model_validate(data["post"]["votes"])

    # Users
    async def get_user(self, *, id: str | None = None, username: str | None = None) -> User | None:
        """Get a user by ID or username."""
        variables = _build_id_or_slug_vars(id, username, id_key="id", slug_key="username")
        data = await self.graphql(queries.GET_USER, variables)
        user_data = data.get("user")
        return User.model_validate(user_data) if user_data else None

    async def get_user_posts(
        self,
        *,
        user_id: str | None = None,
        username: str | None = None,
        first: int | None = 20,
        after: str | None = None,
    ) -> PostConnection:
        """Get posts made by a user."""
        if not user_id and not username:
            raise ValueError("Either user_id or username must be provided")
        variables = _build_pagination_vars(first, after)
        if user_id is not None:
            variables["userId"] = user_id
        if username is not None:
            variables["username"] = username
        data = await self.graphql(queries.GET_USER_POSTS, variables)
        return PostConnection.model_validate(data["user"]["madePosts"])

    async def get_user_voted_posts(
        self,
        *,
        user_id: str | None = None,
        username: str | None = None,
        first: int | None = 20,
        after: str | None = None,
    ) -> PostConnection:
        """Get posts voted by a user."""
        if not user_id and not username:
            raise ValueError("Either user_id or username must be provided")
        variables = _build_pagination_vars(first, after)
        if user_id is not None:
            variables["userId"] = user_id
        if username is not None:
            variables["username"] = username
        data = await self.graphql(queries.GET_USER_VOTED_POSTS, variables)
        return PostConnection.model_validate(data["user"]["votedPosts"])

    async def get_user_followers(
        self,
        *,
        user_id: str | None = None,
        username: str | None = None,
        first: int | None = 20,
        after: str | None = None,
    ) -> UserConnection:
        """Get followers of a user."""
        if not user_id and not username:
            raise ValueError("Either user_id or username must be provided")
        variables = _build_pagination_vars(first, after)
        if user_id is not None:
            variables["userId"] = user_id
        if username is not None:
            variables["username"] = username
        data = await self.graphql(queries.GET_USER_FOLLOWERS, variables)
        return UserConnection.model_validate(data["user"]["followers"])

    async def get_user_following(
        self,
        *,
        user_id: str | None = None,
        username: str | None = None,
        first: int | None = 20,
        after: str | None = None,
    ) -> UserConnection:
        """Get users that a user is following."""
        if not user_id and not username:
            raise ValueError("Either user_id or username must be provided")
        variables = _build_pagination_vars(first, after)
        if user_id is not None:
            variables["userId"] = user_id
        if username is not None:
            variables["username"] = username
        data = await self.graphql(queries.GET_USER_FOLLOWING, variables)
        return UserConnection.model_validate(data["user"]["following"])

    # Collections
    async def get_collection(self, *, id: str | None = None, slug: str | None = None) -> Collection | None:
        """Get a collection by ID or slug."""
        variables = _build_id_or_slug_vars(id, slug)
        data = await self.graphql(queries.GET_COLLECTION, variables)
        collection_data = data.get("collection")
        return Collection.model_validate(collection_data) if collection_data else None

    async def get_collections(
        self,
        *,
        first: int | None = 20,
        after: str | None = None,
        featured: bool | None = None,
        order: CollectionsOrder = CollectionsOrder.FOLLOWERS_COUNT,
        post_id: str | None = None,
        user_id: str | None = None,
    ) -> CollectionConnection:
        """Get collections with filtering and pagination."""
        variables = _build_pagination_vars(first, after)
        variables["order"] = order.value
        if featured is not None:
            variables["featured"] = featured
        if post_id is not None:
            variables["postId"] = post_id
        if user_id is not None:
            variables["userId"] = user_id
        data = await self.graphql(queries.GET_COLLECTIONS, variables)
        return CollectionConnection.model_validate(data["collections"])

    async def get_collection_posts(
        self,
        *,
        collection_id: str | None = None,
        collection_slug: str | None = None,
        first: int | None = 20,
        after: str | None = None,
    ) -> PostConnection:
        """Get posts in a collection."""
        if not collection_id and not collection_slug:
            raise ValueError("Either collection_id or collection_slug must be provided")
        variables = _build_pagination_vars(first, after)
        if collection_id is not None:
            variables["collectionId"] = collection_id
        if collection_slug is not None:
            variables["collectionSlug"] = collection_slug
        data = await self.graphql(queries.GET_COLLECTION_POSTS, variables)
        return PostConnection.model_validate(data["collection"]["posts"])

    # Topics
    async def get_topic(self, *, id: str | None = None, slug: str | None = None) -> Topic | None:
        """Get a topic by ID or slug."""
        variables = _build_id_or_slug_vars(id, slug)
        data = await self.graphql(queries.GET_TOPIC, variables)
        topic_data = data.get("topic")
        return Topic.model_validate(topic_data) if topic_data else None

    async def get_topics(
        self,
        *,
        first: int | None = 20,
        after: str | None = None,
        order: TopicsOrder = TopicsOrder.FOLLOWERS_COUNT,
        query: str | None = None,
        followed_by_user_id: str | None = None,
    ) -> TopicConnection:
        """Get topics with filtering and pagination."""
        variables = _build_pagination_vars(first, after)
        variables["order"] = order.value
        if query is not None:
            variables["query"] = query
        if followed_by_user_id is not None:
            variables["followedByUserid"] = followed_by_user_id
        data = await self.graphql(queries.GET_TOPICS, variables)
        return TopicConnection.model_validate(data["topics"])

    # Comments
    async def get_comment(self, id: str) -> Comment | None:
        """Get a comment by ID."""
        data = await self.graphql(queries.GET_COMMENT, {"id": id})
        comment_data = data.get("comment")
        return Comment.model_validate(comment_data) if comment_data else None

    # Viewer
    async def get_viewer(self) -> Viewer | None:
        """Get the authenticated user's context."""
        data = await self.graphql(queries.GET_VIEWER)
        viewer_data = data.get("viewer")
        return Viewer.model_validate(viewer_data) if viewer_data else None

    # Mutations
    async def follow_user(self, user_id: str) -> User:
        """Follow a user."""
        data = await self.graphql(queries.USER_FOLLOW, {"input": {"userId": user_id}})
        payload = UserPayload.model_validate(data["userFollow"])
        if payload.errors:
            raise MutationError([e.model_dump() for e in payload.errors])
        return cast(User, payload.node)

    async def unfollow_user(self, user_id: str) -> User:
        """Unfollow a user."""
        data = await self.graphql(queries.USER_FOLLOW_UNDO, {"input": {"userId": user_id}})
        payload = UserPayload.model_validate(data["userFollowUndo"])
        if payload.errors:
            raise MutationError([e.model_dump() for e in payload.errors])
        return cast(User, payload.node)
