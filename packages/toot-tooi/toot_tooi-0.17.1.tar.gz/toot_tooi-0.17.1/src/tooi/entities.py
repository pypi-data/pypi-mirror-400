"""
Classes which represent entities returned by the Mastodon API.
"""

from __future__ import annotations

from datetime import date, datetime
from functools import cached_property
from html2text import html2text
from typing import Any, Optional
from pydantic import BaseModel

from tooi.utils.html import get_text


class Account(BaseModel):
    """
    Represents a user of Mastodon and their associated profile.

    https://docs.joinmastodon.org/entities/Account/
    """

    id: str
    username: str
    acct: str
    url: str
    display_name: str
    note: str
    avatar: str
    avatar_static: str
    header: str
    header_static: str
    locked: bool
    fields: list[AccountField]
    emojis: list[CustomEmoji]
    bot: bool
    group: bool
    discoverable: Optional[bool] = None
    noindex: Optional[bool] = None
    moved: Optional[Account] = None
    suspended: Optional[bool] = None
    limited: Optional[bool] = None
    created_at: datetime
    last_status_at: Optional[date] = None
    statuses_count: int
    followers_count: int
    following_count: int

    @cached_property
    def note_md(self) -> str:
        return html2text(self.note, bodywidth=0)


class AccountField(BaseModel):
    """
    https://docs.joinmastodon.org/entities/Account/#Field
    """

    name: str
    value: str
    verified_at: Optional[datetime] = None

    @cached_property
    def value_md(self) -> str:
        return html2text(self.value, bodywidth=0)


class Application(BaseModel):
    """
    Represents an application that interfaces with the REST API, for example to
    access account information or post statuses.

    https://docs.joinmastodon.org/entities/Application/
    """

    id: str
    name: str
    website: str | None = None
    scopes: list[str] | None = None
    redirect_uris: list[str] | None = None


class Context(BaseModel):
    """
    Represents the tree around a given status. Used for reconstructing threads
    of statuses.

    https://docs.joinmastodon.org/entities/Context/
    """

    ancestors: list[Status]
    descendants: list[Status]


class Conversation(BaseModel):
    """
    Represents a conversation with "direct message" visibility.

    https://docs.joinmastodon.org/entities/Conversation/
    """

    id: str
    unread: bool
    accounts: list[Account]
    last_status: Optional[Status] = None


class CredentialApplication(BaseModel):
    """
    https://docs.joinmastodon.org/entities/Application/#CredentialApplication
    """

    id: str
    name: str
    client_id: str
    client_secret: str
    client_secret_expires_at: int
    website: str | None = None
    scopes: list[str] | None = None
    redirect_uris: list[str] | None = None


class CustomEmoji(BaseModel):
    """
    https://docs.joinmastodon.org/entities/CustomEmoji/
    """

    shortcode: str
    url: str
    static_url: str
    visible_in_picker: bool
    category: Optional[str] = None


class ExtendedDescription(BaseModel):
    """
    https://docs.joinmastodon.org/entities/ExtendedDescription/
    """

    updated_at: Optional[datetime] = None
    content: str

    @cached_property
    def content_md(self) -> str:
        return html2text(self.content, bodywidth=0)


class Filter(BaseModel):
    """
    https://docs.joinmastodon.org/entities/Filter/
    """

    id: str
    title: str
    context: list[str]
    expires_at: Optional[datetime] = None
    filter_action: str
    keywords: Optional[list[FilterKeyword]] = None
    statuses: Optional[list[FilterStatus]] = None


class FilterKeyword(BaseModel):
    """
    https://docs.joinmastodon.org/entities/FilterKeyword/
    """

    id: str
    keyword: str
    whole_word: bool


class FilterResult(BaseModel):
    """
    https://docs.joinmastodon.org/entities/FilterResult/
    """

    filter: Filter
    keyword_matches: Optional[list[str]] = None
    status_matches: Optional[str] = None


class FilterStatus(BaseModel):
    """
    https://docs.joinmastodon.org/entities/FilterStatus/
    """

    id: str
    status_id: str


class MediaAttachment(BaseModel):
    """
    https://docs.joinmastodon.org/entities/MediaAttachment/
    """

    id: str
    type: str
    url: str
    preview_url: str
    remote_url: Optional[str] = None
    meta: Optional[dict[str, Any]] = None
    description: Optional[str] = None
    blurhash: Optional[str] = None

    @property
    def aspect_ratio(self) -> float | None:
        if self.meta:
            return self.meta.get("original", {}).get("aspect")


class Notification(BaseModel):
    """
    https://docs.joinmastodon.org/entities/Notification/
    """

    id: str
    type: str
    created_at: datetime
    account: Account
    status: Optional[Status] = None
    report: Optional[Report] = None


class PollOption(BaseModel):
    """
    https://docs.joinmastodon.org/entities/Poll/#Option
    """

    title: str
    votes_count: Optional[int] = None


class Poll(BaseModel):
    """
    https://docs.joinmastodon.org/entities/Poll/
    """

    id: str
    expires_at: Optional[datetime] = None
    expired: bool
    multiple: bool
    votes_count: int
    voters_count: Optional[int] = None
    options: list[PollOption]
    emojis: list[CustomEmoji]
    voted: Optional[bool] = None
    own_votes: Optional[list[int]] = None


class PreviewCard(BaseModel):
    """
    https://docs.joinmastodon.org/entities/PreviewCard/
    """

    url: str
    title: str
    description: str
    type: str
    author_name: str
    author_url: str
    provider_name: str
    provider_url: str
    html: str
    width: int
    height: int
    image: Optional[str] = None
    embed_url: str
    blurhash: Optional[str] = None

    @cached_property
    def markdown(self) -> str:
        return html2text(self.html, bodywidth=0)


class Relationship(BaseModel):
    """
    Represents the relationship between accounts.
    https://docs.joinmastodon.org/entities/Relationship/
    """

    id: str
    following: bool
    showing_reblogs: bool
    notifying: bool
    followed_by: bool
    blocking: bool
    blocked_by: bool
    muting: bool
    muting_notifications: bool
    requested: bool
    requested_by: bool
    domain_blocking: bool
    endorsed: bool
    note: str


class Report(BaseModel):
    """
    https://docs.joinmastodon.org/entities/Report/
    """

    id: str
    action_taken: bool
    action_taken_at: Optional[datetime] = None
    category: str
    comment: str
    forwarded: bool
    created_at: datetime
    status_ids: Optional[list[str]] = None
    rule_ids: Optional[list[str]] = None
    target_account: Account


class Rule(BaseModel):
    """
    https://docs.joinmastodon.org/entities/Rule/
    """

    id: str
    text: str


class Search(BaseModel):
    """
    https://docs.joinmastodon.org/entities/Search/
    """

    accounts: list[Account]
    hashtags: list[Tag]
    statuses: list[Status]


class Status(BaseModel):
    """
    https://docs.joinmastodon.org/entities/Status/
    """

    id: str
    uri: str
    created_at: datetime
    account: Account
    content: str
    visibility: str
    sensitive: bool
    spoiler_text: str
    media_attachments: list[MediaAttachment]
    application: Optional[StatusApplication] = None
    mentions: list[StatusMention]
    tags: list[StatusTag]
    emojis: list[CustomEmoji]
    reblogs_count: int
    favourites_count: int
    replies_count: int
    url: Optional[str] = None
    in_reply_to_id: Optional[str] = None
    in_reply_to_account_id: Optional[str] = None
    reblog: Optional[Status] = None
    poll: Optional[Poll] = None
    card: Optional[PreviewCard] = None
    language: Optional[str] = None
    text: Optional[str] = None
    edited_at: Optional[datetime] = None
    favourited: Optional[bool] = None
    reblogged: Optional[bool] = None
    muted: Optional[bool] = None
    bookmarked: Optional[bool] = None
    pinned: Optional[bool] = None
    filtered: Optional[list[FilterResult]] = None
    # Hometown unfederated posts
    local_only: Optional[bool] = None

    @property
    def original(self) -> "Status":
        return self.reblog or self

    @cached_property
    def content_md(self) -> str:
        return html2text(self.content, bodywidth=0)

    @cached_property
    def content_plaintext(self) -> str:
        return get_text(self.content)


class StatusApplication(BaseModel):
    """
    https://docs.joinmastodon.org/entities/Status/#application
    """

    name: str
    website: Optional[str] = None


class StatusMention(BaseModel):
    """
    https://docs.joinmastodon.org/entities/Status/#Mention
    """

    id: str
    username: str
    url: str
    acct: str


class StatusTag(BaseModel):
    """
    https://docs.joinmastodon.org/entities/Status/#Tag
    """

    name: str
    url: str


class StatusSource(BaseModel):
    """
    https://docs.joinmastodon.org/entities/StatusSource/
    """

    id: str
    text: str
    spoiler_text: str


class Instance(BaseModel):
    """
    https://docs.joinmastodon.org/entities/V1_Instance/
    """

    uri: str
    title: str
    short_description: str
    description: str
    email: str
    version: str
    urls: InstanceUrls
    stats: InstanceStats
    thumbnail: Optional[str] = None
    languages: list[str]
    registrations: bool
    approval_required: bool
    invites_enabled: bool
    configuration: InstanceConfiguration
    contact_account: Optional[Account] = None
    rules: list[Rule]


class InstanceConfiguration(BaseModel):
    """
    https://docs.joinmastodon.org/entities/V1_Instance/#configuration
    """

    statuses: InstanceConfigurationStatuses
    media_attachments: InstanceConfigurationMediaAttachment
    polls: InstancePollConfiguration


class InstanceConfigurationStatuses(BaseModel):
    """
    https://docs.joinmastodon.org/entities/Instance/#statuses
    """

    max_characters: int
    max_media_attachments: int
    characters_reserved_per_url: int


class InstanceConfigurationMediaAttachment(BaseModel):
    supported_mime_types: list[str]
    image_size_limit: int
    image_matrix_limit: int
    video_size_limit: int
    video_frame_rate_limit: int
    video_matrix_limit: int


class InstancePollConfiguration(BaseModel):
    max_options: int
    max_characters_per_option: int
    min_expiration: int
    max_expiration: int


class InstanceStats(BaseModel):
    """
    https://docs.joinmastodon.org/entities/V1_Instance/#stats
    """

    user_count: int
    status_count: int
    domain_count: int


class InstanceUrls(BaseModel):
    """
    https://docs.joinmastodon.org/entities/V1_Instance/#urls
    """

    streaming_api: str


class InstanceV2(BaseModel):
    """
    https://docs.joinmastodon.org/entities/Instance/
    """

    domain: str
    title: str
    version: str
    source_url: str
    description: str
    usage: InstanceV2Usage
    thumbnail: InstanceV2Thumbnail
    languages: list[str]
    configuration: InstanceV2Configuration
    registrations: InstanceV2Registrations
    contact: InstanceV2Contact
    rules: list[Rule]


class InstanceV2Configuration(BaseModel):
    """
    https://docs.joinmastodon.org/entities/Instance/#configuration
    """

    urls: InstanceV2ConfigurationUrls
    statuses: InstanceV2ConfigurationStatuses
    media_attachments: InstanceV2ConfigurationMediaAttachment
    polls: InstancePollConfiguration


class InstanceV2ConfigurationMediaAttachment(BaseModel):
    """
    https://docs.joinmastodon.org/entities/Instance/#media_attachments
    """

    supported_mime_types: list[str]
    image_size_limit: int
    image_matrix_limit: int
    video_size_limit: int
    video_frame_rate_limit: int
    video_matrix_limit: int


class InstanceV2ConfigurationStatuses(BaseModel):
    """
    https://docs.joinmastodon.org/entities/Instance/#statuses
    """

    max_characters: int
    max_media_attachments: int
    characters_reserved_per_url: int


class InstanceV2ConfigurationUrls(BaseModel):
    """
    https://docs.joinmastodon.org/entities/Instance/#urls
    """

    streaming: str


class InstanceV2Contact(BaseModel):
    """
    https://docs.joinmastodon.org/entities/Instance/#contact
    """

    email: str
    account: Optional[Account] = None


class InstanceV2Registrations(BaseModel):
    """
    https://docs.joinmastodon.org/entities/V1_Instance/#registrations
    """

    enabled: bool
    approval_required: bool
    message: Optional[str] = None


class InstanceV2Usage(BaseModel):
    """
    https://docs.joinmastodon.org/entities/Instance/#usage
    """

    users: InstanceV2UsageUsers


class InstanceV2UsageUsers(BaseModel):
    """
    https://docs.joinmastodon.org/entities/Instance/#users
    """

    active_month: int


class InstanceV2Thumbnail(BaseModel):
    """
    https://docs.joinmastodon.org/entities/Instance/#thumbnail
    """

    url: str
    blurhash: Optional[str] = None
    versions: Optional[dict[str, Any]] = None


class TagHistory(BaseModel):
    """
    Usage statistics for given days (typically the past week).
    https://docs.joinmastodon.org/entities/Tag/#history
    """

    day: str
    uses: str
    accounts: str


class Tag(BaseModel):
    """
    Represents a hashtag used within the content of a status.
    https://docs.joinmastodon.org/entities/Tag/
    """

    name: str
    url: str
    history: list[TagHistory]
    following: Optional[bool] = None


class Token(BaseModel):
    """
    Represents an OAuth token used for authenticating with the API and
    performing actions.
    https://docs.joinmastodon.org/entities/Token/
    """

    access_token: str
    token_type: str
    scope: str
    created_at: int


class Translation(BaseModel):
    """
    Represents the result of machine translating some status content
    https://docs.joinmastodon.org/entities/Translation/
    """

    content: str
    spoiler_text: str
    language: str
    poll: TranslationPoll | None
    media_attachments: list[TranslationAttachment]
    detected_source_language: str
    provider: str


class TranslationAttachment(BaseModel):
    """
    https://docs.joinmastodon.org/entities/Translation/#Attachment
    """

    id: str
    description: str


class TranslationPoll(BaseModel):
    """
    https://docs.joinmastodon.org/entities/Translation/#Poll
    """

    id: str
    options: list[TranslationPollOption]


class TranslationPollOption(BaseModel):
    """
    https://docs.joinmastodon.org/entities/Translation/#Option
    """

    title: str
