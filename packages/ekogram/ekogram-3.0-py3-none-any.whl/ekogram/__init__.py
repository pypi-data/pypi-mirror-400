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
    Message,
    MessageId,
    MessageEntity,
    PhotoSize,
    Photo,
    Animation,
    Audio,
    Document,
    Video,
    VideoNote,
    Voice,
    Contact,
    Dice,
    PollOption,
    Poll,
    Location,
    Venue,
    WebAppInfo,
    ProximityAlertTriggered,
    MessageAutoDeleteTimerChanged,
    ForumTopicCreated,
    ForumTopicClosed,
    ForumTopicReopened,
    ForumTopicDeleted,
    GeneralForumTopicHidden,
    GeneralForumTopicUnhidden,
    UserShared,
    ChatShared,
    WriteAccessAllowed,
    VideoChatScheduled,
    VideoChatStarted,
    VideoChatEnded,
    VideoChatParticipantsInvited,
    MenuButtonCommands,
    MenuButtonWebApp,
    MenuButtonDefault,
    Game,
    CallbackGame,
    ChatAdministratorRights,
    ChatPermissions,
    Birthdate,
    BusinessIntro,
    BusinessOpeningHours,
    BusinessLocation,
    ChatBoost,
    ChatBackground,
    ForumTopic,
    GiftInfo,
    StarsTransaction,
    TransactionPartner,
    WebAppData,
    LabeledPrice,
    Invoice,
    ShippingAddress,
    OrderInfo,
    ShippingQuery,
    ShippingPayment,
    PreCheckoutQuery,
    SuccessfulPayment,
    RefundStarPayment,
    PassportData,
    DatedFile,
    InputMedia,
    InputFile,
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaAnimation,
    InputMediaAudio,
    InputMediaDocument,
    InputSticker,
    LoginUrl,
    SwitchInlineQueryChosenChat,
    ChatPhoto,
    ChatInviteLink,
    ChatMember,
    ChatMemberUpdated,
    ChatJoinRequest,
    BotCommand,
    BotCommandScope,
    InlineQuery,
    InlineQueryResult,
    InlineQueryResultArticle,
    InlineQueryResultPhoto,
    InlineQueryResultGif,
    InlineQueryResultSticker,
    InlineQueryResultVideo,
    InlineQueryResultAudio,
    InlineQueryResultVoice,
    InlineQueryResultDocument,
    InlineQueryResultLocation,
    InlineQueryResultVenue,
    InlineQueryResultContact,
    InlineQueryResultGame,
    InlineQueryResultCachedPhoto,
    InlineQueryResultCachedGif,
    InlineQueryResultCachedSticker,
    InlineQueryResultCachedVideo,
    InlineQueryResultCachedAudio,
    InlineQueryResultCachedVoice,
    InlineQueryResultCachedDocument,
    SentWebAppMessage,
    WebhookInfo,
    Update,
    UserProfilePhotos,
    File,
    ReplyParameters,
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    Sticker,
    ChatMemberOwner,
    ChatMemberAdministrator,
    ChatMemberMember,
    ChatMemberRestricted,
    ChatMemberLeft,
    ChatMemberBanned,
    ShippingOption,
    CallbackQuery,
    UserRating,
    ChecklistTask,
    Gift,
    UniqueGift,
    UniqueGiftColors,
    GiftBackground,
    BusinessMessage,
    Bot,
    OnlySQ,
    Deef,
    ChatGPT,
)

__all__ = [
    # Core classes
    'User',
    'Chat',
    'Message',
    'MessageId',
    'MessageEntity',
    
    # Photo and Media classes
    'PhotoSize',
    'Photo',
    'Animation',
    'Audio',
    'Document',
    'Video',
    'VideoNote',
    'Voice',
    'Sticker',
    
    # Content classes
    'Contact',
    'Dice',
    'Location',
    'Venue',
    
    # Poll classes
    'PollOption',
    'Poll',
    
    # Chat management classes
    'ChatMember',
    'ChatMemberOwner',
    'ChatMemberAdministrator',
    'ChatMemberMember',
    'ChatMemberRestricted',
    'ChatMemberLeft',
    'ChatMemberBanned',
    'ChatMemberUpdated',
    'ChatPermissions',
    'ChatPhoto',
    'ChatInviteLink',
    'ChatJoinRequest',
    'ChatAdministratorRights',
    'ChatBoost',
    'ChatBackground',
    
    # Forum classes
    'ForumTopic',
    'ForumTopicCreated',
    'ForumTopicClosed',
    'ForumTopicReopened',
    'ForumTopicDeleted',
    'GeneralForumTopicHidden',
    'GeneralForumTopicUnhidden',
    
    # Business classes
    'BusinessIntro',
    'BusinessOpeningHours',
    'BusinessLocation',
    'BusinessMessage',
    
    # Gift and Stars classes
    'GiftInfo',
    'Gift',
    'UniqueGift',
    'UniqueGiftColors',
    'GiftBackground',
    'StarsTransaction',
    'TransactionPartner',
    
    # Message-related classes
    'ReplyParameters',
    'ReplyKeyboardRemove',
    'ReplyKeyboardMarkup',
    'InlineKeyboardMarkup',
    
    # Input classes
    'InputFile',
    'InputMedia',
    'InputMediaPhoto',
    'InputMediaVideo',
    'InputMediaAnimation',
    'InputMediaAudio',
    'InputMediaDocument',
    'InputSticker',
    
    # Inline query classes
    'InlineQuery',
    'InlineQueryResult',
    'InlineQueryResultArticle',
    'InlineQueryResultPhoto',
    'InlineQueryResultGif',
    'InlineQueryResultSticker',
    'InlineQueryResultVideo',
    'InlineQueryResultAudio',
    'InlineQueryResultVoice',
    'InlineQueryResultDocument',
    'InlineQueryResultLocation',
    'InlineQueryResultVenue',
    'InlineQueryResultContact',
    'InlineQueryResultGame',
    'InlineQueryResultCachedPhoto',
    'InlineQueryResultCachedGif',
    'InlineQueryResultCachedSticker',
    'InlineQueryResultCachedVideo',
    'InlineQueryResultCachedAudio',
    'InlineQueryResultCachedVoice',
    'InlineQueryResultCachedDocument',
    
    # Payment classes
    'LabeledPrice',
    'ShippingOption',
    'Invoice',
    'ShippingAddress',
    'OrderInfo',
    'ShippingQuery',
    'ShippingPayment',
    'PreCheckoutQuery',
    'SuccessfulPayment',
    'RefundStarPayment',
    
    # Passport classes
    'PassportData',
    'DatedFile',
    
    # Update and Webhook classes
    'Update',
    'WebhookInfo',
    'CallbackQuery',
    
    # File and Profile classes
    'File',
    'UserProfilePhotos',
    
    # Other classes
    'WebAppInfo',
    'ProximityAlertTriggered',
    'MessageAutoDeleteTimerChanged',
    'UserShared',
    'ChatShared',
    'WriteAccessAllowed',
    'VideoChatScheduled',
    'VideoChatStarted',
    'VideoChatEnded',
    'VideoChatParticipantsInvited',
    'Game',
    'CallbackGame',
    'MenuButtonCommands',
    'MenuButtonWebApp',
    'MenuButtonDefault',
    'Birthdate',
    'LoginUrl',
    'SwitchInlineQueryChosenChat',
    'BotCommand',
    'BotCommandScope',
    'SentWebAppMessage',
    'WebAppData',
    'UserRating',
    'ChecklistTask',
    'Bot',
    'OnlySQ',
    'Deef',
    'ChatGPT'
]