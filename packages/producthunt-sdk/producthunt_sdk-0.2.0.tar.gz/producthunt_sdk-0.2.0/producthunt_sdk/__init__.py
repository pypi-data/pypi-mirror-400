"""Product Hunt SDK - Python client for the Product Hunt API v2."""

from .auth import BearerAuth, ClientCredentials, OAuth2, TokenCache
from .client import AsyncProductHuntClient, ProductHuntClient
from .exceptions import (
    AuthenticationError,
    GraphQLError,
    MutationError,
    ProductHuntError,
    RateLimitError,
)
from .models import (
    Collection,
    CollectionConnection,
    CollectionEdge,
    CollectionsOrder,
    Comment,
    CommentConnection,
    CommentEdge,
    CommentsOrder,
    Error,
    Media,
    PageInfo,
    Post,
    PostConnection,
    PostEdge,
    PostsOrder,
    Topic,
    TopicConnection,
    TopicEdge,
    TopicsOrder,
    User,
    UserConnection,
    UserEdge,
    UserPayload,
    Viewer,
    Vote,
    VoteConnection,
    VoteEdge,
)
from .rate_limiter import RateLimiter, RateLimitInfo

__version__ = "0.2.0"

__all__ = [
    # Clients
    "ProductHuntClient",
    "AsyncProductHuntClient",
    # Auth
    "BearerAuth",
    "ClientCredentials",
    "OAuth2",
    "TokenCache",
    # Exceptions
    "ProductHuntError",
    "AuthenticationError",
    "GraphQLError",
    "MutationError",
    "RateLimitError",
    # Rate limiting
    "RateLimiter",
    "RateLimitInfo",
    # Models
    "PageInfo",
    "Error",
    "Media",
    "Topic",
    "TopicConnection",
    "TopicEdge",
    "User",
    "UserConnection",
    "UserEdge",
    "Comment",
    "CommentConnection",
    "CommentEdge",
    "Vote",
    "VoteConnection",
    "VoteEdge",
    "Post",
    "PostConnection",
    "PostEdge",
    "Collection",
    "CollectionConnection",
    "CollectionEdge",
    "UserPayload",
    "Viewer",
    # Enums
    "PostsOrder",
    "CollectionsOrder",
    "CommentsOrder",
    "TopicsOrder",
]
