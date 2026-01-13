"""GraphQL queries and mutations for Product Hunt API."""

# Fragments
USER_FRAGMENT = """
fragment UserFields on User {
    id
    name
    username
    headline
    profileImage
    twitterUsername
    websiteUrl
    url
    isFollowing
    isMaker
    isViewer
    createdAt
}
"""

TOPIC_FRAGMENT = """
fragment TopicFields on Topic {
    id
    name
    slug
    description
    followersCount
    postsCount
    image
    url
    isFollowing
    createdAt
}
"""

MEDIA_FRAGMENT = """
fragment MediaFields on Media {
    type
    url
    videoUrl
}
"""

POST_FRAGMENT = (
    """
fragment PostFields on Post {
    id
    name
    slug
    tagline
    description
    url
    website
    votesCount
    commentsCount
    reviewsRating
    isVoted
    isCollected
    featuredAt
    createdAt
    thumbnail {
        ...MediaFields
    }
    user {
        ...UserFields
    }
    makers {
        ...UserFields
    }
}
"""
    + MEDIA_FRAGMENT
    + USER_FRAGMENT
)

POST_DETAIL_FRAGMENT = (
    """
fragment PostDetailFields on Post {
    id
    name
    slug
    tagline
    description
    url
    website
    votesCount
    commentsCount
    reviewsRating
    isVoted
    isCollected
    featuredAt
    createdAt
    thumbnail {
        ...MediaFields
    }
    media {
        ...MediaFields
    }
    user {
        ...UserFields
    }
    makers {
        ...UserFields
    }
}
"""
    + MEDIA_FRAGMENT
    + USER_FRAGMENT
)

COMMENT_FRAGMENT = (
    """
fragment CommentFields on Comment {
    id
    body
    url
    votesCount
    isVoted
    userId
    parentId
    createdAt
    user {
        ...UserFields
    }
}
"""
    + USER_FRAGMENT
)

COLLECTION_FRAGMENT = (
    """
fragment CollectionFields on Collection {
    id
    name
    tagline
    description
    coverImage
    url
    followersCount
    isFollowing
    userId
    featuredAt
    createdAt
    user {
        ...UserFields
    }
}
"""
    + USER_FRAGMENT
)

PAGE_INFO_FRAGMENT = """
fragment PageInfoFields on PageInfo {
    endCursor
    hasNextPage
    hasPreviousPage
    startCursor
}
"""

# Queries
GET_POST = (
    """
query GetPost($id: ID, $slug: String) {
    post(id: $id, slug: $slug) {
        ...PostDetailFields
    }
}
"""
    + POST_DETAIL_FRAGMENT
)

GET_POSTS = (
    """
query GetPosts(
    $first: Int,
    $after: String,
    $last: Int,
    $before: String,
    $featured: Boolean,
    $order: PostsOrder,
    $postedAfter: DateTime,
    $postedBefore: DateTime,
    $topic: String,
    $twitterUrl: String
) {
    posts(
        first: $first,
        after: $after,
        last: $last,
        before: $before,
        featured: $featured,
        order: $order,
        postedAfter: $postedAfter,
        postedBefore: $postedBefore,
        topic: $topic,
        twitterUrl: $twitterUrl
    ) {
        edges {
            cursor
            node {
                ...PostFields
            }
        }
        pageInfo {
            ...PageInfoFields
        }
        totalCount
    }
}
"""
    + POST_FRAGMENT
    + PAGE_INFO_FRAGMENT
)

GET_POST_COMMENTS = (
    """
query GetPostComments(
    $postId: ID,
    $postSlug: String,
    $first: Int,
    $after: String,
    $order: CommentsOrder
) {
    post(id: $postId, slug: $postSlug) {
        comments(first: $first, after: $after, order: $order) {
            edges {
                cursor
                node {
                    ...CommentFields
                }
            }
            pageInfo {
                ...PageInfoFields
            }
            totalCount
        }
    }
}
"""
    + COMMENT_FRAGMENT
    + PAGE_INFO_FRAGMENT
)

GET_POST_VOTES = (
    """
query GetPostVotes(
    $postId: ID,
    $postSlug: String,
    $first: Int,
    $after: String,
    $createdAfter: DateTime,
    $createdBefore: DateTime
) {
    post(id: $postId, slug: $postSlug) {
        votes(
            first: $first,
            after: $after,
            createdAfter: $createdAfter,
            createdBefore: $createdBefore
        ) {
            edges {
                cursor
                node {
                    id
                    userId
                    createdAt
                    user {
                        ...UserFields
                    }
                }
            }
            pageInfo {
                ...PageInfoFields
            }
            totalCount
        }
    }
}
"""
    + USER_FRAGMENT
    + PAGE_INFO_FRAGMENT
)

GET_USER = (
    """
query GetUser($id: ID, $username: String) {
    user(id: $id, username: $username) {
        ...UserFields
    }
}
"""
    + USER_FRAGMENT
)

GET_USER_POSTS = (
    """
query GetUserPosts(
    $userId: ID,
    $username: String,
    $first: Int,
    $after: String
) {
    user(id: $userId, username: $username) {
        madePosts(first: $first, after: $after) {
            edges {
                cursor
                node {
                    ...PostFields
                }
            }
            pageInfo {
                ...PageInfoFields
            }
            totalCount
        }
    }
}
"""
    + POST_FRAGMENT
    + PAGE_INFO_FRAGMENT
)

GET_USER_VOTED_POSTS = (
    """
query GetUserVotedPosts(
    $userId: ID,
    $username: String,
    $first: Int,
    $after: String
) {
    user(id: $userId, username: $username) {
        votedPosts(first: $first, after: $after) {
            edges {
                cursor
                node {
                    ...PostFields
                }
            }
            pageInfo {
                ...PageInfoFields
            }
            totalCount
        }
    }
}
"""
    + POST_FRAGMENT
    + PAGE_INFO_FRAGMENT
)

GET_USER_FOLLOWERS = (
    """
query GetUserFollowers(
    $userId: ID,
    $username: String,
    $first: Int,
    $after: String
) {
    user(id: $userId, username: $username) {
        followers(first: $first, after: $after) {
            edges {
                cursor
                node {
                    ...UserFields
                }
            }
            pageInfo {
                ...PageInfoFields
            }
            totalCount
        }
    }
}
"""
    + USER_FRAGMENT
    + PAGE_INFO_FRAGMENT
)

GET_USER_FOLLOWING = (
    """
query GetUserFollowing(
    $userId: ID,
    $username: String,
    $first: Int,
    $after: String
) {
    user(id: $userId, username: $username) {
        following(first: $first, after: $after) {
            edges {
                cursor
                node {
                    ...UserFields
                }
            }
            pageInfo {
                ...PageInfoFields
            }
            totalCount
        }
    }
}
"""
    + USER_FRAGMENT
    + PAGE_INFO_FRAGMENT
)

GET_COLLECTION = (
    """
query GetCollection($id: ID, $slug: String) {
    collection(id: $id, slug: $slug) {
        ...CollectionFields
    }
}
"""
    + COLLECTION_FRAGMENT
)

GET_COLLECTIONS = (
    """
query GetCollections(
    $first: Int,
    $after: String,
    $featured: Boolean,
    $order: CollectionsOrder,
    $postId: ID,
    $userId: ID
) {
    collections(
        first: $first,
        after: $after,
        featured: $featured,
        order: $order,
        postId: $postId,
        userId: $userId
    ) {
        edges {
            cursor
            node {
                ...CollectionFields
            }
        }
        pageInfo {
            ...PageInfoFields
        }
        totalCount
    }
}
"""
    + COLLECTION_FRAGMENT
    + PAGE_INFO_FRAGMENT
)

GET_COLLECTION_POSTS = (
    """
query GetCollectionPosts(
    $collectionId: ID,
    $collectionSlug: String,
    $first: Int,
    $after: String
) {
    collection(id: $collectionId, slug: $collectionSlug) {
        posts(first: $first, after: $after) {
            edges {
                cursor
                node {
                    ...PostFields
                }
            }
            pageInfo {
                ...PageInfoFields
            }
            totalCount
        }
    }
}
"""
    + POST_FRAGMENT
    + PAGE_INFO_FRAGMENT
)

GET_TOPIC = (
    """
query GetTopic($id: ID, $slug: String) {
    topic(id: $id, slug: $slug) {
        ...TopicFields
    }
}
"""
    + TOPIC_FRAGMENT
)

GET_TOPICS = (
    """
query GetTopics(
    $first: Int,
    $after: String,
    $order: TopicsOrder,
    $query: String,
    $followedByUserid: ID
) {
    topics(
        first: $first,
        after: $after,
        order: $order,
        query: $query,
        followedByUserid: $followedByUserid
    ) {
        edges {
            cursor
            node {
                ...TopicFields
            }
        }
        pageInfo {
            ...PageInfoFields
        }
        totalCount
    }
}
"""
    + TOPIC_FRAGMENT
    + PAGE_INFO_FRAGMENT
)

GET_COMMENT = (
    """
query GetComment($id: ID!) {
    comment(id: $id) {
        ...CommentFields
    }
}
"""
    + COMMENT_FRAGMENT
)

GET_VIEWER = (
    """
query GetViewer {
    viewer {
        user {
            ...UserFields
        }
    }
}
"""
    + USER_FRAGMENT
)

# Mutations
USER_FOLLOW = (
    """
mutation UserFollow($input: UserFollowInput!) {
    userFollow(input: $input) {
        errors {
            field
            message
        }
        node {
            ...UserFields
        }
    }
}
"""
    + USER_FRAGMENT
)

USER_FOLLOW_UNDO = (
    """
mutation UserFollowUndo($input: UserFollowUndoInput!) {
    userFollowUndo(input: $input) {
        errors {
            field
            message
        }
        node {
            ...UserFields
        }
    }
}
"""
    + USER_FRAGMENT
)
