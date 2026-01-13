"""Tests for synchronous ProductHuntClient."""

import json
from datetime import datetime

import httpx
import pytest

from producthunt_sdk import (
    BearerAuth,
    CollectionsOrder,
    CommentsOrder,
    PostsOrder,
    ProductHuntClient,
    TopicsOrder,
)
from producthunt_sdk.exceptions import AuthenticationError, GraphQLError, MutationError

from .conftest import make_connection, make_graphql_error_response, make_graphql_response


class TestClientInit:
    """Tests for client initialization."""

    def test_default_initialization(self):
        client = ProductHuntClient(auth=BearerAuth("test_token"))
        assert client.auth.token == "test_token"
        assert client.timeout == 30.0
        assert client.rate_limiter.auto_wait is True

    def test_custom_initialization(self):
        client = ProductHuntClient(
            auth=BearerAuth("test_token"),
            auto_wait_on_rate_limit=False,
            timeout=10.0,
        )
        assert client.timeout == 10.0
        assert client.rate_limiter.auto_wait is False

    def test_context_manager(self, mock_transport):
        transport = mock_transport(response_data=make_graphql_response({"viewer": None}))
        with ProductHuntClient(auth=BearerAuth("test")) as client:
            client._client = httpx.Client(transport=transport)
            client.get_viewer()
        assert client._client is None


class TestGetPost:
    """Tests for get_post method."""

    def test_get_post_by_id(self, mock_transport, sample_post):
        transport = mock_transport(response_data=make_graphql_response({"post": sample_post}))
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        post = client.get_post(id="456")

        assert post is not None
        assert post.id == "456"
        assert post.name == "Test Product"

    def test_get_post_by_slug(self, mock_transport, sample_post):
        transport = mock_transport(response_data=make_graphql_response({"post": sample_post}))
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        post = client.get_post(slug="test-product")
        assert post is not None
        assert post.slug == "test-product"

    def test_get_post_not_found(self, mock_transport):
        transport = mock_transport(response_data=make_graphql_response({"post": None}))
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        assert client.get_post(id="nonexistent") is None

    def test_get_post_requires_id_or_slug(self):
        client = ProductHuntClient(auth=BearerAuth("test"))
        with pytest.raises(ValueError, match="Either id or slug must be provided"):
            client.get_post()


class TestGetPosts:
    """Tests for get_posts method."""

    def test_get_posts_default(self, mock_transport, sample_post):
        transport = mock_transport(
            response_data=make_graphql_response({"posts": make_connection([sample_post])})
        )
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        result = client.get_posts()

        assert result.total_count == 1
        assert len(result.nodes) == 1
        assert result.nodes[0].name == "Test Product"

    def test_get_posts_with_filters(self, mock_transport, sample_post):
        transport = mock_transport(
            response_data=make_graphql_response({"posts": make_connection([sample_post])})
        )
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        result = client.get_posts(
            featured=True,
            first=10,
            order=PostsOrder.VOTES,
            topic="ai",
            posted_after=datetime(2023, 1, 1),
        )

        assert len(result.nodes) == 1
        request = transport.requests[0]
        body = json.loads(request.content)
        assert body["variables"]["featured"] is True
        assert body["variables"]["order"] == "VOTES"

    def test_get_posts_pagination(self, mock_transport, sample_post):
        transport = mock_transport(
            response_data=make_graphql_response({
                "posts": make_connection([sample_post], {
                    "endCursor": "next_cursor",
                    "hasNextPage": True,
                    "hasPreviousPage": False,
                    "startCursor": "start",
                })
            })
        )
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        result = client.get_posts(first=20, after="cursor123")

        assert result.page_info.end_cursor == "next_cursor"
        assert result.page_info.has_next_page is True


class TestGetUser:
    """Tests for user-related methods."""

    def test_get_user_by_username(self, mock_transport, sample_user):
        transport = mock_transport(response_data=make_graphql_response({"user": sample_user}))
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        user = client.get_user(username="testuser")

        assert user is not None
        assert user.username == "testuser"

    def test_get_user_not_found(self, mock_transport):
        transport = mock_transport(response_data=make_graphql_response({"user": None}))
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        assert client.get_user(username="nonexistent") is None

    def test_get_user_requires_id_or_username(self):
        client = ProductHuntClient(auth=BearerAuth("test"))
        with pytest.raises(ValueError, match="Either id or username"):
            client.get_user()


class TestGetCollection:
    """Tests for collection-related methods."""

    def test_get_collection(self, mock_transport, sample_collection):
        transport = mock_transport(
            response_data=make_graphql_response({"collection": sample_collection})
        )
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        collection = client.get_collection(slug="best-ai-tools")

        assert collection is not None
        assert collection.name == "Best AI Tools"

    def test_get_collections(self, mock_transport, sample_collection):
        transport = mock_transport(
            response_data=make_graphql_response({"collections": make_connection([sample_collection])})
        )
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        result = client.get_collections(order=CollectionsOrder.FOLLOWERS_COUNT)

        assert len(result.nodes) == 1


class TestGetTopic:
    """Tests for topic-related methods."""

    def test_get_topic(self, mock_transport, sample_topic):
        transport = mock_transport(response_data=make_graphql_response({"topic": sample_topic}))
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        topic = client.get_topic(slug="artificial-intelligence")

        assert topic is not None
        assert topic.name == "Artificial Intelligence"

    def test_get_topics(self, mock_transport, sample_topic):
        transport = mock_transport(
            response_data=make_graphql_response({"topics": make_connection([sample_topic])})
        )
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        result = client.get_topics(query="ai", order=TopicsOrder.FOLLOWERS_COUNT)

        assert len(result.nodes) == 1


class TestGetComment:
    """Tests for comment-related methods."""

    def test_get_comment(self, mock_transport, sample_comment):
        transport = mock_transport(response_data=make_graphql_response({"comment": sample_comment}))
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        comment = client.get_comment("com123")

        assert comment is not None
        assert comment.body == "This is a great product!"

    def test_get_post_comments(self, mock_transport, sample_comment):
        transport = mock_transport(
            response_data=make_graphql_response({"post": {"comments": make_connection([sample_comment])}})
        )
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        result = client.get_post_comments(post_slug="test-product", order=CommentsOrder.VOTES_COUNT)

        assert len(result.nodes) == 1


class TestGetViewer:
    """Tests for viewer method."""

    def test_get_viewer(self, mock_transport, sample_user):
        transport = mock_transport(
            response_data=make_graphql_response({"viewer": {"user": sample_user}})
        )
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        viewer = client.get_viewer()

        assert viewer is not None
        assert viewer.user.username == "testuser"

    def test_get_viewer_not_authenticated(self, mock_transport):
        transport = mock_transport(response_data=make_graphql_response({"viewer": None}))
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        assert client.get_viewer() is None


class TestErrorHandling:
    """Tests for error handling."""

    def test_authentication_error(self, mock_transport):
        transport = mock_transport(status_code=401, response_data={})
        client = ProductHuntClient(auth=BearerAuth("invalid"))
        client._client = httpx.Client(transport=transport)

        with pytest.raises(AuthenticationError):
            client.get_posts()

    def test_graphql_error(self, mock_transport):
        transport = mock_transport(
            response_data=make_graphql_error_response([{"message": "Invalid query"}])
        )
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        with pytest.raises(GraphQLError) as exc_info:
            client.get_posts()

        assert "Invalid query" in str(exc_info.value)

    def test_rate_limit_headers_tracked(self, mock_transport, sample_post):
        transport = mock_transport(
            response_data=make_graphql_response({"posts": make_connection([sample_post])}),
            headers={
                "X-Rate-Limit-Limit": "6250",
                "X-Rate-Limit-Remaining": "5000",
                "X-Rate-Limit-Reset": "600",
            },
        )
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        client.get_posts()

        assert client.rate_limit_info.limit == 6250
        assert client.rate_limit_info.remaining == 5000

    def test_server_error_500(self, mock_transport):
        """Test handling of 500 server error."""
        transport = mock_transport(status_code=500, response_data={"error": "Internal Server Error"})
        client = ProductHuntClient(auth=BearerAuth("test"), max_retries=1)
        client._client = httpx.Client(transport=transport)

        with pytest.raises(httpx.HTTPStatusError):
            client.get_posts()


class TestGetPostVotes:
    """Tests for get_post_votes method."""

    def test_get_post_votes(self, mock_transport, sample_user):
        vote_data = {
            "id": "vote123",
            "userId": "123",
            "createdAt": "2023-06-15T12:00:00Z",
            "user": sample_user,
        }
        transport = mock_transport(
            response_data=make_graphql_response({"post": {"votes": make_connection([vote_data])}})
        )
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        result = client.get_post_votes(post_slug="test-product")

        assert len(result.nodes) == 1
        assert result.nodes[0].id == "vote123"

    def test_get_post_votes_requires_id_or_slug(self):
        client = ProductHuntClient(auth=BearerAuth("test"))
        with pytest.raises(ValueError, match="Either post_id or post_slug"):
            client.get_post_votes()


class TestGetCollectionPosts:
    """Tests for get_collection_posts method."""

    def test_get_collection_posts(self, mock_transport, sample_post):
        transport = mock_transport(
            response_data=make_graphql_response({"collection": {"posts": make_connection([sample_post])}})
        )
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        result = client.get_collection_posts(collection_id="col123")

        assert len(result.nodes) == 1
        assert result.nodes[0].name == "Test Product"


class TestUserMethods:
    """Tests for user-related list methods."""

    def test_get_user_posts(self, mock_transport, sample_post):
        transport = mock_transport(
            response_data=make_graphql_response({"user": {"madePosts": make_connection([sample_post])}})
        )
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        result = client.get_user_posts(username="testuser")

        assert len(result.nodes) == 1

    def test_get_user_voted_posts(self, mock_transport, sample_post):
        transport = mock_transport(
            response_data=make_graphql_response({"user": {"votedPosts": make_connection([sample_post])}})
        )
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        result = client.get_user_voted_posts(username="testuser")

        assert len(result.nodes) == 1

    def test_get_user_followers(self, mock_transport, sample_user):
        transport = mock_transport(
            response_data=make_graphql_response({"user": {"followers": make_connection([sample_user])}})
        )
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        result = client.get_user_followers(username="testuser")

        assert len(result.nodes) == 1

    def test_get_user_following(self, mock_transport, sample_user):
        transport = mock_transport(
            response_data=make_graphql_response({"user": {"following": make_connection([sample_user])}})
        )
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        result = client.get_user_following(username="testuser")

        assert len(result.nodes) == 1

    def test_get_user_posts_requires_id_or_username(self):
        client = ProductHuntClient(auth=BearerAuth("test"))
        with pytest.raises(ValueError):
            client.get_user_posts()


class TestMutations:
    """Tests for mutation methods."""

    def test_follow_user_success(self, mock_transport, sample_user):
        transport = mock_transport(
            response_data=make_graphql_response({
                "userFollow": {"node": sample_user, "errors": []}
            })
        )
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        result = client.follow_user(user_id="123")

        assert result is not None
        assert result.username == "testuser"

    def test_follow_user_with_errors(self, mock_transport):
        transport = mock_transport(
            response_data=make_graphql_response({
                "userFollow": {
                    "node": None,
                    "errors": [{"field": "user_id", "message": "User not found"}]
                }
            })
        )
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        with pytest.raises(MutationError) as exc_info:
            client.follow_user(user_id="invalid")

        assert "User not found" in str(exc_info.value)

    def test_unfollow_user_success(self, mock_transport, sample_user):
        transport = mock_transport(
            response_data=make_graphql_response({
                "userFollowUndo": {"node": sample_user, "errors": []}
            })
        )
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        result = client.unfollow_user(user_id="123")

        assert result is not None
        assert result.username == "testuser"


class TestGraphQLMethod:
    """Tests for raw graphql method."""

    def test_graphql_with_variables(self, mock_transport):
        transport = mock_transport(
            response_data=make_graphql_response({"test": "result"})
        )
        client = ProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.Client(transport=transport)

        result = client.graphql("query Test($id: ID!) { post(id: $id) { name } }", {"id": "123"})

        assert result == {"test": "result"}
        request = transport.requests[0]
        body = json.loads(request.content)
        assert body["variables"] == {"id": "123"}
