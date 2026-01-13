"""Test fixtures for Product Hunt SDK tests."""

from collections.abc import Callable
from typing import Any

import httpx
import pytest

SAMPLE_USER = {
    "id": "123",
    "name": "Test User",
    "username": "testuser",
    "headline": "Building cool stuff",
    "profileImage": "https://example.com/avatar.jpg",
    "twitterUsername": "testuser",
    "websiteUrl": "https://example.com",
    "url": "https://producthunt.com/@testuser",
    "isFollowing": False,
    "isMaker": True,
    "isViewer": False,
    "createdAt": "2023-01-01T00:00:00Z",
}

SAMPLE_POST = {
    "id": "456",
    "name": "Test Product",
    "slug": "test-product",
    "tagline": "A test product for testing",
    "description": "This is a test product description",
    "url": "https://producthunt.com/posts/test-product",
    "website": "https://testproduct.com",
    "votesCount": 500,
    "commentsCount": 25,
    "reviewsRating": 4.5,
    "isVoted": False,
    "isCollected": False,
    "featuredAt": "2023-06-15T00:00:00Z",
    "createdAt": "2023-06-15T00:00:00Z",
    "thumbnail": {
        "type": "image",
        "url": "https://example.com/thumb.jpg",
        "videoUrl": None,
    },
    "user": SAMPLE_USER,
    "makers": [SAMPLE_USER],
}

SAMPLE_TOPIC = {
    "id": "789",
    "name": "Artificial Intelligence",
    "slug": "artificial-intelligence",
    "description": "AI and machine learning products",
    "followersCount": 10000,
    "postsCount": 500,
    "image": "https://example.com/topic.jpg",
    "url": "https://producthunt.com/topics/artificial-intelligence",
    "isFollowing": False,
    "createdAt": "2020-01-01T00:00:00Z",
}

SAMPLE_COLLECTION = {
    "id": "col123",
    "name": "Best AI Tools",
    "tagline": "Top AI products",
    "description": "A collection of the best AI tools",
    "coverImage": "https://example.com/cover.jpg",
    "url": "https://producthunt.com/collections/best-ai-tools",
    "followersCount": 500,
    "isFollowing": False,
    "userId": "123",
    "featuredAt": "2023-06-01T00:00:00Z",
    "createdAt": "2023-05-01T00:00:00Z",
    "user": SAMPLE_USER,
}

SAMPLE_COMMENT = {
    "id": "com123",
    "body": "This is a great product!",
    "url": "https://producthunt.com/posts/test-product#comment-123",
    "votesCount": 10,
    "isVoted": False,
    "userId": "123",
    "parentId": None,
    "createdAt": "2023-06-15T12:00:00Z",
    "user": SAMPLE_USER,
}

SAMPLE_PAGE_INFO = {
    "endCursor": "cursor123",
    "hasNextPage": True,
    "hasPreviousPage": False,
    "startCursor": "cursor000",
}


def make_connection(
    nodes: list[dict[str, Any]], page_info: dict[str, Any] | None = None
) -> dict[str, Any]:
    return {
        "edges": [{"cursor": f"cursor{i}", "node": node} for i, node in enumerate(nodes)],
        "pageInfo": page_info or SAMPLE_PAGE_INFO,
        "totalCount": len(nodes),
    }


def make_graphql_response(data: dict[str, Any]) -> dict[str, Any]:
    return {"data": data}


def make_graphql_error_response(errors: list[dict[str, Any]]) -> dict[str, Any]:
    return {"errors": errors}


class MockTransport(httpx.BaseTransport):
    def __init__(
        self,
        response_data: dict[str, Any] | None = None,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        handler: Callable[[httpx.Request], httpx.Response] | None = None,
    ):
        self.response_data = response_data or {}
        self.status_code = status_code
        self.headers = headers or {}
        self.handler = handler
        self.requests: list[httpx.Request] = []

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if self.handler:
            return self.handler(request)

        default_headers = {
            "X-Rate-Limit-Limit": "6250",
            "X-Rate-Limit-Remaining": "6000",
            "X-Rate-Limit-Reset": "900",
        }
        default_headers.update(self.headers)
        return httpx.Response(
            status_code=self.status_code,
            json=self.response_data,
            headers=default_headers,
        )


class MockAsyncTransport(httpx.AsyncBaseTransport):
    def __init__(
        self,
        response_data: dict[str, Any] | None = None,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        handler: Callable[[httpx.Request], httpx.Response] | None = None,
    ):
        self.response_data = response_data or {}
        self.status_code = status_code
        self.headers = headers or {}
        self.handler = handler
        self.requests: list[httpx.Request] = []

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if self.handler:
            return self.handler(request)

        default_headers = {
            "X-Rate-Limit-Limit": "6250",
            "X-Rate-Limit-Remaining": "6000",
            "X-Rate-Limit-Reset": "900",
        }
        default_headers.update(self.headers)
        return httpx.Response(
            status_code=self.status_code,
            json=self.response_data,
            headers=default_headers,
        )


@pytest.fixture
def mock_transport():
    def factory(
        response_data: dict[str, Any] | None = None,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        handler: Callable[[httpx.Request], httpx.Response] | None = None,
    ) -> MockTransport:
        return MockTransport(response_data, status_code, headers, handler)
    return factory


@pytest.fixture
def mock_async_transport():
    def factory(
        response_data: dict[str, Any] | None = None,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        handler: Callable[[httpx.Request], httpx.Response] | None = None,
    ) -> MockAsyncTransport:
        return MockAsyncTransport(response_data, status_code, headers, handler)
    return factory


@pytest.fixture
def sample_user():
    return SAMPLE_USER.copy()


@pytest.fixture
def sample_post():
    return SAMPLE_POST.copy()


@pytest.fixture
def sample_topic():
    return SAMPLE_TOPIC.copy()


@pytest.fixture
def sample_collection():
    return SAMPLE_COLLECTION.copy()


@pytest.fixture
def sample_comment():
    return SAMPLE_COMMENT.copy()
