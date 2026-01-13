"""Data models for Product Hunt API responses."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


# Base model with alias support
class _BaseModel(BaseModel):
    """Base model with camelCase alias support."""
    model_config = ConfigDict(populate_by_name=True)


# Enums
class PostsOrder(str, Enum):
    """Order for Posts queries."""
    FEATURED_AT = "FEATURED_AT"
    NEWEST = "NEWEST"
    RANKING = "RANKING"
    VOTES = "VOTES"


class CollectionsOrder(str, Enum):
    """Order for Collections queries."""
    FEATURED_AT = "FEATURED_AT"
    FOLLOWERS_COUNT = "FOLLOWERS_COUNT"
    NEWEST = "NEWEST"


class CommentsOrder(str, Enum):
    """Order for Comments queries."""
    NEWEST = "NEWEST"
    VOTES_COUNT = "VOTES_COUNT"


class TopicsOrder(str, Enum):
    """Order for Topics queries."""
    FOLLOWERS_COUNT = "FOLLOWERS_COUNT"
    NEWEST = "NEWEST"


# Base models
class PageInfo(_BaseModel):
    """Pagination information."""
    end_cursor: str | None = Field(None, alias="endCursor")
    has_next_page: bool = Field(alias="hasNextPage")
    has_previous_page: bool = Field(alias="hasPreviousPage")
    start_cursor: str | None = Field(None, alias="startCursor")


class Error(_BaseModel):
    """API error."""
    field: str
    message: str


# Core models
class Media(_BaseModel):
    """Media object (image/video)."""
    type: str
    url: str
    video_url: str | None = Field(None, alias="videoUrl")


class Topic(_BaseModel):
    """A topic/category."""
    id: str
    name: str
    slug: str
    description: str = ""
    followers_count: int = Field(0, alias="followersCount")
    posts_count: int = Field(0, alias="postsCount")
    image: str | None = None
    url: str = ""
    is_following: bool = Field(False, alias="isFollowing")
    created_at: datetime | None = Field(None, alias="createdAt")


class TopicEdge(_BaseModel):
    """Edge for Topic connection."""
    cursor: str
    node: Topic


class TopicConnection(_BaseModel):
    """Connection for Topic pagination."""
    edges: list[TopicEdge]
    page_info: PageInfo = Field(alias="pageInfo")
    total_count: int = Field(alias="totalCount")

    @property
    def nodes(self) -> list[Topic]:
        return [edge.node for edge in self.edges]


class User(_BaseModel):
    """A Product Hunt user."""
    id: str
    name: str
    username: str
    headline: str | None = None
    cover_image: str | None = Field(None, alias="coverImage")
    profile_image: str | None = Field(None, alias="profileImage")
    twitter_username: str | None = Field(None, alias="twitterUsername")
    website_url: str | None = Field(None, alias="websiteUrl")
    url: str = ""
    is_following: bool = Field(False, alias="isFollowing")
    is_maker: bool = Field(False, alias="isMaker")
    is_viewer: bool = Field(False, alias="isViewer")
    created_at: datetime | None = Field(None, alias="createdAt")


class UserEdge(_BaseModel):
    """Edge for User connection."""
    cursor: str
    node: User


class UserConnection(_BaseModel):
    """Connection for User pagination."""
    edges: list[UserEdge]
    page_info: PageInfo = Field(alias="pageInfo")
    total_count: int = Field(alias="totalCount")

    @property
    def nodes(self) -> list[User]:
        return [edge.node for edge in self.edges]


class Comment(_BaseModel):
    """A comment on a post."""
    id: str
    body: str
    url: str = ""
    votes_count: int = Field(0, alias="votesCount")
    is_voted: bool = Field(False, alias="isVoted")
    user: User | None = None
    user_id: str = Field("", alias="userId")
    parent_id: str | None = Field(None, alias="parentId")
    created_at: datetime | None = Field(None, alias="createdAt")


class CommentEdge(_BaseModel):
    """Edge for Comment connection."""
    cursor: str
    node: Comment


class CommentConnection(_BaseModel):
    """Connection for Comment pagination."""
    edges: list[CommentEdge]
    page_info: PageInfo = Field(alias="pageInfo")
    total_count: int = Field(alias="totalCount")

    @property
    def nodes(self) -> list[Comment]:
        return [edge.node for edge in self.edges]


class Vote(_BaseModel):
    """A vote on a post or comment."""
    id: str
    user: User | None = None
    user_id: str = Field("", alias="userId")
    created_at: datetime | None = Field(None, alias="createdAt")


class VoteEdge(_BaseModel):
    """Edge for Vote connection."""
    cursor: str
    node: Vote


class VoteConnection(_BaseModel):
    """Connection for Vote pagination."""
    edges: list[VoteEdge]
    page_info: PageInfo = Field(alias="pageInfo")
    total_count: int = Field(alias="totalCount")

    @property
    def nodes(self) -> list[Vote]:
        return [edge.node for edge in self.edges]


class Post(_BaseModel):
    """A Product Hunt post."""
    id: str
    name: str
    slug: str
    tagline: str
    description: str | None = None
    url: str = ""
    website: str = ""
    votes_count: int = Field(0, alias="votesCount")
    comments_count: int = Field(0, alias="commentsCount")
    reviews_rating: float = Field(0.0, alias="reviewsRating")
    is_voted: bool = Field(False, alias="isVoted")
    is_collected: bool = Field(False, alias="isCollected")
    thumbnail: Media | None = None
    media: list[Media] = Field(default_factory=list)
    makers: list[User] = Field(default_factory=list)
    user: User | None = None
    user_id: str = Field("", alias="userId")
    featured_at: datetime | None = Field(None, alias="featuredAt")
    created_at: datetime | None = Field(None, alias="createdAt")


class PostEdge(_BaseModel):
    """Edge for Post connection."""
    cursor: str
    node: Post


class PostConnection(_BaseModel):
    """Connection for Post pagination."""
    edges: list[PostEdge]
    page_info: PageInfo = Field(alias="pageInfo")
    total_count: int = Field(alias="totalCount")

    @property
    def nodes(self) -> list[Post]:
        return [edge.node for edge in self.edges]


class Collection(_BaseModel):
    """A collection of posts."""
    id: str
    name: str
    tagline: str
    description: str | None = None
    cover_image: str | None = Field(None, alias="coverImage")
    url: str = ""
    followers_count: int = Field(0, alias="followersCount")
    is_following: bool = Field(False, alias="isFollowing")
    user: User | None = None
    user_id: str = Field("", alias="userId")
    featured_at: datetime | None = Field(None, alias="featuredAt")
    created_at: datetime | None = Field(None, alias="createdAt")


class CollectionEdge(_BaseModel):
    """Edge for Collection connection."""
    cursor: str
    node: Collection


class CollectionConnection(_BaseModel):
    """Connection for Collection pagination."""
    edges: list[CollectionEdge]
    page_info: PageInfo = Field(alias="pageInfo")
    total_count: int = Field(alias="totalCount")

    @property
    def nodes(self) -> list[Collection]:
        return [edge.node for edge in self.edges]


class Viewer(_BaseModel):
    """The authenticated user's context."""
    user: User


# Mutation payloads
class UserPayload(_BaseModel):
    """Response payload for user mutations."""
    errors: list[Error] = Field(default_factory=list)
    node: User | None = None
