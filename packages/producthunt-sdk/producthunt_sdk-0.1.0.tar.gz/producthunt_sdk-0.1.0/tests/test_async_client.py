"""Tests for AsyncProductHuntClient."""

import httpx
import pytest

from producthunt_sdk import AsyncProductHuntClient, BearerAuth, PostsOrder
from producthunt_sdk.exceptions import AuthenticationError, GraphQLError

from .conftest import make_connection, make_graphql_error_response, make_graphql_response


@pytest.mark.asyncio
class TestAsyncClientInit:
    async def test_default_initialization(self):
        client = AsyncProductHuntClient(auth=BearerAuth("test_token"))
        assert client.auth.token == "test_token"
        assert client.timeout == 30.0

    async def test_context_manager(self, mock_async_transport):
        transport = mock_async_transport(response_data=make_graphql_response({"viewer": None}))
        async with AsyncProductHuntClient(auth=BearerAuth("test")) as client:
            client._client = httpx.AsyncClient(transport=transport)
            await client.get_viewer()
        assert client._client is None


@pytest.mark.asyncio
class TestAsyncGetPost:
    async def test_get_post_by_slug(self, mock_async_transport, sample_post):
        transport = mock_async_transport(
            response_data=make_graphql_response({"post": sample_post})
        )
        client = AsyncProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.AsyncClient(transport=transport)

        post = await client.get_post(slug="test-product")

        assert post is not None
        assert post.name == "Test Product"

    async def test_get_post_not_found(self, mock_async_transport):
        transport = mock_async_transport(response_data=make_graphql_response({"post": None}))
        client = AsyncProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.AsyncClient(transport=transport)

        assert await client.get_post(id="nonexistent") is None


@pytest.mark.asyncio
class TestAsyncGetPosts:
    async def test_get_posts(self, mock_async_transport, sample_post):
        transport = mock_async_transport(
            response_data=make_graphql_response({"posts": make_connection([sample_post])})
        )
        client = AsyncProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.AsyncClient(transport=transport)

        result = await client.get_posts(featured=True, order=PostsOrder.VOTES)

        assert result.total_count == 1
        assert result.nodes[0].name == "Test Product"


@pytest.mark.asyncio
class TestAsyncGetUser:
    async def test_get_user(self, mock_async_transport, sample_user):
        transport = mock_async_transport(
            response_data=make_graphql_response({"user": sample_user})
        )
        client = AsyncProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.AsyncClient(transport=transport)

        user = await client.get_user(username="testuser")

        assert user is not None
        assert user.username == "testuser"


@pytest.mark.asyncio
class TestAsyncGetCollection:
    async def test_get_collection(self, mock_async_transport, sample_collection):
        transport = mock_async_transport(
            response_data=make_graphql_response({"collection": sample_collection})
        )
        client = AsyncProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.AsyncClient(transport=transport)

        collection = await client.get_collection(slug="best-ai-tools")

        assert collection is not None
        assert collection.name == "Best AI Tools"


@pytest.mark.asyncio
class TestAsyncGetTopic:
    async def test_get_topic(self, mock_async_transport, sample_topic):
        transport = mock_async_transport(
            response_data=make_graphql_response({"topic": sample_topic})
        )
        client = AsyncProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.AsyncClient(transport=transport)

        topic = await client.get_topic(slug="artificial-intelligence")

        assert topic is not None
        assert topic.name == "Artificial Intelligence"


@pytest.mark.asyncio
class TestAsyncErrorHandling:
    async def test_authentication_error(self, mock_async_transport):
        transport = mock_async_transport(status_code=401, response_data={})
        client = AsyncProductHuntClient(auth=BearerAuth("invalid"))
        client._client = httpx.AsyncClient(transport=transport)

        with pytest.raises(AuthenticationError):
            await client.get_posts()

    async def test_graphql_error(self, mock_async_transport):
        transport = mock_async_transport(
            response_data=make_graphql_error_response([{"message": "Invalid query"}])
        )
        client = AsyncProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.AsyncClient(transport=transport)

        with pytest.raises(GraphQLError):
            await client.get_posts()

    async def test_rate_limit_headers_tracked(self, mock_async_transport, sample_post):
        transport = mock_async_transport(
            response_data=make_graphql_response({"posts": make_connection([sample_post])}),
            headers={
                "X-Rate-Limit-Limit": "6250",
                "X-Rate-Limit-Remaining": "4000",
                "X-Rate-Limit-Reset": "300",
            },
        )
        client = AsyncProductHuntClient(auth=BearerAuth("test"))
        client._client = httpx.AsyncClient(transport=transport)

        await client.get_posts()

        assert client.rate_limit_info.remaining == 4000
