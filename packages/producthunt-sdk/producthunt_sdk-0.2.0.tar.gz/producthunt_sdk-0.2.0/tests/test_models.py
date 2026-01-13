"""Tests for Pydantic models."""

from producthunt_sdk.models import (
    Collection,
    CollectionConnection,
    Comment,
    CommentConnection,
    Media,
    PageInfo,
    Post,
    PostConnection,
    Topic,
    TopicConnection,
    User,
    UserConnection,
    Viewer,
    Vote,
    VoteConnection,
)

from .conftest import make_connection


class TestPageInfo:
    def test_parse_page_info(self):
        data = {
            "endCursor": "abc123",
            "hasNextPage": True,
            "hasPreviousPage": False,
            "startCursor": "start",
        }
        page_info = PageInfo.model_validate(data)

        assert page_info.end_cursor == "abc123"
        assert page_info.has_next_page is True

    def test_parse_page_info_null_cursors(self):
        data = {
            "endCursor": None,
            "hasNextPage": False,
            "hasPreviousPage": False,
            "startCursor": None,
        }
        page_info = PageInfo.model_validate(data)
        assert page_info.end_cursor is None


class TestUser:
    def test_parse_user(self, sample_user):
        user = User.model_validate(sample_user)

        assert user.id == "123"
        assert user.username == "testuser"
        assert user.is_maker is True

    def test_parse_user_minimal(self):
        data = {"id": "1", "name": "Test", "username": "test"}
        user = User.model_validate(data)

        assert user.id == "1"
        assert user.headline is None


class TestPost:
    def test_parse_post(self, sample_post):
        post = Post.model_validate(sample_post)

        assert post.id == "456"
        assert post.name == "Test Product"
        assert post.votes_count == 500
        assert post.user is not None

    def test_parse_post_with_makers(self, sample_post):
        post = Post.model_validate(sample_post)

        assert len(post.makers) == 1
        assert post.makers[0].username == "testuser"


class TestTopic:
    def test_parse_topic(self, sample_topic):
        topic = Topic.model_validate(sample_topic)

        assert topic.id == "789"
        assert topic.name == "Artificial Intelligence"
        assert topic.followers_count == 10000


class TestCollection:
    def test_parse_collection(self, sample_collection):
        collection = Collection.model_validate(sample_collection)

        assert collection.id == "col123"
        assert collection.name == "Best AI Tools"
        assert collection.followers_count == 500


class TestComment:
    def test_parse_comment(self, sample_comment):
        comment = Comment.model_validate(sample_comment)

        assert comment.id == "com123"
        assert comment.body == "This is a great product!"
        assert comment.votes_count == 10


class TestMedia:
    def test_parse_image_media(self):
        data = {"type": "image", "url": "https://example.com/image.jpg", "videoUrl": None}
        media = Media.model_validate(data)

        assert media.type == "image"
        assert media.video_url is None

    def test_parse_video_media(self):
        data = {
            "type": "video",
            "url": "https://example.com/thumb.jpg",
            "videoUrl": "https://example.com/video.mp4",
        }
        media = Media.model_validate(data)

        assert media.type == "video"
        assert media.video_url == "https://example.com/video.mp4"


class TestVote:
    def test_parse_vote(self, sample_user):
        data = {
            "id": "vote123",
            "userId": "123",
            "createdAt": "2023-06-15T12:00:00Z",
            "user": sample_user,
        }
        vote = Vote.model_validate(data)

        assert vote.id == "vote123"
        assert vote.user.username == "testuser"


class TestViewer:
    def test_parse_viewer(self, sample_user):
        data = {"user": sample_user}
        viewer = Viewer.model_validate(data)

        assert viewer.user.username == "testuser"


class TestConnections:
    def test_post_connection(self, sample_post):
        data = make_connection([sample_post])
        connection = PostConnection.model_validate(data)

        assert connection.total_count == 1
        assert len(connection.nodes) == 1

    def test_user_connection(self, sample_user):
        data = make_connection([sample_user])
        connection = UserConnection.model_validate(data)

        assert len(connection.nodes) == 1

    def test_topic_connection(self, sample_topic):
        data = make_connection([sample_topic])
        connection = TopicConnection.model_validate(data)

        assert len(connection.nodes) == 1

    def test_collection_connection(self, sample_collection):
        data = make_connection([sample_collection])
        connection = CollectionConnection.model_validate(data)

        assert len(connection.nodes) == 1

    def test_comment_connection(self, sample_comment):
        data = make_connection([sample_comment])
        connection = CommentConnection.model_validate(data)

        assert len(connection.nodes) == 1

    def test_vote_connection(self, sample_user):
        vote_data = {
            "id": "v1",
            "userId": "123",
            "createdAt": "2023-01-01T00:00:00Z",
            "user": sample_user,
        }
        data = make_connection([vote_data])
        connection = VoteConnection.model_validate(data)

        assert len(connection.nodes) == 1

    def test_empty_connection(self):
        data = {
            "edges": [],
            "pageInfo": {
                "endCursor": None,
                "hasNextPage": False,
                "hasPreviousPage": False,
                "startCursor": None,
            },
            "totalCount": 0,
        }
        connection = PostConnection.model_validate(data)

        assert connection.total_count == 0
        assert len(connection.nodes) == 0
