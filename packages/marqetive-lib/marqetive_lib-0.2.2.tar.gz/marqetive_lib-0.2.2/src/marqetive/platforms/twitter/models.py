"""Twitter/X-specific models for post creation and direct messages.

This module defines Twitter-specific data models for creating tweets,
replies, quote tweets, polls, and direct messages.
"""

from pydantic import BaseModel, Field

# ==================== Post Models ====================


class TwitterPostRequest(BaseModel):
    """Twitter/X-specific post creation request.

    Supports tweets, replies, quote tweets, and media attachments.
    Twitter has a 280 character limit for text content.

    Attributes:
        content: Tweet text (max 280 characters)
        media_urls: List of media URLs to attach (max 4 images or 1 video)
        media_ids: List of pre-uploaded media IDs
        reply_to_post_id: Tweet ID to reply to
        quote_post_id: Tweet ID to quote
        poll_options: List of poll options (2-4 options, each max 25 chars)
        poll_duration_minutes: Poll duration in minutes (5-10080)
        alt_texts: Alt text for each media item (for accessibility)

    Example:
        >>> # Simple tweet
        >>> request = TwitterPostRequest(content="Hello Twitter!")

        >>> # Reply to a tweet
        >>> request = TwitterPostRequest(
        ...     content="Great point!",
        ...     reply_to_post_id="1234567890"
        ... )

        >>> # Quote tweet with media
        >>> request = TwitterPostRequest(
        ...     content="Check this out!",
        ...     quote_post_id="1234567890",
        ...     media_urls=["https://example.com/image.jpg"]
        ... )

        >>> # Tweet with poll
        >>> request = TwitterPostRequest(
        ...     content="What's your favorite?",
        ...     poll_options=["Option A", "Option B", "Option C"],
        ...     poll_duration_minutes=1440
        ... )
    """

    content: str | None = None
    media_urls: list[str] = Field(default_factory=list, max_length=4)
    media_ids: list[str] = Field(default_factory=list, max_length=4)
    reply_to_post_id: str | None = None
    quote_post_id: str | None = None
    poll_options: list[str] = Field(default_factory=list, max_length=4)
    poll_duration_minutes: int | None = Field(default=None, ge=5, le=10080)
    alt_texts: list[str] = Field(default_factory=list)


# ==================== Direct Message Models ====================


class TwitterDMRequest(BaseModel):
    """Twitter/X-specific direct message request.

    Supports sending DMs to individuals or existing conversations.
    Twitter has a 10,000 character limit for DM text content.
    Only one media attachment is allowed per DM.

    Attributes:
        text: Message text (max 10,000 characters)
        participant_id: User ID for new 1-to-1 DM (mutually exclusive with conversation_id)
        conversation_id: Existing conversation ID (mutually exclusive with participant_id)
        media_url: URL of media to attach (max 1 attachment)
        media_id: Pre-uploaded media ID (from TwitterMediaManager)

    Example:
        >>> # Send 1-to-1 DM
        >>> request = TwitterDMRequest(
        ...     text="Hello!",
        ...     participant_id="1234567890"
        ... )

        >>> # Send to existing conversation
        >>> request = TwitterDMRequest(
        ...     text="Hello group!",
        ...     conversation_id="dm_conv_123456"
        ... )

        >>> # Send DM with media
        >>> request = TwitterDMRequest(
        ...     text="Check this out!",
        ...     participant_id="1234567890",
        ...     media_url="https://example.com/image.jpg"
        ... )
    """

    text: str = Field(max_length=10000)
    participant_id: str | None = None
    conversation_id: str | None = None
    media_url: str | None = None
    media_id: str | None = None


class TwitterGroupDMRequest(BaseModel):
    """Twitter/X-specific group DM creation request.

    Creates a new group conversation with multiple participants and an initial message.
    Twitter allows 2-49 participants in a group DM (excluding the sender).

    Attributes:
        participant_ids: List of user IDs (2-49 participants, excluding sender)
        text: Initial message text (max 10,000 characters)
        media_url: URL of media to attach
        media_id: Pre-uploaded media ID

    Example:
        >>> request = TwitterGroupDMRequest(
        ...     participant_ids=["user1_id", "user2_id", "user3_id"],
        ...     text="Welcome to the group!"
        ... )
    """

    participant_ids: list[str] = Field(min_length=2, max_length=49)
    text: str = Field(max_length=10000)
    media_url: str | None = None
    media_id: str | None = None
