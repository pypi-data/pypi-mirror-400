"""
Telegram Bot API Python Library - Data Classes Module

This module contains all data classes (DTO - Data Transfer Objects) for working with Telegram Bot API.
All classes correspond to the official Telegram Bot API version 9.3 documentation.

Available Classes:
- User: Represents a Telegram user or bot
- Chat: Represents a Telegram chat  
- Message: Represents a Telegram message
- ChatMember: Represents a chat member
- ChatPermissions: Represents chat permissions
- PhotoSize, Photo: Photo representations
- Audio, Voice: Audio representations
- Video, VideoNote: Video representations
- Animation: Animation/GIF representation
- Sticker: Sticker representation
- Document: Document representation
- File: File representation
- Location, Venue: Location and venue representations
- Contact: Contact information
- Dice: Dice throw representation
- WebhookInfo: Webhook information
- InputMedia classes: For sending media
- InlineQuery, InlineQueryResult: Inline query classes
- CallbackQuery: Callback query representation
- ForumTopic: Forum topic representation
- MessageEntity: Message entity/formatting
- Markup: Keyboard creation helper
- BusinessIntro, BusinessLocation, BusinessOpeningHours: Business classes
- Gift, UniqueGift, GiftBackground: Gift-related classes
- And many more...

Usage:
    from telegram_classes import User, Chat, Message
"""

# Import all classes from the main module
from .ekogram import (
    User,
    Chat,
    ChatMember,
    ChatPermissions,
    PhotoSize,
    Photo,
    Audio,
    Voice,
    Video,
    VideoNote,
    Animation,
    Dice,
    Sticker,
    Location,
    Venue,
    Contact,
    Document,
    File,
    WebhookInfo,
    InputFile,
    InputMedia,
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaAnimation,
    InputMediaAudio,
    InputMediaDocument,
    InlineQuery,
    InlineQueryResult,
    InlineQueryResultArticle,
    InlineQueryResultPhoto,
    InlineQueryResultVideo,
    LabeledPrice,
    ShippingOption,
    UserProfilePhotos,
    CallbackQuery,
    ForumTopic,
    MessageEntity,
    Message,
    Markup,
    BusinessIntro,
    BusinessLocation,
    BusinessOpeningHours,
    BusinessMessage,
    Gift,
    UniqueGift,
    UniqueGiftColors,
    GiftBackground,
    UserRating,
    ChecklistTask,
    Bot,
    OnlySQ,
    Deef,
    ChatGPT,
)

__all__ = [
    'User',
    'Chat',
    'ChatMember',
    'ChatPermissions',
    'PhotoSize',
    'Photo',
    'Audio',
    'Voice',
    'Video',
    'VideoNote',
    'Animation',
    'Dice',
    'Sticker',
    'Location',
    'Venue',
    'Contact',
    'Document',
    'File',
    'WebhookInfo',
    'InputFile',
    'InputMedia',
    'InputMediaPhoto',
    'InputMediaVideo',
    'InputMediaAnimation',
    'InputMediaAudio',
    'InputMediaDocument',
    'InlineQuery',
    'InlineQueryResult',
    'InlineQueryResultArticle',
    'InlineQueryResultPhoto',
    'InlineQueryResultVideo',
    'LabeledPrice',
    'ShippingOption',
    'UserProfilePhotos',
    'CallbackQuery',
    'ForumTopic',
    'MessageEntity',
    'Message',
    'Markup',
    'BusinessIntro',
    'BusinessLocation',
    'BusinessOpeningHours',
    'BusinessMessage',
    'Gift',
    'UniqueGift',
    'UniqueGiftColors',
    'GiftBackground',
    'UserRating',
    'ChecklistTask',
    'Bot',
    'OnlySQ',
    'Deef',
    'ChatGPT',
]