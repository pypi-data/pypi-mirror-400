import requests, json, os, time, re, bs4, random, string, base64, threading
from typing import Optional, Union, BinaryIO


class User:
    """Класс для представления пользователя Telegram"""
    def __init__(self, user_id: int, is_bot: bool = False, first_name: str = None, last_name: str = None,
                 username: str = None, language_code: str = None, is_premium: bool = None,
                 added_to_attachment_menu: bool = None, can_join_groups: bool = None,
                 can_read_all_group_messages: bool = None, supports_inline_queries: bool = None,
                 can_connect_to_business: bool = None, has_main_web_app: bool = None,
                 has_topics_enabled: bool = None):
        self.id = user_id
        self.is_bot = is_bot
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.language_code = language_code
        self.is_premium = is_premium
        self.added_to_attachment_menu = added_to_attachment_menu
        self.can_join_groups = can_join_groups
        self.can_read_all_group_messages = can_read_all_group_messages
        self.supports_inline_queries = supports_inline_queries
        self.can_connect_to_business = can_connect_to_business
        self.has_main_web_app = has_main_web_app
        self.has_topics_enabled = has_topics_enabled

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        return cls(
            user_id=data['id'],
            is_bot=data.get('is_bot', False),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            username=data.get('username'),
            language_code=data.get('language_code'),
            is_premium=data.get('is_premium'),
            added_to_attachment_menu=data.get('added_to_attachment_menu'),
            can_join_groups=data.get('can_join_groups'),
            can_read_all_group_messages=data.get('can_read_all_group_messages'),
            supports_inline_queries=data.get('supports_inline_queries'),
            can_connect_to_business=data.get('can_connect_to_business'),
            has_main_web_app=data.get('has_main_web_app'),
            has_topics_enabled=data.get('has_topics_enabled'))

    def __repr__(self) -> str:
        return (f"User(id={self.id}, is_bot={self.is_bot}, first_name={self.first_name}, "
                f"username={self.username}, has_topics_enabled={self.has_topics_enabled})")


class Chat:
    """Класс для представления чата"""
    def __init__(self, chat_id: Union[int, str], chat_type: str, title: str = None, username: str = None,
                 first_name: str = None, last_name: str = None, is_forum: bool = None, 
                 is_direct_messages: bool = None, photo: dict = None, active_usernames: list[str] = None, 
                 emoji_status_custom_emoji_id: str = None, bio: str = None, has_private_forum_tags: bool = None,
                 has_aggressive_anti_spam_enabled: bool = None, has_hidden_members: bool = None, 
                 join_to_send_messages: bool = None, join_by_request: bool = None, description: str = None, 
                 invite_link: str = None, pinned_message: dict = None, permissions: dict = None, 
                 slow_mode_delay: int = None, message_auto_delete_time: int = None,
                 has_protected_content: bool = None, sticker_set_name: str = None, 
                 can_set_sticker_set: bool = None, linked_chat_id: int = None, location: dict = None):
        self.id = chat_id
        self.type = chat_type
        self.title = title
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.is_forum = is_forum
        self.is_direct_messages = is_direct_messages
        self.photo = photo
        self.active_usernames = active_usernames
        self.emoji_status_custom_emoji_id = emoji_status_custom_emoji_id
        self.bio = bio
        self.has_private_forum_tags = has_private_forum_tags
        self.has_aggressive_anti_spam_enabled = has_aggressive_anti_spam_enabled
        self.has_hidden_members = has_hidden_members
        self.join_to_send_messages = join_to_send_messages
        self.join_by_request = join_by_request
        self.description = description
        self.invite_link = invite_link
        self.pinned_message = pinned_message
        self.permissions = permissions
        self.slow_mode_delay = slow_mode_delay
        self.message_auto_delete_time = message_auto_delete_time
        self.has_protected_content = has_protected_content
        self.sticker_set_name = sticker_set_name
        self.can_set_sticker_set = can_set_sticker_set
        self.linked_chat_id = linked_chat_id
        self.location = location

    @classmethod
    def from_dict(cls, data: dict) -> 'Chat':
        return cls(
            chat_id=data['id'],
            chat_type=data['type'],
            title=data.get('title'),
            username=data.get('username'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            is_forum=data.get('is_forum'),
            is_direct_messages=data.get('is_direct_messages'),
            photo=data.get('photo'),
            active_usernames=data.get('active_usernames'),
            emoji_status_custom_emoji_id=data.get('emoji_status_custom_emoji_id'),
            bio=data.get('bio'),
            has_private_forum_tags=data.get('has_private_forum_tags'),
            has_aggressive_anti_spam_enabled=data.get('has_aggressive_anti_spam_enabled'),
            has_hidden_members=data.get('has_hidden_members'),
            join_to_send_messages=data.get('join_to_send_messages'),
            join_by_request=data.get('join_by_request'),
            description=data.get('description'),
            invite_link=data.get('invite_link'),
            pinned_message=data.get('pinned_message'),
            permissions=data.get('permissions'),
            slow_mode_delay=data.get('slow_mode_delay'),
            message_auto_delete_time=data.get('message_auto_delete_time'),
            has_protected_content=data.get('has_protected_content'),
            sticker_set_name=data.get('sticker_set_name'),
            can_set_sticker_set=data.get('can_set_sticker_set'),
            linked_chat_id=data.get('linked_chat_id'),
            location=data.get('location'))

    def __repr__(self) -> str:
        return f"Chat(id={self.id}, type={self.type}, title={self.title})"


class ChatMember:
    """Класс для представления участника чата"""
    def __init__(self, user: 'User', status: str, **kwargs: dict):
        self.user = user
        self.status = status
        # Поля для всех типов участников
        self.is_anonymous = kwargs.get('is_anonymous', None)
        self.custom_title = kwargs.get('custom_title', None)
        # Поля для администратора
        self.can_be_edited = kwargs.get('can_be_edited', None)
        self.can_manage_chat = kwargs.get('can_manage_chat', None)
        self.can_delete_messages = kwargs.get('can_delete_messages', None)
        self.can_manage_video_chats = kwargs.get('can_manage_video_chats', None)
        self.can_manage_topics = kwargs.get('can_manage_topics', None)
        self.can_restrict_members = kwargs.get('can_restrict_members', None)
        self.can_promote_members = kwargs.get('can_promote_members', None)
        self.can_change_info = kwargs.get('can_change_info', None)
        self.can_invite_users = kwargs.get('can_invite_users', None)
        self.can_pin_messages = kwargs.get('can_pin_messages', None)
        self.can_post_stories = kwargs.get('can_post_stories', None)
        self.can_edit_stories = kwargs.get('can_edit_stories', None)
        self.can_delete_stories = kwargs.get('can_delete_stories', None)
        # Поля для ограниченного участника
        self.is_member = kwargs.get('is_member', None)
        self.until_date = kwargs.get('until_date', None)
        self.can_send_messages = kwargs.get('can_send_messages', None)
        self.can_send_media_messages = kwargs.get('can_send_media_messages', None)
        self.can_send_polls = kwargs.get('can_send_polls', None)
        self.can_send_other_messages = kwargs.get('can_send_other_messages', None)
        self.can_add_web_page_previews = kwargs.get('can_add_web_page_previews', None)
        self.can_use_stories = kwargs.get('can_use_stories', None)
        self.can_manage_anti_spam = kwargs.get('can_manage_anti_spam', None)

    @classmethod
    def from_dict(cls, data: dict) -> 'ChatMember':
        user = User.from_dict(data['user'])
        status = data.get('status')
        
        common_kwargs = {
            'is_anonymous': data.get('is_anonymous'),
            'custom_title': data.get('custom_title'),
        }
        
        if status == 'creator':
            return cls(user=user, status=status, **common_kwargs)
        elif status == 'administrator':
            admin_kwargs = {
                **common_kwargs,
                'can_be_edited': data.get('can_be_edited'),
                'can_manage_chat': data.get('can_manage_chat'),
                'can_delete_messages': data.get('can_delete_messages'),
                'can_manage_video_chats': data.get('can_manage_video_chats'),
                'can_manage_topics': data.get('can_manage_topics'),
                'can_restrict_members': data.get('can_restrict_members'),
                'can_promote_members': data.get('can_promote_members'),
                'can_change_info': data.get('can_change_info'),
                'can_invite_users': data.get('can_invite_users'),
                'can_pin_messages': data.get('can_pin_messages'),
                'can_post_stories': data.get('can_post_stories'),
                'can_edit_stories': data.get('can_edit_stories'),
                'can_delete_stories': data.get('can_delete_stories'),
            }
            return cls(user=user, status=status, **admin_kwargs)
        elif status == 'restricted':
            restricted_kwargs = {
                'is_member': data.get('is_member'),
                'until_date': data.get('until_date'),
                'can_send_messages': data.get('can_send_messages'),
                'can_send_media_messages': data.get('can_send_media_messages'),
                'can_send_polls': data.get('can_send_polls'),
                'can_send_other_messages': data.get('can_send_other_messages'),
                'can_add_web_page_previews': data.get('can_add_web_page_previews'),
                'can_use_stories': data.get('can_use_stories'),
                'can_manage_anti_spam': data.get('can_manage_anti_spam'),
            }
            return cls(user=user, status=status, **restricted_kwargs)
        elif status in ['kicked', 'banned']:
            return cls(user=user, status=status, until_date=data.get('until_date'))
        elif status in ['left', 'member']:
            return cls(user=user, status=status)
        else:
            return cls(user=user, status=status)

    def __repr__(self) -> str:
        return f"<ChatMember {self.user.first_name if self.user else 'Unknown'}, status: {self.status}>"


class ChatPermissions:
    """Класс для управления правами участников чата"""
    def __init__(self, can_send_messages: bool = None, can_send_media_messages: bool = None,
                 can_send_polls: bool = None, can_send_other_messages: bool = None,
                 can_add_web_page_previews: bool = None, can_change_info: bool = None,
                 can_invite_users: bool = None, can_pin_messages: bool = None,
                 can_manage_topics: bool = None, can_send_audios: bool = None,
                 can_send_documents: bool = None, can_send_photos: bool = None,
                 can_send_videos: bool = None, can_send_video_notes: bool = None,
                 can_send_voice_notes: bool = None, can_use_stories: bool = None,
                 can_post_stories: bool = None, can_edit_stories: bool = None,
                 can_delete_stories: bool = None, can_manage_anti_spam: bool = None):
        self.can_send_messages = can_send_messages
        self.can_send_media_messages = can_send_media_messages
        self.can_send_polls = can_send_polls
        self.can_send_other_messages = can_send_other_messages
        self.can_add_web_page_previews = can_add_web_page_previews
        self.can_change_info = can_change_info
        self.can_invite_users = can_invite_users
        self.can_pin_messages = can_pin_messages
        self.can_manage_topics = can_manage_topics
        self.can_send_audios = can_send_audios
        self.can_send_documents = can_send_documents
        self.can_send_photos = can_send_photos
        self.can_send_videos = can_send_videos
        self.can_send_video_notes = can_send_video_notes
        self.can_send_voice_notes = can_send_voice_notes
        self.can_use_stories = can_use_stories
        self.can_post_stories = can_post_stories
        self.can_edit_stories = can_edit_stories
        self.can_delete_stories = can_delete_stories
        self.can_manage_anti_spam = can_manage_anti_spam

    def to_dict(self) -> dict:
        return {k: v for k, v in {
            'can_send_messages': self.can_send_messages,
            'can_send_media_messages': self.can_send_media_messages,
            'can_send_polls': self.can_send_polls,
            'can_send_other_messages': self.can_send_other_messages,
            'can_add_web_page_previews': self.can_add_web_page_previews,
            'can_change_info': self.can_change_info,
            'can_invite_users': self.can_invite_users,
            'can_pin_messages': self.can_pin_messages,
            'can_manage_topics': self.can_manage_topics,
            'can_send_audios': self.can_send_audios,
            'can_send_documents': self.can_send_documents,
            'can_send_photos': self.can_send_photos,
            'can_send_videos': self.can_send_videos,
            'can_send_video_notes': self.can_send_video_notes,
            'can_send_voice_notes': self.can_send_voice_notes,
            'can_use_stories': self.can_use_stories,
            'can_post_stories': self.can_post_stories,
            'can_edit_stories': self.can_edit_stories,
            'can_delete_stories': self.can_delete_stories,
            'can_manage_anti_spam': self.can_manage_anti_spam,
        }.items() if v is not None}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            can_send_messages=data.get('can_send_messages'),
            can_send_media_messages=data.get('can_send_media_messages'),
            can_send_polls=data.get('can_send_polls'),
            can_send_other_messages=data.get('can_send_other_messages'),
            can_add_web_page_previews=data.get('can_add_web_page_previews'),
            can_change_info=data.get('can_change_info'),
            can_invite_users=data.get('can_invite_users'),
            can_pin_messages=data.get('can_pin_messages'),
            can_manage_topics=data.get('can_manage_topics'),
            can_send_audios=data.get('can_send_audios'),
            can_send_documents=data.get('can_send_documents'),
            can_send_photos=data.get('can_send_photos'),
            can_send_videos=data.get('can_send_videos'),
            can_send_video_notes=data.get('can_send_video_notes'),
            can_send_voice_notes=data.get('can_send_voice_notes'),
            can_use_stories=data.get('can_use_stories'),
            can_post_stories=data.get('can_post_stories'),
            can_edit_stories=data.get('can_edit_stories'),
            can_delete_stories=data.get('can_delete_stories'),
            can_manage_anti_spam=data.get('can_manage_anti_spam'))

    def __repr__(self):
        return f'<ChatPermissions {self.to_dict()}>'


class PhotoSize:
    """Класс для представления размера фотографии"""
    def __init__(self, file_id: str, file_unique_id: str, width: int, height: int, 
                 file_size: int = None, thumbnail: dict = None):
        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.width = width
        self.height = height
        self.file_size = file_size
        self.thumbnail = PhotoSize.from_dict(thumbnail) if thumbnail else None

    @classmethod
    def from_dict(cls, data: dict) -> 'PhotoSize':
        return cls(
            file_id=data['file_id'],
            file_unique_id=data['file_unique_id'],
            width=data['width'],
            height=data['height'],
            file_size=data.get('file_size'),
            thumbnail=data.get('thumbnail'))


class Photo:
    """Класс для представления фотографии"""
    def __init__(self, file_id: str, file_unique_id: str, width: int, height: int,
                 file_size: int = None, thumbnail: dict = None):
        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.width = width
        self.height = height
        self.file_size = file_size
        self.thumbnail = PhotoSize.from_dict(thumbnail) if thumbnail else None

    @classmethod
    def from_dict(cls, data: dict) -> 'Photo':
        return cls(
            file_id=data['file_id'],
            file_unique_id=data['file_unique_id'],
            width=data['width'],
            height=data['height'],
            file_size=data.get('file_size'),
            thumbnail=data.get('thumbnail'))


class Audio:
    """Класс для представления аудиофайла"""
    def __init__(self, file_id: str, file_unique_id: str, duration: int, performer: str = None, 
                 title: str = None, thumbnail: dict = None, file_name: str = None, 
                 mime_type: str = None, file_size: int = None):
        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.duration = duration
        self.performer = performer
        self.title = title
        self.thumbnail = PhotoSize.from_dict(thumbnail) if thumbnail else None
        self.file_name = file_name
        self.mime_type = mime_type
        self.file_size = file_size

    @classmethod
    def from_dict(cls, data: dict) -> 'Audio':
        return cls(
            file_id=data['file_id'],
            file_unique_id=data['file_unique_id'],
            duration=data['duration'],
            performer=data.get('performer'),
            title=data.get('title'),
            thumbnail=data.get('thumbnail'),
            file_name=data.get('file_name'),
            mime_type=data.get('mime_type'),
            file_size=data.get('file_size'))


class Voice:
    """Класс для представления голосового сообщения"""
    def __init__(self, file_id: str, file_unique_id: str, duration: int, mime_type: str = None, 
                 file_size: int = None, thumbnail: dict = None):
        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.duration = duration
        self.mime_type = mime_type
        self.file_size = file_size
        self.thumbnail = PhotoSize.from_dict(thumbnail) if thumbnail else None

    @classmethod
    def from_dict(cls, data: dict) -> 'Voice':
        return cls(
            file_id=data['file_id'],
            file_unique_id=data['file_unique_id'],
            duration=data['duration'],
            mime_type=data.get('mime_type'),
            file_size=data.get('file_size'),
            thumbnail=data.get('thumbnail'))


class Video:
    """Класс для представления видеофайла"""
    def __init__(self, file_id: str, file_unique_id: str, duration: int, width: int, height: int, 
                 thumbnail: dict = None, file_name: str = None, mime_type: str = None, 
                 file_size: int = None, supports_streaming: bool = None):
        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.duration = duration
        self.width = width
        self.height = height
        self.thumbnail = PhotoSize.from_dict(thumbnail) if thumbnail else None
        self.file_name = file_name
        self.mime_type = mime_type
        self.file_size = file_size
        self.supports_streaming = supports_streaming

    @classmethod
    def from_dict(cls, data: dict) -> 'Video':
        return cls(
            file_id=data['file_id'],
            file_unique_id=data['file_unique_id'],
            duration=data['duration'],
            width=data['width'],
            height=data['height'],
            thumbnail=data.get('thumbnail'),
            file_name=data.get('file_name'),
            mime_type=data.get('mime_type'),
            file_size=data.get('file_size'),
            supports_streaming=data.get('supports_streaming'))


class VideoNote:
    """Класс для представления видеозаметки"""
    def __init__(self, file_id: str, file_unique_id: str, duration: int, length: int, 
                 thumbnail: dict = None, file_size: int = None):
        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.duration = duration
        self.length = length
        self.thumbnail = PhotoSize.from_dict(thumbnail) if thumbnail else None
        self.file_size = file_size

    @classmethod
    def from_dict(cls, data: dict) -> 'VideoNote':
        return cls(
            file_id=data['file_id'],
            file_unique_id=data['file_unique_id'],
            duration=data['duration'],
            length=data['length'],
            thumbnail=data.get('thumbnail'),
            file_size=data.get('file_size'))


class Animation:
    """Класс для представления анимации (GIF)"""
    def __init__(self, file_id: str, file_unique_id: str, width: int, height: int, duration: int, 
                 thumbnail: dict = None, file_name: str = None, mime_type: str = None, 
                 file_size: int = None):
        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.width = width
        self.height = height
        self.duration = duration
        self.thumbnail = PhotoSize.from_dict(thumbnail) if thumbnail else None
        self.file_name = file_name
        self.mime_type = mime_type
        self.file_size = file_size

    @classmethod
    def from_dict(cls, data: dict) -> 'Animation':
        return cls(
            file_id=data['file_id'],
            file_unique_id=data['file_unique_id'],
            width=data['width'],
            height=data['height'],
            duration=data['duration'],
            thumbnail=data.get('thumbnail'),
            file_name=data.get('file_name'),
            mime_type=data.get('mime_type'),
            file_size=data.get('file_size'))


class Dice:
    """Класс для представления броска игральной кости"""
    def __init__(self, emoji: str, value: int, animation_duration: int = None, static_url: str = None):
        self.emoji = emoji
        self.value = value
        self.animation_duration = animation_duration
        self.static_url = static_url

    @classmethod
    def from_dict(cls, data: dict) -> 'Dice':
        return cls(
            emoji=data['emoji'],
            value=data['value'],
            animation_duration=data.get('animation_duration'),
            static_url=data.get('static_url'))


class Sticker:
    """Класс для представления стикера"""
    def __init__(self, file_id: str, file_unique_id: str, width: int, height: int, 
                 is_animated: bool, is_video: bool, thumbnail: dict = None, 
                 emoji: str = None, set_name: str = None, mask_position: dict = None,
                 premium_animation: dict = None, file_size: int = None):
        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.width = width
        self.height = height
        self.is_animated = is_animated
        self.is_video = is_video
        self.thumbnail = PhotoSize.from_dict(thumbnail) if thumbnail else None
        self.emoji = emoji
        self.set_name = set_name
        self.mask_position = mask_position
        self.premium_animation = premium_animation
        self.file_size = file_size

    @classmethod
    def from_dict(cls, data: dict) -> 'Sticker':
        return cls(
            file_id=data['file_id'],
            file_unique_id=data['file_unique_id'],
            width=data['width'],
            height=data['height'],
            is_animated=data.get('is_animated', False),
            is_video=data.get('is_video', False),
            thumbnail=data.get('thumbnail'),
            emoji=data.get('emoji'),
            set_name=data.get('set_name'),
            mask_position=data.get('mask_position'),
            premium_animation=data.get('premium_animation'),
            file_size=data.get('file_size'))


class Location:
    """Класс для представления геолокации"""
    def __init__(self, latitude: float, longitude: float, horizontal_accuracy: float = None,
                 live_period: int = None, heading: int = None, proximity_alert_radius: int = None):
        self.latitude = latitude
        self.longitude = longitude
        self.horizontal_accuracy = horizontal_accuracy
        self.live_period = live_period
        self.heading = heading
        self.proximity_alert_radius = proximity_alert_radius

    @classmethod
    def from_dict(cls, data: dict) -> 'Location':
        return cls(
            latitude=data['latitude'],
            longitude=data['longitude'],
            horizontal_accuracy=data.get('horizontal_accuracy'),
            live_period=data.get('live_period'),
            heading=data.get('heading'),
            proximity_alert_radius=data.get('proximity_alert_radius'))

    def to_dict(self) -> dict:
        data = {'latitude': self.latitude, 'longitude': self.longitude}
        if self.horizontal_accuracy is not None:
            data['horizontal_accuracy'] = self.horizontal_accuracy
        if self.live_period is not None:
            data['live_period'] = self.live_period
        if self.heading is not None:
            data['heading'] = self.heading
        if self.proximity_alert_radius is not None:
            data['proximity_alert_radius'] = self.proximity_alert_radius
        return data


class Venue:
    """Класс для представления места проведения"""
    def __init__(self, location: 'Location', title: str, address: str, 
                 foursquare_id: str = None, foursquare_type: str = None,
                 google_place_id: str = None, google_place_type: str = None):
        self.location = location
        self.title = title
        self.address = address
        self.foursquare_id = foursquare_id
        self.foursquare_type = foursquare_type
        self.google_place_id = google_place_id
        self.google_place_type = google_place_type

    @classmethod
    def from_dict(cls, data: dict) -> 'Venue':
        location = Location.from_dict(data['location'])
        return cls(
            location=location,
            title=data['title'],
            address=data['address'],
            foursquare_id=data.get('foursquare_id'),
            foursquare_type=data.get('foursquare_type'),
            google_place_id=data.get('google_place_id'),
            google_place_type=data.get('google_place_type'))


class Contact:
    """Класс для представления контактных данных"""
    def __init__(self, phone_number: str, first_name: str, last_name: str = None, 
                 user_id: int = None, vcard: str = None):
        self.phone_number = phone_number
        self.first_name = first_name
        self.last_name = last_name
        self.user_id = user_id
        self.vcard = vcard

    @classmethod
    def from_dict(cls, data: dict) -> 'Contact':
        return cls(
            phone_number=data['phone_number'],
            first_name=data['first_name'],
            last_name=data.get('last_name'),
            user_id=data.get('user_id'),
            vcard=data.get('vcard'))


class Document:
    """Класс для представления документа"""
    def __init__(self, file_id: str, file_unique_id: str, file_name: str = None, 
                 mime_type: str = None, file_size: int = None, thumbnail: dict = None):
        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.file_name = file_name
        self.mime_type = mime_type
        self.file_size = file_size
        self.thumbnail = PhotoSize.from_dict(thumbnail) if thumbnail else None

    @classmethod
    def from_dict(cls, data: dict) -> 'Document':
        return cls(
            file_id=data['file_id'],
            file_unique_id=data['file_unique_id'],
            file_name=data.get('file_name'),
            mime_type=data.get('mime_type'),
            file_size=data.get('file_size'),
            thumbnail=data.get('thumbnail'))


class File:
    """Класс для представления файла"""
    def __init__(self, file_id: str, file_unique_id: str, file_size: int = None, file_path: str = None):
        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.file_size = file_size
        self.file_path = file_path

    @classmethod
    def from_dict(cls, data: dict) -> 'File':
        return cls(
            file_id=data['file_id'],
            file_unique_id=data['file_unique_id'],
            file_size=data.get('file_size'),
            file_path=data.get('file_path'))


class WebhookInfo:
    """Класс для представления информации о вебхуке"""
    def __init__(self, url: str = None, has_custom_certificate: bool = None, 
                 pending_update_count: int = None, last_error_date: int = None, 
                 last_error_message: str = None, last_synchronization_error_date: int = None,
                 max_connections: int = None, allowed_updates: list = None,
                 ip_address: str = None, protect_content: bool = None):
        self.url = url
        self.has_custom_certificate = has_custom_certificate
        self.pending_update_count = pending_update_count
        self.last_error_date = last_error_date
        self.last_error_message = last_error_message
        self.last_synchronization_error_date = last_synchronization_error_date
        self.max_connections = max_connections
        self.allowed_updates = allowed_updates
        self.ip_address = ip_address
        self.protect_content = protect_content

    @classmethod
    def from_dict(cls, data: dict) -> 'WebhookInfo':
        return cls(
            url=data.get('url'),
            has_custom_certificate=data.get('has_custom_certificate'),
            pending_update_count=data.get('pending_update_count'),
            last_error_date=data.get('last_error_date'),
            last_error_message=data.get('last_error_message'),
            last_synchronization_error_date=data.get('last_synchronization_error_date'),
            max_connections=data.get('max_connections'),
            allowed_updates=data.get('allowed_updates'),
            ip_address=data.get('ip_address'),
            protect_content=data.get('protect_content'))


class InputFile:
    """Класс для представления файла, отправляемого через Bot API"""
    def __init__(self, file_path: str):
        self.file_path = file_path

    def __str__(self) -> str:
        return self.file_path


class InputMedia:
    """Базовый класс для медиа контента"""
    def __init__(self, media: str, caption: str = None, parse_mode: str = None, 
                 caption_entities: list = None):
        self.media = media
        self.caption = caption
        self.parse_mode = parse_mode
        self.caption_entities = caption_entities

    def to_dict(self) -> dict:
        data = {'media': self.media}
        if self.caption:
            data['caption'] = self.caption
        if self.parse_mode:
            data['parse_mode'] = self.parse_mode
        if self.caption_entities:
            data['caption_entities'] = [entity.to_dict() for entity in self.caption_entities]
        return data


class InputMediaPhoto(InputMedia):
    """Класс для отправки фото"""
    def __init__(self, media: str, caption: str = None, parse_mode: str = "Markdown", 
                 caption_entities: list = None, show_caption_above_media: bool = None, 
                 has_spoiler: bool = None):
        super().__init__(media, caption, parse_mode, caption_entities)
        self.type = 'photo'
        self.show_caption_above_media = show_caption_above_media
        self.has_spoiler = has_spoiler

    def to_dict(self) -> dict:
        data = super().to_dict()
        data['type'] = self.type
        if self.show_caption_above_media is not None:
            data['show_caption_above_media'] = self.show_caption_above_media
        if self.has_spoiler is not None:
            data['has_spoiler'] = self.has_spoiler
        return data


class InputMediaVideo(InputMedia):
    """Класс для отправки видео"""
    def __init__(self, media: str, caption: str = None, parse_mode: str = "Markdown", 
                 caption_entities: list = None, show_caption_above_media: bool = None, 
                 width: int = None, height: int = None, duration: int = None, 
                 supports_streaming: bool = False, has_spoiler: bool = None):
        super().__init__(media, caption, parse_mode, caption_entities)
        self.type = 'video'
        self.show_caption_above_media = show_caption_above_media
        self.width = width
        self.height = height
        self.duration = duration
        self.supports_streaming = supports_streaming
        self.has_spoiler = has_spoiler

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({'type': self.type, 'supports_streaming': self.supports_streaming})
        if self.width:
            data['width'] = self.width
        if self.height:
            data['height'] = self.height
        if self.duration:
            data['duration'] = self.duration
        if self.show_caption_above_media is not None:
            data['show_caption_above_media'] = self.show_caption_above_media
        if self.has_spoiler is not None:
            data['has_spoiler'] = self.has_spoiler
        return data


class InputMediaAnimation(InputMedia):
    """Класс для отправки анимации"""
    def __init__(self, media: str, caption: str = None, parse_mode: str = "Markdown", 
                 caption_entities: list = None, show_caption_above_media: bool = None, 
                 width: int = None, height: int = None, duration: int = None, has_spoiler: bool = None):
        super().__init__(media, caption, parse_mode, caption_entities)
        self.type = 'animation'
        self.width = width
        self.height = height
        self.duration = duration
        self.show_caption_above_media = show_caption_above_media
        self.has_spoiler = has_spoiler

    def to_dict(self) -> dict:
        data = super().to_dict()
        data['type'] = self.type
        if self.width:
            data['width'] = self.width
        if self.height:
            data['height'] = self.height
        if self.duration:
            data['duration'] = self.duration
        if self.show_caption_above_media is not None:
            data['show_caption_above_media'] = self.show_caption_above_media
        if self.has_spoiler is not None:
            data['has_spoiler'] = self.has_spoiler
        return data


class InputMediaAudio(InputMedia):
    """Класс для отправки аудиофайлов"""
    def __init__(self, media: str, caption: str = None, parse_mode: str = "Markdown", 
                 caption_entities: list = None, duration: int = None, 
                 performer: str = None, title: str = None):
        super().__init__(media, caption, parse_mode, caption_entities)
        self.type = 'audio'
        self.duration = duration
        self.performer = performer
        self.title = title

    def to_dict(self) -> dict:
        data = super().to_dict()
        data['type'] = self.type
        if self.duration:
            data['duration'] = self.duration
        if self.performer:
            data['performer'] = self.performer
        if self.title:
            data['title'] = self.title
        return data


class InputMediaDocument(InputMedia):
    """Класс для отправки документов"""
    def __init__(self, media: str, caption: str = None, parse_mode: str = "Markdown", 
                 caption_entities: list = None, disable_content_type_detection: bool = False):
        super().__init__(media, caption, parse_mode, caption_entities)
        self.type = 'document'
        self.disable_content_type_detection = disable_content_type_detection

    def to_dict(self) -> dict:
        data = super().to_dict()
        data['type'] = self.type
        if self.disable_content_type_detection:
            data['disable_content_type_detection'] = self.disable_content_type_detection
        return data


class InlineQuery:
    """Класс для обработки inline-запросов"""
    def __init__(self, id: str, from_user: 'User', query: str, offset: str, 
                 chat_type: str = None, location: 'Location' = None):
        self.id = id
        self.from_user = from_user
        self.query = query
        self.offset = offset
        self.chat_type = chat_type
        self.location = location

    @classmethod
    def from_dict(cls, data: dict) -> 'InlineQuery':
        from_user = User.from_dict(data['from'])
        location = Location.from_dict(data['location']) if 'location' in data else None
        return cls(
            id=data['id'],
            from_user=from_user,
            query=data['query'],
            offset=data['offset'],
            chat_type=data.get('chat_type'),
            location=location)


class InlineQueryResult:
    """Базовый класс для inline-результатов"""
    def __init__(self, type: str, id: str):
        self.type = type
        self.id = id

    def to_dict(self) -> dict:
        return {'type': self.type, 'id': self.id}


class InlineQueryResultArticle(InlineQueryResult):
    """Класс для отправки статьи"""
    def __init__(self, id: str, title: str, input_message_content: dict,
                 reply_markup: dict = None, url: str = None, hide_url: bool = None,
                 description: str = None, thumb_url: str = None, thumb_width: int = None, 
                 thumb_height: int = None):
        super().__init__('article', id)
        self.title = title
        self.input_message_content = input_message_content
        self.reply_markup = reply_markup
        self.url = url
        self.hide_url = hide_url
        self.description = description
        self.thumb_url = thumb_url
        self.thumb_width = thumb_width
        self.thumb_height = thumb_height

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            'title': self.title,
            'input_message_content': self.input_message_content,
        })
        if self.reply_markup is not None:
            data['reply_markup'] = self.reply_markup
        if self.url is not None:
            data['url'] = self.url
        if self.hide_url is not None:
            data['hide_url'] = self.hide_url
        if self.description is not None:
            data['description'] = self.description
        if self.thumb_url is not None:
            data['thumb_url'] = self.thumb_url
        if self.thumb_width is not None:
            data['thumb_width'] = self.thumb_width
        if self.thumb_height is not None:
            data['thumb_height'] = self.thumb_height
        return data


class InlineQueryResultPhoto(InlineQueryResult):
    """Класс для отправки фото"""
    def __init__(self, id: str, photo_url: str, thumb_url: str, photo_width: int = None, 
                 photo_height: int = None, title: str = None, description: str = None, 
                 caption: str = None, parse_mode: str = None, reply_markup: dict = None):
        super().__init__('photo', id)
        self.photo_url = photo_url
        self.thumb_url = thumb_url
        self.photo_width = photo_width
        self.photo_height = photo_height
        self.title = title
        self.description = description
        self.caption = caption
        self.parse_mode = parse_mode
        self.reply_markup = reply_markup

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            'photo_url': self.photo_url,
            'thumb_url': self.thumb_url
        })
        if self.photo_width is not None:
            data['photo_width'] = self.photo_width
        if self.photo_height is not None:
            data['photo_height'] = self.photo_height
        if self.title is not None:
            data['title'] = self.title
        if self.description is not None:
            data['description'] = self.description
        if self.caption is not None:
            data['caption'] = self.caption
        if self.parse_mode is not None:
            data['parse_mode'] = self.parse_mode
        if self.reply_markup is not None:
            data['reply_markup'] = self.reply_markup
        return data


class InlineQueryResultVideo(InlineQueryResult):
    """Класс для отправки видео"""
    def __init__(self, id: str, video_url: str, mime_type: str, thumb_url: str, title: str,
                 caption: str = None, parse_mode: str = None, video_width: int = None,
                 video_height: int = None, video_duration: int = None, description: str = None,
                 reply_markup: dict = None):
        super().__init__('video', id)
        self.video_url = video_url
        self.mime_type = mime_type
        self.thumb_url = thumb_url
        self.title = title
        self.caption = caption
        self.parse_mode = parse_mode
        self.video_width = video_width
        self.video_height = video_height
        self.video_duration = video_duration
        self.description = description
        self.reply_markup = reply_markup

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({'video_url': self.video_url, 'mime_type': self.mime_type, 
                     'thumb_url': self.thumb_url, 'title': self.title})
        if self.caption is not None:
            data['caption'] = self.caption
        if self.parse_mode is not None:
            data['parse_mode'] = self.parse_mode
        if self.video_width is not None:
            data['video_width'] = self.video_width
        if self.video_height is not None:
            data['video_height'] = self.video_height
        if self.video_duration is not None:
            data['video_duration'] = self.video_duration
        if self.description is not None:
            data['description'] = self.description
        if self.reply_markup is not None:
            data['reply_markup'] = self.reply_markup
        return data


class LabeledPrice:
    """Класс для обработки платежей"""
    def __init__(self, label: str, amount: int):
        self.label = label
        self.amount = amount

    def to_dict(self) -> dict:
        return {'label': self.label, 'amount': self.amount}


class ShippingOption:
    """Класс для вариантов доставки"""
    def __init__(self, id: str, title: str, prices: list):
        self.id = id
        self.title = title
        self.prices = prices

    def to_dict(self) -> dict:
        return {'id': self.id, 'title': self.title, 'prices': [price.to_dict() for price in self.prices]}


class UserProfilePhotos:
    """Класс для фотографий профиля пользователя"""
    def __init__(self, total_count: int, photos: list):
        self.total_count = total_count
        self.photos = photos

    @classmethod
    def from_dict(cls, data: dict) -> 'UserProfilePhotos':
        photos = [[PhotoSize.from_dict(photo) for photo in photo_list] for photo_list in data['photos']]
        return cls(total_count=data['total_count'], photos=photos)


class CallbackQuery:
    """Класс для обработки callback-запросов"""
    def __init__(self, callback_query_data: dict):
        self.id = callback_query_data['id']
        self.from_user = User.from_dict(callback_query_data['from'])
        self.data = callback_query_data.get('data')
        self.message = Message.from_dict(callback_query_data['message']) if callback_query_data.get('message') else None
        self.inline_message_id = callback_query_data.get('inline_message_id')
        self.chat_instance = callback_query_data.get('chat_instance')
        self.game_short_name = callback_query_data.get('game_short_name')


class ForumTopic:
    """Класс для представления темы форума"""
    def __init__(self, message_thread_id: int, name: str, icon_color: int, 
                 icon_custom_emoji_id: str = None, is_name_implicit: bool = None):
        self.message_thread_id = message_thread_id
        self.name = name
        self.icon_color = icon_color
        self.icon_custom_emoji_id = icon_custom_emoji_id
        self.is_name_implicit = is_name_implicit

    @classmethod
    def from_dict(cls, data: dict) -> 'ForumTopic':
        return cls(
            message_thread_id=data['message_thread_id'],
            name=data['name'],
            icon_color=data['icon_color'],
            icon_custom_emoji_id=data.get('icon_custom_emoji_id'),
            is_name_implicit=data.get('is_name_implicit'))


class MessageEntity:
    """Класс для описания форматирования текста"""
    def __init__(self, type: str, offset: int, length: int, url: str = None,
                 user: dict = None, language: str = None):
        self.type = type
        self.offset = offset
        self.length = length
        self.url = url
        self.user = user
        self.language = language

    def to_dict(self) -> dict:
        data = {
            'type': self.type,
            'offset': self.offset,
            'length': self.length,
            'url': self.url,
            'user': self.user,
            'language': self.language}
        return {k: v for k, v in data.items() if v is not None}


class Message:
    """Класс для представления сообщения"""
    def __init__(self, message_id: int, chat: 'Chat', from_user: 'User' = None, text: str = None, 
                 date: int = None, message_thread_id: int = None, is_topic_message: bool = None,
                 reply_to_message: 'Message' = None, content_type: str = None, 
                 photo: list = None, audio: 'Audio' = None, video: 'Video' = None, 
                 video_note: 'VideoNote' = None, voice: 'Voice' = None, animation: 'Animation' = None, 
                 dice: 'Dice' = None, sticker: 'Sticker' = None, document: 'Document' = None, 
                 caption: str = None, new_chat_members: list = None, new_chat_member: 'User' = None, 
                 left_chat_member: 'User' = None, entities: list = None, 
                 venue: 'Venue' = None, contact: 'Contact' = None, location: 'Location' = None,
                 poll: dict = None, game: dict = None, invoice: dict = None, 
                 successful_payment: dict = None, connected_website: str = None, 
                 write_access_allowed: bool = None, passport_data: dict = None, 
                 forum_topic_created: 'ForumTopic' = None, gift_sent: bool = None, 
                 gift_upgrade_sent: bool = None, giveaway_started: dict = None,
                 giveaway: dict = None, giveaway_winners: dict = None):
        self.message_id = message_id
        self.chat = chat
        self.from_user = from_user
        self.text = text
        self.date = date
        self.message_thread_id = message_thread_id
        self.is_topic_message = is_topic_message
        self.reply_to_message = reply_to_message
        self.content_type = content_type
        self.photo = photo
        self.audio = audio
        self.video = video
        self.video_note = video_note
        self.voice = voice
        self.animation = animation
        self.dice = dice
        self.sticker = sticker
        self.document = document
        self.caption = caption
        self.new_chat_members = new_chat_members
        self.new_chat_member = new_chat_member
        self.left_chat_member = left_chat_member
        self.entities = entities
        self.venue = venue
        self.contact = contact
        self.location = location
        self.poll = poll
        self.game = game
        self.invoice = invoice
        self.successful_payment = successful_payment
        self.connected_website = connected_website
        self.write_access_allowed = write_access_allowed
        self.passport_data = passport_data
        self.forum_topic_created = forum_topic_created
        self.gift_sent = gift_sent
        self.gift_upgrade_sent = gift_upgrade_sent
        self.giveaway_started = giveaway_started
        self.giveaway = giveaway
        self.giveaway_winners = giveaway_winners

    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        chat = Chat.from_dict(data['chat'])
        from_user = User.from_dict(data['from']) if 'from' in data else None
        reply_to_message = Message.from_dict(data['reply_to_message']) if 'reply_to_message' in data else None
        forum_topic_created = ForumTopic.from_dict(data['forum_topic_created']) if 'forum_topic_created' in data else None
        
        content_type = None
        text = None
        photo = None
        audio = None
        video = None
        video_note = None
        voice = None
        animation = None
        dice = None
        sticker = None
        document = None
        new_chat_members = None
        new_chat_member = None
        left_chat_member = None
        caption = data.get('caption')
        entities = [MessageEntity(**entity) for entity in data.get('entities', [])]
        venue = Venue.from_dict(data['venue']) if 'venue' in data else None
        contact = Contact.from_dict(data['contact']) if 'contact' in data else None
        location = Location.from_dict(data['location']) if 'location' in data else None
        
        if 'text' in data:
            content_type = 'text'
            text = data['text']
        elif 'photo' in data:
            content_type = 'photo'
            photo = [Photo.from_dict(p) for p in data['photo']]
        elif 'audio' in data:
            content_type = 'audio'
            audio = Audio.from_dict(data['audio'])
        elif 'video' in data:
            content_type = 'video'
            video = Video.from_dict(data['video'])
        elif 'video_note' in data:
            content_type = 'video_note'
            video_note = VideoNote.from_dict(data['video_note'])
        elif 'voice' in data:
            content_type = 'voice'
            voice = Voice.from_dict(data['voice'])
        elif 'animation' in data:
            content_type = 'animation'
            animation = Animation.from_dict(data['animation'])
        elif 'dice' in data:
            content_type = 'dice'
            dice = Dice.from_dict(data['dice'])
        elif 'sticker' in data:
            content_type = 'sticker'
            sticker = Sticker.from_dict(data['sticker'])
        elif 'document' in data:
            content_type = 'document'
            document = Document.from_dict(data['document'])
        elif 'new_chat_members' in data:
            content_type = 'new_chat_members'
            new_chat_members = [User.from_dict(member) for member in data['new_chat_members']]
        elif 'new_chat_member' in data:
            content_type = 'new_chat_member'
            new_chat_member = User.from_dict(data['new_chat_member'])
        elif 'left_chat_member' in data:
            content_type = 'left_chat_member'
            left_chat_member = User.from_dict(data['left_chat_member'])
        
        return cls(
            message_id=data['message_id'],
            chat=chat,
            from_user=from_user,
            text=text,
            date=data.get('date'),
            message_thread_id=data.get('message_thread_id'),
            is_topic_message=data.get('is_topic_message'),
            reply_to_message=reply_to_message,
            content_type=content_type,
            photo=photo,
            audio=audio,
            video=video,
            video_note=video_note,
            voice=voice,
            animation=animation,
            dice=dice,
            sticker=sticker,
            document=document,
            caption=caption,
            new_chat_members=new_chat_members,
            new_chat_member=new_chat_member,
            left_chat_member=left_chat_member,
            entities=entities,
            venue=venue,
            contact=contact,
            location=location,
            forum_topic_created=forum_topic_created,
            gift_upgrade_sent=data.get('gift_upgrade_sent'))


class Markup:
    """Класс для создания клавиатур"""
    @staticmethod
    def create_reply_keyboard(buttons: list, row_width: int = 2, is_persistent: bool = False, 
                              resize_keyboard: bool = True, one_time_keyboard: bool = False,
                              selective: bool = False) -> dict:
        if not buttons:
            raise ValueError("buttons не может быть None")
        keyboard = []
        for i in range(0, len(buttons), row_width):
            keyboard.append(buttons[i:i + row_width])
        return {'keyboard': keyboard, 'is_persistent': is_persistent, 
                'resize_keyboard': resize_keyboard, 'one_time_keyboard': one_time_keyboard,
                'selective': selective}

    @staticmethod
    def remove_reply_keyboard(status: bool = True, selective: bool = False) -> dict:
        result = {'remove_keyboard': status}
        if selective:
            result['selective'] = True
        return result

    @staticmethod
    def create_inline_keyboard(buttons: list, row_width: int = 2) -> dict:
        if not buttons:
            raise ValueError("buttons не может быть None")
        keyboard = []
        for i in range(0, len(buttons), row_width):
            keyboard.append(buttons[i:i + row_width])
        return {'inline_keyboard': keyboard}


class BusinessIntro:
    """Класс для представления вводной информации бизнес-аккаунта"""
    def __init__(self, text: str, text_format_mode: str = None, sticker: 'Sticker' = None):
        self.text = text
        self.text_format_mode = text_format_mode
        self.sticker = sticker


class BusinessLocation:
    """Класс для представления местоположения бизнес-аккаунта"""
    def __init__(self, address: str, location: 'Location' = None):
        self.address = address
        self.location = location


class BusinessOpeningHours:
    """Класс для представления часов работы бизнес-аккаунта"""
    def __init__(self, timezone_name: str, opening_hours: list):
        self.timezone_name = timezone_name
        self.opening_hours = opening_hours


class BusinessMessage:
    """Класс для представления бизнес-сообщения"""
    def __init__(self, id: str, business_connection_id: str, chat: 'Chat', 
                 from_user: 'User', date: int, **kwargs):
        self.id = id
        self.business_connection_id = business_connection_id
        self.chat = chat
        self.from_user = from_user
        self.date = date
        for key, value in kwargs.items():
            setattr(self, key, value)


class Gift:
    """Класс для представления подарка"""
    def __init__(self, id: str, gift: str, star_count: int, total_count: int,
                 is_limited: bool = None, is_unique: bool = None, 
                 contains_gift: bool = None, gift_id: str = None, 
                 is_from_blockchain: bool = None, is_premium: bool = None,
                 personal_total_count: int = None, personal_remaining_count: int = None,
                 has_colors: bool = None, background: dict = None, 
                 unique_gift_variant_count: int = None):
        self.id = id
        self.gift = gift
        self.star_count = star_count
        self.total_count = total_count
        self.is_limited = is_limited
        self.is_unique = is_unique
        self.contains_gift = contains_gift
        self.gift_id = gift_id
        self.is_from_blockchain = is_from_blockchain
        self.is_premium = is_premium
        self.personal_total_count = personal_total_count
        self.personal_remaining_count = personal_remaining_count
        self.has_colors = has_colors
        self.background = background
        self.unique_gift_variant_count = unique_gift_variant_count


class UniqueGift:
    """Класс для представления уникального подарка"""
    def __init__(self, id: str, gift_id: str, owner_id: int, owned_gift: dict,
                 gift: 'Gift' = None, last_resale_star_count: int = None, 
                 is_from_blockchain: bool = None, is_premium: bool = None, 
                 colors: dict = None):
        self.id = id
        self.gift_id = gift_id
        self.owner_id = owner_id
        self.owned_gift = owned_gift
        self.gift = gift
        self.last_resale_star_count = last_resale_star_count
        self.is_from_blockchain = is_from_blockchain
        self.is_premium = is_premium
        self.colors = colors


class UniqueGiftColors:
    """Класс для представления цветовых схем уникального подарка"""
    def __init__(self, light: dict, dark: dict):
        self.light = light
        self.dark = dark


class GiftBackground:
    """Класс для представления фона подарка"""
    def __init__(self, type: str, colors: dict):
        self.type = type
        self.colors = colors


class UserRating:
    """Класс для представления рейтинга пользователя"""
    def __init__(self, rating: float, user: 'User'):
        self.rating = rating
        self.user = user


class ChecklistTask:
    """Класс для представления задачи в чек-листе"""
    def __init__(self, id: str, title: str, task_set_id: str, 
                 position: int, is_unowned: bool = None, is_multiple: bool = None,
                 name: str = None, name_localized: str = None, 
                 completed_by_user_id: int = None, completed_by_chat: dict = None):
        self.id = id
        self.title = title
        self.task_set_id = task_set_id
        self.position = position
        self.is_unowned = is_unowned
        self.is_multiple = is_multiple
        self.name = name
        self.name_localized = name_localized
        self.completed_by_user_id = completed_by_user_id
        self.completed_by_chat = completed_by_chat


# Основа
class Bot:
    """Класс для работы с Telegram Bot API"""
    
    def __init__(self, token: str):
        """Создает экземпляр Bot"""
        self.token = token
        self.handlers = {'message': [], 'command': [], 'callback_query': [], 'inline_query': []}
        self.running = False
        self.update_offset = 0
        self.next_steps = {}
        self.bot_info = self.get_me()
        self.bot_username = self.bot_info.username.lower() if self.bot_info and self.bot_info.username else None

    def _make_request(self, method: str, params: dict = None, files: dict = None, json_data: dict = None):
        """Отправляет запрос в Telegram API с обработкой ошибок и повторными попытками"""
        url = f'https://api.telegram.org/bot{self.token}/{method}'
        max_retries = 3
        retry_after = 3
        
        for attempt in range(max_retries):
            try:
                response = requests.post(url, params=params, files=files, json=json_data)
                if response.status_code == 200:
                    return response.json()
                if response.status_code == 429:
                    retry_after = response.json().get('parameters', {}).get('retry_after', retry_after)
                    print(f"Ошибка 429 в методе {method}: Превышен лимит запросов. Повтор через {retry_after} секунд")
                    time.sleep(retry_after)
                elif response.status_code == 502:
                    print(f"Ошибка 502 в методе {method}: Bad Gateway. Попытка повторить запрос через несколько секунд...")
                    time.sleep(random.uniform(2, 5))
                elif response.status_code == 503:
                    print(f"Ошибка 503 в методе {method}: Сервис недоступен. Повтор через несколько секунд...")
                    time.sleep(random.uniform(5, 10))
                elif response.status_code == 400:
                    print(f"Ошибка 400 в методе {method}: Неверный запрос. {response.text}")
                    return None
                elif response.status_code == 404:
                    print(f"Ошибка 404 в методе {method}: Страница не найдена. {response.text}")
                    return None
                else:
                    print(f"Неизвестная ошибка в методе {method}: {response.status_code} - {response.text}")
                    return None
            except requests.exceptions.RequestException as e:
                return None
            except Exception as e:
                print(f"Необработанная ошибка: {e}")
                return None
            time.sleep(2 ** attempt + random.uniform(0, 1))
        print(f"Не удалось выполнить запрос {method} после {max_retries} попыток")
        return None

    def reply_message(self, chat_id: Union[int, str] = None, text: str = None, mode: str = "Markdown",
                      disable_web_page_preview: bool = None, disable_notification: bool = None,
                      reply_to_message_id: int = None, reply_markup: Union[dict, Markup] = None,
                      message_thread_id: int = None, protect_content: bool = None,
                      link_preview_options: dict = None) -> Optional[Message]:
        """Отправляет сообщение"""
        method = 'sendMessage'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif text is None:
            raise ValueError("text не должен быть None")
        
        params = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': mode,
            'disable_web_page_preview': disable_web_page_preview,
            'disable_notification': disable_notification,
            'reply_to_message_id': reply_to_message_id,
            'reply_markup': json.dumps(reply_markup) if reply_markup is not None else None,
            'message_thread_id': message_thread_id,
            'protect_content': protect_content,
            'link_preview_options': json.dumps(link_preview_options) if link_preview_options is not None else None
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        if response and 'result' in response:
            return Message.from_dict(response['result'])
        return None

    def reply_message_draft(self, chat_id: Union[int, str] = None, draft_id: str = None,
                            message_thread_id: int = None) -> Optional[Message]:
        """Отправляет черновик сообщения (Bot API 9.3)"""
        method = 'sendDraftMessage'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif draft_id is None:
            raise ValueError("draft_id не должен быть None")
        
        params = {
            'chat_id': chat_id,
            'draft_id': draft_id,
            'message_thread_id': message_thread_id
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        if response and 'result' in response:
            return Message.from_dict(response['result'])
        return None

    def get_user_gifts(self, user_id: int = None, offset: int = None, limit: int = None) -> list:
        """Получает подарки пользователя (Bot API 9.3)"""
        method = 'getUserGifts'
        if user_id is None:
            raise ValueError("user_id не должен быть None")
        
        params = {
            'user_id': user_id,
            'offset': offset,
            'limit': limit
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        if response and 'result' in response:
            return response['result']
        return []

    def get_chat_gifts(self, chat_id: Union[int, str] = None, offset: int = None, limit: int = None) -> list:
        """Получает подарки чата (Bot API 9.3)"""
        method = 'getChatGifts'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        
        params = {
            'chat_id': chat_id,
            'offset': offset,
            'limit': limit
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        if response and 'result' in response:
            return response['result']
        return []

    def repost_story(self, chat_id: Union[int, str] = None, from_chat_id: Union[int, str] = None,
                     story_id: int = None, disable_notification: bool = None,
                     protect_content: bool = None) -> Optional[Message]:
        """Репостит историю (Bot API 9.3)"""
        method = 'repostStory'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif from_chat_id is None:
            raise ValueError("from_chat_id не должен быть None")
        elif story_id is None:
            raise ValueError("story_id не должен быть None")
        
        params = {
            'chat_id': chat_id,
            'from_chat_id': from_chat_id,
            'story_id': story_id,
            'disable_notification': disable_notification,
            'protect_content': protect_content
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        if response and 'result' in response:
            return Message.from_dict(response['result'])
        return None

    def reply_photo(self, chat_id: Union[int, str] = None, photo: Union[str, bytes] = None,
                    caption: str = None, mode: str = "Markdown", disable_notification: bool = None,
                    reply_to_message_id: int = None, reply_markup: Union[dict, Markup] = None,
                    message_thread_id: int = None, protect_content: bool = None,
                    has_spoiler: bool = None, show_caption_above_media: bool = None) -> Optional[Message]:
        """Отправляет фотографию"""
        method = 'sendPhoto'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif photo is None:
            raise ValueError("photo не должен быть None")
        
        params = {
            'chat_id': chat_id,
            'caption': caption,
            'parse_mode': mode,
            'disable_notification': disable_notification,
            'reply_to_message_id': reply_to_message_id,
            'reply_markup': json.dumps(reply_markup) if reply_markup is not None else None,
            'message_thread_id': message_thread_id,
            'protect_content': protect_content,
            'has_spoiler': has_spoiler,
            'show_caption_above_media': show_caption_above_media
        }
        params = {k: v for k, v in params.items() if v is not None}
        
        files = None
        if isinstance(photo, str):
            params['photo'] = photo
        else:
            files = {'photo': photo}
        
        response = self._make_request(method, params, files)
        if response and 'result' in response:
            return Message.from_dict(response['result'])
        return None

    def reply_audio(self, chat_id: Union[int, str] = None, audio: Union[str, bytes] = None,
                    caption: str = None, mode: str = "Markdown", duration: int = None,
                    performer: str = None, title: str = None, thumb: Union[str, bytes] = None,
                    disable_notification: bool = None, reply_to_message_id: int = None,
                    reply_markup: Union[dict, Markup] = None, message_thread_id: int = None,
                    protect_content: bool = None) -> Optional[Message]:
        """Отправляет аудиофайл"""
        method = 'sendAudio'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif audio is None:
            raise ValueError("audio не должен быть None")
        
        params = {
            'chat_id': chat_id,
            'caption': caption,
            'parse_mode': mode,
            'duration': duration,
            'performer': performer,
            'title': title,
            'disable_notification': disable_notification,
            'reply_to_message_id': reply_to_message_id,
            'reply_markup': json.dumps(reply_markup) if reply_markup is not None else None,
            'message_thread_id': message_thread_id,
            'protect_content': protect_content
        }
        params = {k: v for k, v in params.items() if v is not None}
        
        files = None
        if isinstance(audio, str):
            params['audio'] = audio
        else:
            files = {'audio': audio}
        
        if thumb is not None:
            if isinstance(thumb, str):
                params['thumb'] = thumb
            else:
                if files is None:
                    files = {}
                files['thumb'] = thumb
        
        response = self._make_request(method, params, files)
        if response and 'result' in response:
            return Message.from_dict(response['result'])
        return None

    def reply_document(self, chat_id: Union[int, str] = None, document: Union[str, bytes] = None,
                       caption: str = None, mode: str = "Markdown", disable_notification: bool = None,
                       reply_to_message_id: int = None, reply_markup: Union[dict, Markup] = None,
                       message_thread_id: int = None, protect_content: bool = None,
                       disable_content_type_detection: bool = None) -> Optional[Message]:
        """Отправляет документ"""
        method = 'sendDocument'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif document is None:
            raise ValueError("document не должен быть None")
        
        params = {
            'chat_id': chat_id,
            'caption': caption,
            'parse_mode': mode,
            'disable_notification': disable_notification,
            'reply_to_message_id': reply_to_message_id,
            'reply_markup': json.dumps(reply_markup) if reply_markup is not None else None,
            'message_thread_id': message_thread_id,
            'protect_content': protect_content,
            'disable_content_type_detection': disable_content_type_detection
        }
        params = {k: v for k, v in params.items() if v is not None}
        
        files = None
        if isinstance(document, str):
            params['document'] = document
        else:
            files = {'document': document}
        
        response = self._make_request(method, params, files)
        if response and 'result' in response:
            return Message.from_dict(response['result'])
        return None

    def reply_video(self, chat_id: Union[int, str] = None, video: Union[str, bytes] = None,
                    duration: int = None, width: int = None, height: int = None,
                    caption: str = None, mode: str = "Markdown", supports_streaming: bool = None,
                    disable_notification: bool = None, reply_to_message_id: int = None,
                    reply_markup: Union[dict, Markup] = None, message_thread_id: int = None,
                    protect_content: bool = None, has_spoiler: bool = None,
                    show_caption_above_media: bool = None) -> Optional[Message]:
        """Отправляет видеофайл"""
        method = 'sendVideo'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif video is None:
            raise ValueError("video не должен быть None")
        
        params = {
            'chat_id': chat_id,
            'duration': duration,
            'width': width,
            'height': height,
            'caption': caption,
            'parse_mode': mode,
            'supports_streaming': supports_streaming,
            'disable_notification': disable_notification,
            'reply_to_message_id': reply_to_message_id,
            'reply_markup': json.dumps(reply_markup) if reply_markup is not None else None,
            'message_thread_id': message_thread_id,
            'protect_content': protect_content,
            'has_spoiler': has_spoiler,
            'show_caption_above_media': show_caption_above_media
        }
        params = {k: v for k, v in params.items() if v is not None}
        
        files = None
        if isinstance(video, str):
            params['video'] = video
        else:
            files = {'video': video}
        
        response = self._make_request(method, params, files)
        if response and 'result' in response:
            return Message.from_dict(response['result'])
        return None

    def reply_video_note(self, chat_id: Union[int, str] = None, video_note: Union[str, bytes] = None,
                         duration: int = None, length: int = None, disable_notification: bool = None,
                         reply_to_message_id: int = None, reply_markup: Union[dict, Markup] = None,
                         message_thread_id: int = None, protect_content: bool = None) -> Optional[Message]:
        """Отправляет видео-заметку"""
        method = 'sendVideoNote'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif video_note is None:
            raise ValueError("video_note не должен быть None")
        
        params = {
            'chat_id': chat_id,
            'duration': duration,
            'length': length,
            'disable_notification': disable_notification,
            'reply_to_message_id': reply_to_message_id,
            'reply_markup': json.dumps(reply_markup) if reply_markup is not None else None,
            'message_thread_id': message_thread_id,
            'protect_content': protect_content
        }
        params = {k: v for k, v in params.items() if v is not None}
        
        files = None
        if isinstance(video_note, str):
            params['video_note'] = video_note
        else:
            files = {'video_note': video_note}
        
        response = self._make_request(method, params, files)
        if response and 'result' in response:
            return Message.from_dict(response['result'])
        return None

    def reply_animation(self, chat_id: Union[int, str] = None, animation: Union[str, bytes] = None,
                        duration: int = None, width: int = None, height: int = None,
                        caption: str = None, mode: str = "Markdown", disable_notification: bool = None,
                        reply_to_message_id: int = None, reply_markup: Union[dict, Markup] = None,
                        message_thread_id: int = None, protect_content: bool = None,
                        has_spoiler: bool = None, show_caption_above_media: bool = None) -> Optional[Message]:
        """Отправляет анимацию"""
        method = 'sendAnimation'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif animation is None:
            raise ValueError("animation не должен быть None")
        
        params = {
            'chat_id': chat_id,
            'duration': duration,
            'width': width,
            'height': height,
            'caption': caption,
            'parse_mode': mode,
            'disable_notification': disable_notification,
            'reply_to_message_id': reply_to_message_id,
            'reply_markup': json.dumps(reply_markup) if reply_markup is not None else None,
            'message_thread_id': message_thread_id,
            'protect_content': protect_content,
            'has_spoiler': has_spoiler,
            'show_caption_above_media': show_caption_above_media
        }
        params = {k: v for k, v in params.items() if v is not None}
        
        files = None
        if isinstance(animation, str):
            params['animation'] = animation
        else:
            files = {'animation': animation}
        
        response = self._make_request(method, params, files)
        if response and 'result' in response:
            return Message.from_dict(response['result'])
        return None

    def reply_voice(self, chat_id: Union[int, str] = None, voice: Union[str, bytes] = None,
                    caption: str = None, mode: str = "Markdown", duration: int = None,
                    disable_notification: bool = None, reply_to_message_id: int = None,
                    reply_markup: Union[dict, Markup] = None, message_thread_id: int = None,
                    protect_content: bool = None) -> Optional[Message]:
        """Отправляет голосовое сообщение"""
        method = 'sendVoice'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif voice is None:
            raise ValueError("voice не должен быть None")
        
        params = {
            'chat_id': chat_id,
            'caption': caption,
            'parse_mode': mode,
            'duration': duration,
            'disable_notification': disable_notification,
            'reply_to_message_id': reply_to_message_id,
            'reply_markup': json.dumps(reply_markup) if reply_markup is not None else None,
            'message_thread_id': message_thread_id,
            'protect_content': protect_content
        }
        params = {k: v for k, v in params.items() if v is not None}
        
        files = None
        if isinstance(voice, str):
            params['voice'] = voice
        else:
            files = {'voice': voice}
        
        response = self._make_request(method, params, files)
        if response and 'result' in response:
            return Message.from_dict(response['result'])
        return None

    def reply_location(self, chat_id: Union[int, str] = None, latitude: float = None,
                       longitude: float = None, live_period: int = None,
                       disable_notification: bool = None, reply_to_message_id: int = None,
                       reply_markup: Union[dict, Markup] = None, message_thread_id: int = None,
                       protect_content: bool = None, horizontal_accuracy: float = None,
                       heading: int = None, proximity_alert_radius: int = None) -> Optional[Message]:
        """Отправляет локацию"""
        method = 'sendLocation'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif latitude is None:
            raise ValueError("latitude не должен быть None")
        elif longitude is None:
            raise ValueError("longitude не может быть None")
        
        params = {
            'chat_id': chat_id,
            'latitude': latitude,
            'longitude': longitude,
            'live_period': live_period,
            'disable_notification': disable_notification,
            'reply_to_message_id': reply_to_message_id,
            'reply_markup': json.dumps(reply_markup) if reply_markup is not None else None,
            'message_thread_id': message_thread_id,
            'protect_content': protect_content,
            'horizontal_accuracy': horizontal_accuracy,
            'heading': heading,
            'proximity_alert_radius': proximity_alert_radius
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        if response and 'result' in response:
            return Location.from_dict(response['result'])
        return None

    def reply_chat_action(self, chat_id: Union[int, str] = None, action: str = None,
                          message_thread_id: int = None) -> bool:
        """Отправляет активность чата"""
        method = 'sendChatAction'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif action is None:
            raise ValueError("action не должен быть None")
        
        params = {
            'chat_id': chat_id,
            'action': action,
            'message_thread_id': message_thread_id
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        return response and 'result' in response

    def reply_venue(self, chat_id: Union[int, str] = None, latitude: float = None,
                    longitude: float = None, title: str = None, address: str = None,
                    foursquare_id: str = None, disable_notification: bool = None,
                    reply_to_message_id: int = None, reply_markup: Union[dict, Markup] = None,
                    message_thread_id: int = None, protect_content: bool = None,
                    foursquare_type: str = None, google_place_id: str = None,
                    google_place_type: str = None) -> Optional[Message]:
        """Отправляет место"""
        method = 'sendVenue'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif latitude is None:
            raise ValueError("latitude не должен быть None")
        elif longitude is None:
            raise ValueError("longitude не может быть None")
        
        params = {
            'chat_id': chat_id,
            'latitude': latitude,
            'longitude': longitude,
            'title': title,
            'address': address,
            'foursquare_id': foursquare_id,
            'disable_notification': disable_notification,
            'reply_to_message_id': reply_to_message_id,
            'reply_markup': json.dumps(reply_markup) if reply_markup is not None else None,
            'message_thread_id': message_thread_id,
            'protect_content': protect_content,
            'foursquare_type': foursquare_type,
            'google_place_id': google_place_id,
            'google_place_type': google_place_type
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        if response and 'result' in response:
            return Message.from_dict(response['result'])
        return None

    def reply_contact(self, chat_id: Union[int, str] = None, phone_number: str = None,
                      first_name: str = None, last_name: str = None,
                      disable_notification: bool = None, reply_to_message_id: int = None,
                      reply_markup: Union[dict, Markup] = None, message_thread_id: int = None,
                      protect_content: bool = None, vcard: str = None) -> Optional[Message]:
        """Отправляет контакт"""
        method = 'sendContact'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif phone_number is None:
            raise ValueError("phone_number не должен быть None")
        elif first_name is None:
            raise ValueError("first_name не может быть None")
        
        params = {
            'chat_id': chat_id,
            'phone_number': phone_number,
            'first_name': first_name,
            'last_name': last_name,
            'disable_notification': disable_notification,
            'reply_to_message_id': reply_to_message_id,
            'reply_markup': json.dumps(reply_markup) if reply_markup is not None else None,
            'message_thread_id': message_thread_id,
            'protect_content': protect_content,
            'vcard': vcard
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        if response and 'result' in response:
            return Message.from_dict(response['result'])
        return None

    def reply_sticker(self, chat_id: Union[int, str] = None, sticker: Union[str, bytes] = None,
                      disable_notification: bool = None, reply_to_message_id: int = None,
                      reply_markup: Union[dict, Markup] = None, message_thread_id: int = None,
                      protect_content: bool = None, emoji: str = None) -> Optional[Message]:
        """Отправляет стикер"""
        method = 'sendSticker'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif sticker is None:
            raise ValueError("sticker не должен быть None")
        
        params = {
            'chat_id': chat_id,
            'disable_notification': disable_notification,
            'reply_to_message_id': reply_to_message_id,
            'reply_markup': json.dumps(reply_markup) if reply_markup is not None else None,
            'message_thread_id': message_thread_id,
            'protect_content': protect_content,
            'emoji': emoji
        }
        params = {k: v for k, v in params.items() if v is not None}
        
        files = None
        if isinstance(sticker, str):
            params['sticker'] = sticker
        else:
            files = {'sticker': sticker}
        
        response = self._make_request(method, params, files)
        if response and 'result' in response:
            return Message.from_dict(response['result'])
        return None

    def reply_dice(self, chat_id: Union[int, str] = None, emoji: str = None,
                   disable_notification: bool = None, reply_to_message_id: int = None,
                   reply_markup: Union[dict, Markup] = None, message_thread_id: int = None,
                   protect_content: bool = None) -> Optional[Message]:
        """Отправляет игральную кость"""
        method = 'sendDice'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif emoji is None:
            raise ValueError("emoji не должен быть None")
        
        params = {
            'chat_id': chat_id,
            'emoji': emoji,
            'disable_notification': disable_notification,
            'reply_to_message_id': reply_to_message_id,
            'reply_markup': json.dumps(reply_markup) if reply_markup is not None else None,
            'message_thread_id': message_thread_id,
            'protect_content': protect_content
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        return response and 'result' in response

    def reply_message_reaction(self, chat_id: Union[int, str] = None, message_id: int = None,
                               reaction: str = None, is_big: bool = False) -> bool:
        """Отправляет реакцию на сообщение"""
        method = 'setMessageReaction'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif message_id is None:
            raise ValueError("message_id не должен быть None")
        elif reaction is None:
            raise ValueError("reaction не должен быть None")
        
        params = {
            'chat_id': chat_id,
            'message_id': message_id,
            'reaction': [{'type': 'emoji', 'emoji': reaction}],
            'is_big': is_big
        }
        response = self._make_request(method, json_data=params)
        return response and 'result' in response

    def reply_invoice(self, chat_id: Union[int, str] = None, title: str = None,
                      description: str = None, payload: str = None, provider_token: str = None,
                      currency: str = None, prices: list = None, max_tip_amount: int = None,
                      suggested_tip_amounts: list = None, start_parameter: str = None,
                      provider_data: str = None, photo_url: str = None, photo_size: int = None,
                      photo_width: int = None, photo_height: int = None, need_name: bool = None,
                      need_phone_number: bool = None, need_email: bool = None,
                      need_shipping_address: bool = None, send_phone_number_to_provider: bool = None,
                      send_email_to_provider: bool = None, is_flexible: bool = None,
                      disable_notification: bool = None, reply_to_message_id: int = None,
                      reply_markup: Union[dict, Markup] = None, message_thread_id: int = None,
                      protect_content: bool = None) -> Optional[Message]:
        """Отправляет счет на оплату"""
        method = 'sendInvoice'
        if chat_id is None or title is None or description is None or payload is None or \
           provider_token is None or currency is None or prices is None:
            raise ValueError("Отсутствуют обязательные параметры для отправки инвойса")
        
        if prices and hasattr(prices[0], 'to_dict'):
            prices_serialized = json.dumps([price.to_dict() for price in prices])
        else:
            prices_serialized = json.dumps(prices)
        
        params = {
            'chat_id': chat_id,
            'title': title,
            'description': description,
            'payload': payload,
            'provider_token': provider_token,
            'currency': currency,
            'prices': prices_serialized,
            'max_tip_amount': max_tip_amount,
            'suggested_tip_amounts': json.dumps(suggested_tip_amounts) if suggested_tip_amounts is not None else None,
            'start_parameter': start_parameter,
            'provider_data': provider_data,
            'photo_url': photo_url,
            'photo_size': photo_size,
            'photo_width': photo_width,
            'photo_height': photo_height,
            'need_name': need_name,
            'need_phone_number': need_phone_number,
            'need_email': need_email,
            'need_shipping_address': need_shipping_address,
            'send_phone_number_to_provider': send_phone_number_to_provider,
            'send_email_to_provider': send_email_to_provider,
            'is_flexible': is_flexible,
            'disable_notification': disable_notification,
            'reply_to_message_id': reply_to_message_id,
            'reply_markup': json.dumps(reply_markup) if reply_markup is not None else None,
            'message_thread_id': message_thread_id,
            'protect_content': protect_content
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        if response and 'result' in response:
            return Message.from_dict(response['result'])
        return None

    def reply_shipping_query(self, shipping_query_id: str = None, ok: bool = None,
                             shipping_options: list = None, error_message: str = None) -> bool:
        """Отвечает на запрос доставки"""
        method = 'answerShippingQuery'
        if shipping_query_id is None or ok is None:
            raise ValueError("shipping_query_id и ok обязательны")
        
        if shipping_options and hasattr(shipping_options[0], 'to_dict'):
            shipping_options_serialized = json.dumps([option.to_dict() for option in shipping_options])
        else:
            shipping_options_serialized = json.dumps(shipping_options) if shipping_options is not None else None
        
        params = {
            'shipping_query_id': shipping_query_id,
            'ok': ok,
            'shipping_options': shipping_options_serialized,
            'error_message': error_message
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        return response and 'result' in response

    def reply_pre_checkout_query(self, pre_checkout_query_id: str = None, ok: bool = None,
                                  error_message: str = None) -> bool:
        """Отвечает на запрос предчекаута"""
        method = 'answerPreCheckoutQuery'
        if pre_checkout_query_id is None or ok is None:
            raise ValueError("pre_checkout_query_id и ok обязательны")
        
        params = {
            'pre_checkout_query_id': pre_checkout_query_id,
            'ok': ok,
            'error_message': error_message
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        return response and 'result' in response

    def reply_poll(self, chat_id: Union[int, str] = None, question: str = None, options: list = None,
                   is_anonymous: bool = False, type: str = 'regular', allows_multiple_answers: bool = False,
                   correct_option_id: int = None, explanation: str = None, mode: str = "Markdown",
                   open_period: int = None, close_date: int = None, is_closed: bool = False,
                   disable_notification: bool = None, reply_to_message_id: int = None,
                   reply_markup: Union[dict, Markup] = None, message_thread_id: int = None,
                   protect_content: bool = None, question_parse_mode: str = None,
                   question_entities: list = None) -> bool:
        """Отправляет опрос"""
        method = 'sendPoll'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif question is None:
            raise ValueError("question не должен быть None")
        elif options is None:
            raise ValueError("options не должен быть None")
        if not isinstance(options, list):
            raise ValueError("options должны быть списком")
        
        params = {
            'chat_id': chat_id,
            'question': question,
            'options': json.dumps(options),
            'is_anonymous': is_anonymous,
            'type': type,
            'allows_multiple_answers': allows_multiple_answers,
            'correct_option_id': correct_option_id,
            'explanation': explanation,
            'explanation_parse_mode': mode,
            'open_period': open_period,
            'close_date': close_date,
            'is_closed': is_closed,
            'disable_notification': disable_notification,
            'reply_to_message_id': reply_to_message_id,
            'reply_markup': json.dumps(reply_markup) if reply_markup is not None else None,
            'message_thread_id': message_thread_id,
            'protect_content': protect_content,
            'question_parse_mode': question_parse_mode,
            'question_entities': json.dumps(question_entities) if question_entities is not None else None
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        return response and 'result' in response

    def stop_poll(self, chat_id: Union[int, str] = None, message_id: int = None,
                  reply_markup: Union[dict, Markup] = None) -> bool:
        """Останавливает опрос"""
        method = 'stopPoll'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif message_id is None:
            raise ValueError("message_id не должен быть None")
        
        params = {
            'chat_id': chat_id,
            'message_id': message_id,
            'reply_markup': json.dumps(reply_markup) if reply_markup is not None else None
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        return response and 'result' in response

    def pin_message(self, chat_id: Union[int, str] = None, message_id: int = None,
                    disable_notification: bool = None) -> bool:
        """Закрепляет сообщение"""
        method = 'pinChatMessage'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif message_id is None:
            raise ValueError("message_id не должен быть None")
        
        params = {
            'chat_id': chat_id,
            'message_id': message_id,
            'disable_notification': disable_notification
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        return response and 'result' in response

    def unpin_message(self, chat_id: Union[int, str] = None, message_id: int = None) -> bool:
        """Открепляет сообщение"""
        method = 'unpinChatMessage'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif message_id is None:
            raise ValueError("message_id не должен быть None")
        
        params = {'chat_id': chat_id, 'message_id': message_id}
        response = self._make_request(method, params)
        return response and 'result' in response

    def forward_message(self, chat_id: Union[int, str] = None, from_chat_id: Union[int, str] = None,
                        message_id: int = None, disable_notification: bool = None,
                        protect_content: bool = None, message_thread_id: int = None) -> bool:
        """Пересылает сообщение"""
        method = 'forwardMessage'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif from_chat_id is None:
            raise ValueError("from_chat_id не должен быть None")
        elif message_id is None:
            raise ValueError("message_id не должен быть None")
        
        params = {
            'chat_id': chat_id,
            'from_chat_id': from_chat_id,
            'message_id': message_id,
            'disable_notification': disable_notification,
            'protect_content': protect_content,
            'message_thread_id': message_thread_id
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        return response and 'result' in response

    def forward_messages(self, chat_id: Union[int, str] = None, from_chat_id: Union[int, str] = None,
                         message_ids: Union[int, list] = None, disable_notification: bool = None,
                         protect_content: bool = None, message_thread_id: int = None) -> bool:
        """Пересылает несколько сообщений"""
        method = 'forwardMessages'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif from_chat_id is None:
            raise ValueError("from_chat_id не должен быть None")
        elif message_ids is None:
            raise ValueError("message_ids не должен быть None")
        
        params = {
            'chat_id': chat_id,
            'from_chat_id': from_chat_id,
            'message_ids': message_ids,
            'disable_notification': disable_notification,
            'protect_content': protect_content,
            'message_thread_id': message_thread_id
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        return response and 'result' in response

    def copy_message(self, chat_id: Union[int, str] = None, from_chat_id: Union[int, str] = None,
                     message_id: int = None, caption: str = None, disable_notification: bool = None,
                     mode: str = "Markdown", reply_markup: Union[dict, Markup] = None,
                     message_thread_id: int = None, protect_content: bool = None,
                     show_caption_above_media: bool = None) -> bool:
        """Копирует сообщение"""
        method = 'copyMessage'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif from_chat_id is None:
            raise ValueError("from_chat_id не должен быть None")
        elif message_id is None:
            raise ValueError("message_id не должен быть None")
        
        params = {
            'chat_id': chat_id,
            'from_chat_id': from_chat_id,
            'message_id': message_id,
            'caption': caption,
            'parse_mode': mode,
            'disable_notification': disable_notification,
            'reply_markup': json.dumps(reply_markup) if reply_markup is not None else None,
            'message_thread_id': message_thread_id,
            'protect_content': protect_content,
            'show_caption_above_media': show_caption_above_media
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        return response and 'result' in response

    def copy_messages(self, chat_id: Union[int, str] = None, from_chat_id: Union[int, str] = None,
                      message_ids: Union[int, list] = None, disable_notification: bool = None,
                      message_thread_id: int = None, protect_content: bool = None,
                      remove_caption: bool = None) -> bool:
        """Копирует несколько сообщений"""
        method = 'copyMessages'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif from_chat_id is None:
            raise ValueError("from_chat_id не должен быть None")
        elif message_ids is None:
            raise ValueError("message_ids не должен быть None")
        
        params = {
            'chat_id': chat_id,
            'from_chat_id': from_chat_id,
            'message_ids': message_ids,
            'disable_notification': disable_notification,
            'message_thread_id': message_thread_id,
            'protect_content': protect_content,
            'remove_caption': remove_caption
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        return response and 'result' in response

    def delete_message(self, chat_id: Union[int, str] = None, message_id: int = None) -> bool:
        """Удаляет сообщение"""
        method = 'deleteMessage'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif message_id is None:
            raise ValueError("message_id не должен быть None")
        
        params = {'chat_id': chat_id, 'message_id': message_id}
        response = self._make_request(method, params)
        return response and 'result' in response

    def delete_messages(self, chat_id: Union[int, str] = None, message_ids: Union[int, list] = None) -> bool:
        """Удаляет несколько сообщений"""
        method = 'deleteMessages'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        if message_ids is None:
            raise ValueError("message_ids не должен быть None")
        if isinstance(message_ids, int):
            message_ids = [message_ids]
        elif not isinstance(message_ids, list):
            raise ValueError("message_ids должен быть int или list")
        
        params = {
            'chat_id': chat_id,
            'message_ids': json.dumps(message_ids)
        }
        response = self._make_request(method, params)
        return response and 'result' in response

    def get_profile_photos(self, user_id: int = None, offset: int = None, limit: int = None) -> Optional[UserProfilePhotos]:
        """Получает фотографии профиля пользователя"""
        if user_id is None:
            raise ValueError("user_id не должен быть None")
        
        method_url = 'getUserProfilePhotos'
        params = {'user_id': user_id, 'offset': offset, 'limit': limit}
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method_url, params=params)
        if response and 'result' in response:
            return UserProfilePhotos.from_dict(response['result'])
        return None

    def get_me(self) -> Optional[User]:
        """Возвращает информацию о боте"""
        method = 'getMe'
        response = self._make_request(method)
        if 'result' in response:
            return User.from_dict(response['result'])
        return None

    def get_file(self, file_id: str = None) -> Optional[File]:
        """Получает информацию о файле"""
        method = 'getFile'
        if file_id is None:
            raise ValueError("file_id не может быть None")
        
        params = {'file_id': file_id}
        response = self._make_request(method, params)
        if response and 'result' in response:
            return File.from_dict(response['result'])
        return None

    def download_file(self, file: File = None, save_path: str = None, chunk_size: int = 1024,
                      timeout: int = 60, headers: dict = None, stream: bool = True) -> bool:
        """Скачивает файл с серверов Telegram"""
        if file is None:
            raise ValueError("file не должен быть None")
        elif not isinstance(file, File):
            raise ValueError("file должен быть объектом класса File")
        elif file.file_path is None:
            raise ValueError("file_path не должен быть None")
        elif save_path is None:
            raise ValueError("save_path не должен быть None")
        
        if not os.path.isdir(os.path.dirname(save_path)):
            os.makedirs(os.path.dirname(save_path))
        
        file_url = f"https://api.telegram.org/file/bot{self.token}/{file.file_path}"
        try:
            with requests.get(file_url, stream=stream, timeout=timeout, headers=headers) as response:
                if response.status_code == 200:
                    with open(save_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            f.write(chunk)
                    return True
                else:
                    print(f"Ошибка при скачивании файла: {response.json()}")
                    return False
        except requests.exceptions.RequestException as e:
            print(f"Произошла ошибка при скачивании файла: {e}")
            return False

    def edit_message_text(self, chat_id: Union[int, str] = None, message_id: int = None,
                          text: str = None, inline_message_id: str = None, mode: str = "Markdown",
                          reply_markup: Union[dict, Markup] = None, link_preview_options: dict = None) -> bool:
        """Редактирует текст сообщения"""
        method = 'editMessageText'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif message_id is None:
            raise ValueError("message_id не должен быть None")
        elif text is None:
            raise ValueError("text не должен быть None")
        
        params = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': mode,
            'inline_message_id': inline_message_id,
            'reply_markup': json.dumps(reply_markup) if reply_markup is not None else None,
            'link_preview_options': json.dumps(link_preview_options) if link_preview_options is not None else None
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        return response and 'result' in response

    def edit_message_caption(self, chat_id: Union[int, str] = None, message_id: int = None,
                             caption: str = None, inline_message_id: str = None, mode: str = "Markdown",
                             show_caption_above_media: bool = False, reply_markup: Union[dict, Markup] = None,
                             caption_entities: list = None) -> bool:
        """Редактирует подпись к медиа"""
        method = 'editMessageCaption'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif message_id is None:
            raise ValueError("message_id не должен быть None")
        elif caption is None:
            raise ValueError("caption не должен быть None")
        
        params = {
            'chat_id': chat_id,
            'message_id': message_id,
            'caption': caption,
            'parse_mode': mode,
            'inline_message_id': inline_message_id,
            'show_caption_above_media': show_caption_above_media,
            'reply_markup': json.dumps(reply_markup) if reply_markup is not None else None,
            'caption_entities': json.dumps(caption_entities) if caption_entities is not None else None
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        return response and 'result' in response

    def reply_media_group(self, chat_id: Union[int, str] = None, media: list = None,
                          disable_notification: bool = None, message_thread_id: int = None,
                          protect_content: bool = None) -> Optional[list]:
        """Отправляет группу медиа"""
        method = 'sendMediaGroup'
        files = {}
        
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif media is None or not isinstance(media, list) or len(media) == 0:
            raise ValueError("media должен быть непустым списком")
        elif len(media) > 10:
            raise ValueError("Нельзя отправлять более 10 объектов в одном сообщении")
        
        media_payload = []
        for i, item in enumerate(media):
            if isinstance(item, (InputMediaPhoto, InputMediaAnimation, InputMediaVideo,
                                 InputMediaAudio, InputMediaDocument)):
                media_payload.append(item.to_dict())
            elif isinstance(item, str):
                media_payload.append({'type': 'photo', 'media': item})
            elif isinstance(item, bytes):
                file_key = f"media{i}"
                media_payload.append({'type': 'photo', 'media': f'attach://{file_key}'})
                files[file_key] = item
            else:
                raise ValueError("Элемент media должен быть экземпляром str, bytes или одного из классов InputMedia")
        
        params = {
            'chat_id': chat_id,
            'media': json.dumps(media_payload),
            'disable_notification': disable_notification,
            'message_thread_id': message_thread_id,
            'protect_content': protect_content
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params, files=files if files else None)
        if response and 'result' in response:
            return [Message.from_dict(item) for item in response['result']]
        return None

    def edit_message_reply_markup(self, chat_id: Union[int, str] = None, message_id: int = None,
                                  reply_markup: Union[dict, Markup] = None, inline_message_id: str = None) -> bool:
        """Редактирует клавиатуру сообщения"""
        method = 'editMessageReplyMarkup'
        if chat_id is None:
            raise ValueError("chat_id не должен быть None")
        elif message_id is None:
            raise ValueError("message_id не должен быть None")
        elif reply_markup is None:
            raise ValueError("reply_markup не должен быть None")
        
        params = {
            'chat_id': chat_id,
            'message_id': message_id,
            'inline_message_id': inline_message_id,
            'reply_markup': json.dumps(reply_markup)
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        return response and 'result' in response

    def edit_message_live_location(self, chat_id: Union[int, str] = None, message_id: int = None,
                                   inline_message_id: str = None, latitude: float = None,
                                   longitude: float = None, horizontal_accuracy: float = None,
                                   heading: int = None, proximity_alert_radius: int = None,
                                   reply_markup: Union[dict, Markup] = None, live_period: int = None) -> Optional[Message]:
        """Редактирует живую локацию"""
        method = 'editMessageLiveLocation'
        if (chat_id is None and inline_message_id is None) or latitude is None or longitude is None:
            raise ValueError("Необходимы либо chat_id и message_id, либо inline_message_id, а также latitude и longitude")
        
        params = {
            'chat_id': chat_id,
            'message_id': message_id,
            'inline_message_id': inline_message_id,
            'latitude': latitude,
            'longitude': longitude,
            'horizontal_accuracy': horizontal_accuracy,
            'heading': heading,
            'proximity_alert_radius': proximity_alert_radius,
            'reply_markup': json.dumps(reply_markup) if reply_markup is not None else None,
            'live_period': live_period
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        if response and 'result' in response:
            return Message.from_dict(response['result'])
        return None

    def stop_message_live_location(self, chat_id: Union[int, str] = None, message_id: int = None,
                                   inline_message_id: str = None,
                                   reply_markup: Union[dict, Markup] = None) -> Optional[Message]:
        """Останавливает обновление живой локации"""
        method = 'stopMessageLiveLocation'
        if chat_id is None and inline_message_id is None:
            raise ValueError("Необходимы либо chat_id и message_id, либо inline_message_id")
        
        params = {
            'chat_id': chat_id,
            'message_id': message_id,
            'inline_message_id': inline_message_id,
            'reply_markup': json.dumps(reply_markup) if reply_markup is not None else None
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        if response and 'result' in response:
            return Message.from_dict(response['result'])
        return None

    def set_webhook(self, url: str = None, certificate: str = None, max_connections: int = None,
                    allowed_updates: Union[list, str] = None, ip_address: str = None,
                    drop_pending_updates: bool = None, secret_token: str = None) -> Optional[WebhookInfo]:
        """Устанавливает вебхук"""
        method = 'setWebhook'
        if url is None:
            raise ValueError("url не может быть None")
        
        params = {
            'url': url,
            'max_connections': max_connections,
            'allowed_updates': json.dumps(allowed_updates) if allowed_updates else None,
            'ip_address': ip_address,
            'drop_pending_updates': drop_pending_updates,
            'secret_token': secret_token
        }
        params = {k: v for k, v in params.items() if v is not None}
        files = {'certificate': certificate} if certificate else None
        response = self._make_request(method, params, files)
        if response and 'result' in response:
            return WebhookInfo.from_dict(response['result'])
        return None

    def get_webhook_info(self, timeout: int = 30, drop_pending_updates: bool = None) -> Optional[WebhookInfo]:
        """Получает информацию о вебхуке"""
        method = 'getWebhookInfo'
        params = {'timeout': timeout, 'drop_pending_updates': drop_pending_updates}
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params=params)
        if response and 'result' in response:
            return WebhookInfo.from_dict(response['result'])
        return None

    def delete_webhook(self, drop_pending_updates: bool = False) -> bool:
        """Удаляет вебхук"""
        method = 'deleteWebhook'
        params = {'drop_pending_updates': drop_pending_updates}
        response = self._make_request(method, params=params)
        return response and 'result' in response

    def get_updates(self, timeout: int = 45, allowed_updates: Union[list, str] = None,
                    long_polling_timeout: int = 45) -> list:
        """Получает обновления"""
        method = 'getUpdates'
        params = {
            'timeout': timeout,
            'allowed_updates': allowed_updates,
            'offset': self.update_offset,
            'long_polling_timeout': long_polling_timeout
        }
        params = {k: v for k, v in params.items() if v is not None}
        updates = self._make_request(method, params)
        if updates and 'result' in updates:
            return updates['result']
        return []

    def process_updates(self, updates: list = None):
        """Обрабатывает обновления"""
        if updates is None:
            raise ValueError("updates не должен быть None")
        
        for update in updates:
            if 'message' in update:
                self._handle_message(update['message'])
                self.update_offset = update['update_id'] + 1
            elif 'callback_query' in update:
                self._handle_callback_query(update['callback_query'])
                self.update_offset = update['update_id'] + 1

    def polling(self, interval: int = 1):
        """Запускает polling"""
        self.running = True
        while self.running:
            updates = self.get_updates()
            if updates:
                self.process_updates(updates)
            time.sleep(interval)

    def always_polling(self, interval: int = 1, timeout: int = 45, long_polling_timeout: int = 45,
                       allowed_updates: Union[list, str] = None, restart_on_error: bool = True):
        """Запускает бесконечный polling"""
        self.running = True
        while self.running:
            try:
                updates = self.get_updates(timeout=timeout, allowed_updates=allowed_updates,
                                           long_polling_timeout=long_polling_timeout)
                if updates:
                    self.process_updates(updates)
            except Exception as e:
                if not restart_on_error:
                    self.running = False
            time.sleep(interval)

    def stop_polling(self):
        """Останавливает polling"""
        self.running = False

    def get_chat(self, chat_id: Union[int, str] = None) -> Optional[Chat]:
        """Получает информацию о чате"""
        method = 'getChat'
        if chat_id is None:
            raise ValueError("chat_id не может быть None")
        
        params = {'chat_id': chat_id}
        response = self._make_request(method, params)
        if response and 'result' in response:
            return Chat.from_dict(response['result'])
        return None

    def get_chat_administrators(self, chat_id: Union[int, str] = None) -> list:
        """Получает администраторов чата"""
        method = 'getChatAdministrators'
        if chat_id is None:
            raise ValueError("chat_id не может быть None")
        
        params = {'chat_id': chat_id}
        response = self._make_request(method, params)
        if response and 'result' in response:
            return [ChatMember.from_dict(admin) for admin in response['result']]
        return []

    def get_chat_members_count(self, chat_id: Union[int, str] = None) -> int:
        """Получает количество участников чата"""
        method = 'getChatMemberCount'
        if chat_id is None:
            raise ValueError("chat_id не может быть None")
        
        params = {'chat_id': chat_id}
        response = self._make_request(method, params)
        if response and 'result' in response:
            return response['result']
        return 0

    def get_chat_member(self, chat_id: Union[int, str] = None, user_id: int = None) -> Optional[ChatMember]:
        """Получает информацию об участнике чата"""
        method = 'getChatMember'
        if chat_id is None:
            raise ValueError("chat_id не может быть None")
        elif user_id is None:
            raise ValueError("user_id не может быть None")
        
        params = {'chat_id': chat_id, 'user_id': user_id}
        response = self._make_request(method, params)
        if response and 'result' in response:
            return ChatMember.from_dict(response['result'])
        return None

    def set_chat_photo(self, chat_id: Union[int, str] = None, photo: Union[str, bytes, InputFile] = None) -> bool:
        """Устанавливает фото чата"""
        method = 'setChatPhoto'
        if chat_id is None:
            raise ValueError("chat_id не может быть None")
        elif photo is None:
            raise ValueError("photo не может быть None")
        
        params = {'chat_id': chat_id}
        files = None
        
        if isinstance(photo, InputFile):
            with open(photo.file_path, 'rb') as f:
                files = {'photo': f}
        elif isinstance(photo, str):
            if photo.startswith('http'):
                params['photo'] = photo
            else:
                with open(photo, 'rb') as f:
                    files = {'photo': f}
        else:
            raise ValueError("Неверный формат фото")
        
        response = self._make_request(method, params, files)
        return response and 'result' in response

    def delete_chat_photo(self, chat_id: Union[int, str] = None) -> bool:
        """Удаляет фото чата"""
        method = 'deleteChatPhoto'
        if chat_id is None:
            raise ValueError("chat_id не может быть None")
        
        params = {'chat_id': chat_id}
        response = self._make_request(method, params)
        return response and 'result' in response

    def set_chat_title(self, chat_id: Union[int, str] = None, title: str = None) -> bool:
        """Устанавливает название чата"""
        method = 'setChatTitle'
        if chat_id is None:
            raise ValueError("chat_id не может быть None")
        elif title is None:
            raise ValueError("title не может быть None")
        elif len(title) < 1 or len(title) > 128:
            raise ValueError("Название чата должно быть от 1 до 128 символов")
        
        params = {'chat_id': chat_id, 'title': title}
        response = self._make_request(method, params)
        return response and 'result' in response

    def set_chat_description(self, chat_id: Union[int, str] = None, description: str = None) -> bool:
        """Устанавливает описание чата"""
        method = 'setChatDescription'
        if chat_id is None:
            raise ValueError("chat_id не может быть None")
        elif description is None:
            raise ValueError("description не может быть None")
        elif len(description) < 0 or len(description) > 255:
            raise ValueError("Описание чата должно быть от 0 до 255 символов")
        
        params = {'chat_id': chat_id, 'description': description}
        response = self._make_request(method, params)
        return response and 'result' in response

    def leave_chat(self, chat_id: Union[int, str] = None) -> bool:
        """Покидает чат"""
        method = 'leaveChat'
        if chat_id is None:
            raise ValueError("chat_id не может быть None")
        
        params = {'chat_id': chat_id}
        response = self._make_request(method, params)
        return response and 'result' in response

    def kick_chat_member(self, chat_id: Union[int, str] = None, user_id: int = None,
                         until_date: float = None) -> bool:
        """Исключает пользователя из чата"""
        method = 'kickChatMember'
        if chat_id is None:
            raise ValueError("chat_id не может быть None")
        elif user_id is None:
            raise ValueError("user_id не может быть None")
        
        params = {
            'chat_id': chat_id,
            'user_id': user_id,
            'until_date': until_date if until_date else time.time()
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        return response and 'result' in response

    def ban_chat_member(self, chat_id: Union[int, str] = None, user_id: int = None,
                        until_date: float = None, revoke_messages: bool = False) -> bool:
        """Блокирует пользователя в чате"""
        method = 'banChatMember'
        if chat_id is None:
            raise ValueError("chat_id не может быть None")
        elif user_id is None:
            raise ValueError("user_id не может быть None")
        
        params = {
            'chat_id': chat_id,
            'user_id': user_id,
            'until_date': until_date if until_date else time.time(),
            'revoke_messages': revoke_messages
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        return response and 'result' in response

    def unban_chat_member(self, chat_id: Union[int, str] = None, user_id: int = None,
                          only_if_banned: bool = False) -> bool:
        """Разблокирует пользователя"""
        method = 'unbanChatMember'
        if chat_id is None:
            raise ValueError("chat_id не может быть None")
        elif user_id is None:
            raise ValueError("user_id не может быть None")
        
        params = {'chat_id': chat_id, 'user_id': user_id, 'only_if_banned': only_if_banned}
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        return response and 'result' in response

    def mute_user(self, chat_id: Union[int, str] = None, user_id: int = None, duration: int = 3600,
                  use_independent_chat_permissions: bool = None) -> bool:
        """Запрещает пользователю отправлять сообщения"""
        method = 'restrictChatMember'
        if chat_id is None:
            raise ValueError("chat_id не может быть None")
        elif user_id is None:
            raise ValueError("user_id не может быть None")
        
        permissions = ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_polls=False,
            can_send_other_messages=False)
        
        params = {
            'chat_id': chat_id,
            'user_id': user_id,
            'permissions': permissions.to_dict(),
            'use_independent_chat_permissions': use_independent_chat_permissions
        }
        if duration:
            params['until_date'] = time.time() + duration
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        return response and 'result' in response

    def unmute_user(self, chat_id: Union[int, str] = None, user_id: int = None,
                    use_independent_chat_permissions: bool = None) -> bool:
        """Разрешает пользователю отправлять сообщения"""
        method = 'restrictChatMember'
        if chat_id is None:
            raise ValueError("chat_id не может быть None")
        elif user_id is None:
            raise ValueError("user_id не может быть None")
        
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_polls=True,
            can_send_other_messages=True)
        
        params = {
            'chat_id': chat_id,
            'user_id': user_id,
            'permissions': permissions.to_dict(),
            'use_independent_chat_permissions': use_independent_chat_permissions
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        return response and 'result' in response

    def restrict_chat_member(self, chat_id: Union[int, str] = None, user_id: int = None,
                             permissions: ChatPermissions = None, until_date: float = None,
                             use_independent_chat_permissions: bool = None) -> bool:
        """Изменяет права пользователя"""
        method = 'restrictChatMember'
        if chat_id is None:
            raise ValueError("chat_id не может быть None")
        elif user_id is None:
            raise ValueError("user_id не может быть None")
        elif permissions is None:
            raise ValueError("permissions не может быть None")
        
        params = {
            'chat_id': chat_id,
            'user_id': user_id,
            'permissions': permissions.to_dict(),
            'until_date': until_date if until_date else time.time(),
            'use_independent_chat_permissions': use_independent_chat_permissions
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        return response and 'result' in response

    def promote_chat_member(self, chat_id: Union[int, str] = None, user_id: int = None,
                            can_change_info: bool = False, can_post_messages: bool = False,
                            can_edit_messages: bool = False, can_delete_messages: bool = False,
                            can_invite_users: bool = False, can_restrict_members: bool = False,
                            can_pin_messages: bool = False, can_promote_members: bool = False,
                            is_anonymous: bool = None, can_manage_chat: bool = None,
                            can_manage_video_chats: bool = None, can_post_stories: bool = None,
                            can_edit_stories: bool = None, can_delete_stories: bool = None) -> bool:
        """Повышает права пользователя"""
        method = 'promoteChatMember'
        if chat_id is None:
            raise ValueError("chat_id не может быть None")
        elif user_id is None:
            raise ValueError("user_id не может быть None")
        
        params = {
            'chat_id': chat_id,
            'user_id': user_id,
            'is_anonymous': is_anonymous,
            'can_manage_chat': can_manage_chat,
            'can_delete_messages': can_delete_messages,
            'can_manage_video_chats': can_manage_video_chats,
            'can_restrict_members': can_restrict_members,
            'can_promote_members': can_promote_members,
            'can_change_info': can_change_info,
            'can_invite_users': can_invite_users,
            'can_post_messages': can_post_messages,
            'can_edit_messages': can_edit_messages,
            'can_pin_messages': can_pin_messages,
            'can_post_stories': can_post_stories,
            'can_edit_stories': can_edit_stories,
            'can_delete_stories': can_delete_stories
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        return response and 'result' in response

    def set_chat_permissions(self, chat_id: Union[int, str] = None, permissions: ChatPermissions = None,
                             use_independent_chat_permissions: bool = None) -> bool:
        """Устанавливает права чата"""
        method = 'setChatPermissions'
        if chat_id is None:
            raise ValueError("chat_id не может быть None")
        elif permissions is None:
            raise ValueError("permissions не может быть None")
        
        params = {
            'chat_id': chat_id,
            'permissions': permissions.to_dict(),
            'use_independent_chat_permissions': use_independent_chat_permissions
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        return response and 'result' in response

    def chat_permissions(self, can_send_messages: bool = True, can_send_media_messages: bool = True,
                         can_send_polls: bool = True, can_send_other_messages: bool = True,
                         can_add_web_page_previews: bool = True, can_change_info: bool = False,
                         can_invite_users: bool = True, can_pin_messages: bool = False) -> dict:
        """Создает объект прав"""
        permissions = ChatPermissions(
            can_send_messages=can_send_messages,
            can_send_media_messages=can_send_media_messages,
            can_send_polls=can_send_polls,
            can_send_other_messages=can_send_other_messages,
            can_add_web_page_previews=can_add_web_page_previews,
            can_change_info=can_change_info,
            can_invite_users=can_invite_users,
            can_pin_messages=can_pin_messages)
        return permissions.to_dict()

    def message_handler(self, func: callable = None, commands: list = None, regexp: str = None,
                        content_types: list = None) -> callable:
        """Декоратор для регистрации обработчика сообщений"""
        def decorator(handler: callable) -> callable:
            self.handlers['message'].append({
                'function': handler,
                'func': func,
                'commands': commands,
                'regexp': re.compile(regexp) if regexp else None,
                'content_types': content_types
            })
            return handler
        return decorator

    def _handle_message(self, message_data: dict = None) -> None:
        """Обрабатывает сообщения"""
        if message_data is None:
            raise ValueError("message_data не может быть None")
        
        message = Message.from_dict(message_data)
        chat_id = message.chat.id
        
        if chat_id in self.next_steps and self.next_steps[chat_id]:
            step = self.next_steps[chat_id].pop(0)
            step['callback'](message, *step['args'], **step['kwargs'])
            if not self.next_steps[chat_id]:
                del self.next_steps[chat_id]
            return
        
        text = str(message.text)
        if text and text.startswith('/'):
            command_full = text.split()[0][1:]
            if '@' in command_full:
                parts = command_full.split('@', 1)
                command = parts[0].lower()
                target_username = parts[1].lower() if len(parts) > 1 else None
            else:
                command = command_full.lower()
                target_username = None
            
            chat_type = message.chat.type
            if (chat_type == 'private') or (chat_type in ['group', 'supergroup'] and target_username == self.bot_username):
                for handler in self.handlers['message']:
                    if handler['commands'] and command in handler['commands']:
                        if handler['func'] is None or handler['func'](message):
                            handler['function'](message)
                            return
        
        for handler in self.handlers['message']:
            if handler['regexp'] and handler['regexp'].search(text):
                if handler['func'] is None or handler['func'](message):
                    handler['function'](message)
                    return
        
        for handler in self.handlers['message']:
            if not handler['regexp'] and not handler['commands']:
                if handler['content_types']:
                    if message.content_type in handler['content_types']:
                        if handler['func'] is None or handler['func'](message):
                            handler['function'](message)
                            return
                else:
                    if handler['func'] is None or handler['func'](message):
                        handler['function'](message)
                        return

    def register_next_step_handler(self, message: Message = None, callback: callable = None,
                                    *args, **kwargs) -> None:
        """Регистрирует следующий обработчик"""
        if message is None:
            raise ValueError("message не может быть None")
        elif callback is None:
            raise ValueError("callback не может быть None")
        
        chat_id = message.chat.id
        if chat_id not in self.next_steps:
            self.next_steps[chat_id] = []
        self.next_steps[chat_id].append({'callback': callback, 'args': args, 'kwargs': kwargs})

    def callback_query_handler(self, func: callable = None, data: str = None) -> callable:
        """Декоратор для callback запросов"""
        def decorator(handler: callable) -> callable:
            self.handlers['callback_query'].append({
                'function': handler,
                'func': func,
                'data': data
            })
            return handler
        return decorator

    def _handle_callback_query(self, callback_query_data: dict = None) -> None:
        """Обрабатывает callback запросы"""
        if callback_query_data is None:
            raise ValueError("callback_query_data не может быть None")
        
        callback_query = CallbackQuery(callback_query_data)
        data = callback_query.data
        
        for handler in self.handlers['callback_query']:
            if handler['data'] is None or handler['data'] == data:
                if handler['func'] is None or handler['func'](callback_query):
                    handler['function'](callback_query)
                    break

    def answer_callback_query(self, callback_id: str = None, text: str = "Что-то забыли указать",
                              show_alert: bool = False, url: str = None, cache_time: int = 0) -> bool:
        """Отвечает на callback запрос"""
        method = 'answerCallbackQuery'
        if callback_id is None:
            raise ValueError("callback_id не должен быть None")
        
        params = {
            'callback_query_id': callback_id,
            'text': text,
            'show_alert': show_alert,
            'cache_time': cache_time
        }
        if url is not None:
            params['url'] = url
        
        response = self._make_request(method, params)
        return response and 'result' in response

    def inline_query_handler(self, func: callable = None, query: str = None) -> callable:
        """Декоратор для inline запросов"""
        def decorator(handler: callable) -> callable:
            self.handlers['inline_query'].append({
                'function': handler,
                'func': func,
                'query': query
            })
            return handler
        return decorator

    def _handle_inline_query(self, inline_query_data: dict = None) -> None:
        """Обрабатывает inline запросы"""
        if inline_query_data is None:
            raise ValueError("inline_query_data не может быть None")
        
        inline_query = InlineQuery.from_dict(inline_query_data)
        query_text = inline_query.query
        
        for handler in self.handlers.get('inline_query', []):
            if handler['query'] is None or handler['query'] in query_text:
                if handler['func'] is None or handler['func'](inline_query):
                    handler['function'](inline_query)
                    break

    def answer_inline_query(self, inline_query_id: str = None, results: list = None,
                            cache_time: int = None, is_personal: bool = None,
                            next_offset: str = None, switch_pm_text: str = None,
                            switch_pm_parameter: str = None, button: dict = None) -> bool:
        """Отвечает на inline запрос"""
        method = 'answerInlineQuery'
        if inline_query_id is None:
            raise ValueError("inline_query_id не должен быть None")
        if results is None or not isinstance(results, list):
            raise ValueError("results должен быть непустым списком")
        
        if results and hasattr(results[0], 'to_dict'):
            results_serialized = json.dumps([result.to_dict() for result in results])
        else:
            results_serialized = json.dumps(results)
        
        params = {
            'inline_query_id': inline_query_id,
            'results': results_serialized,
            'cache_time': cache_time,
            'is_personal': is_personal,
            'next_offset': next_offset,
            'switch_pm_text': switch_pm_text,
            'switch_pm_parameter': switch_pm_parameter,
            'button': json.dumps(button) if button is not None else None
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._make_request(method, params)
        return response and 'result' in response

    def run_in_bg(self, func, *args, **kwargs):
        """Запускает функцию в фоне"""
        def wrapper():
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(f"Error[{func}]: {e}")
        threading.Thread(target=wrapper, daemon=True).start()

    def encode_base64(self, path: str = None) -> str:
        """Кодирует файл в base64"""
        try:
            if path is None:
                raise ValueError("path must be provided and non-empty")
            with open(path, "rb") as file:
                return base64.b64encode(file.read()).decode('utf-8')
        except FileNotFoundError:
            return None


#Блок - Нейросети
class OnlySQ:
    def get_models(self, modality: str | list = None, can_tools: bool = None, can_stream: bool = None, status: str = None, max_cost: float = None, return_names: bool = False) -> list:
        '''
        Фильтрует модели по заданным параметрам
        Args:
            modality: Модальность ('text', 'image', 'sound') или список модальностей
            can_tools: Фильтр по поддержке инструментов
            can_stream: Фильтр по возможности потоковой передачи
            status: Статус модели (например, 'work')
            max_cost: Максимальная стоимость (включительно)
            return_names: Если True, возвращает названия моделей вместо ключей
        Returns:
            Список отфильтрованных моделей (ключи или названия)
        '''
        try:
            response = requests.get('https://api.onlysq.ru/ai/models')
            response.raise_for_status()
            data = response.json()
            filtered_models = []
            for model_key, model_data in data["models"].items():
                matches = True
                if modality is not None:
                    if isinstance(modality, list):
                        if model_data["modality"] not in modality:
                            matches = False
                    else:
                        if model_data["modality"] != modality:
                            matches = False
                if matches and can_tools is not None:
                    model_tools = model_data.get("can-tools", False)
                    if model_tools != can_tools:
                        matches = False
                if matches and can_stream is not None:
                    model_can_stream = model_data.get("can-stream", False)
                    if model_can_stream != can_stream:
                        matches = False
                if matches and status is not None:
                    model_status = model_data.get("status", "")
                    if model_status != status:
                        matches = False
                if matches and max_cost is not None:
                    model_cost = model_data.get("cost", float('inf'))
                    if float(model_cost) > max_cost:
                        matches = False
                if matches:
                    if return_names:
                        filtered_models.append(model_data["name"])
                    else:
                        filtered_models.append(model_key)
            return filtered_models 
        except Exception as e:
            print(f"OnlySQ(get_models): {e}")
            return []

    def generate_answer(self, model: str = "gpt-5.2-chat", messages: dict = None) -> str:
        '''Генерация ответа с использованием onlysq'''
        try:
            if messages is None:
                raise ValueError("Забыли указать messages")
            else:
                payload = {"model": model, "request": {"messages": messages}}
                response = requests.post("http://api.onlysq.ru/ai/v2", json=payload, headers={"Authorization":"Bearer openai"})
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"OnlySQ(generate_answer): {e}")
            return "Error"
    
    def generate_image(self, model: str = "flux", prompt: str = None, ratio: str = "16:9", filename: str = 'image.png') -> bool:
        '''Генерация фотографии с использованием onlysq'''
        try:
            if prompt is None:
                raise ValueError("Забыли указать prompt")
            else:
                payload = {"model": model, "prompt": prompt, "ratio": ratio}
                response = requests.post("https://api.onlysq.ru/ai/imagen", json=payload, headers={"Authorization":"Bearer openai"})
                if response.status_code == 200:
                    img_bytes = base64.b64decode(response.json()["files"][0])
                    with open(filename, 'wb') as f:
                        f.write(img_bytes)
                    return True
                else:
                    return False
        except Exception as e:
            print(f"OnlySQ(generate_image): {e}")
            return False


class Deef:
    def translate(self, text: str = None, lang: str = "en") -> str:
        '''Перевод текста'''
        try:
            if text is None:
                raise ValueError("Забыли указать text")
            base_url = f"https://translate.google.com/m?tl={lang}&sl=auto&q={text}"
            response = requests.get(base_url)
            soup = bs4.BeautifulSoup(response.text, "html.parser")
            translated_div = soup.find('div', class_='result-container')
            return translated_div.text
        except:
            return text

    def short_url(self, long_url: str = None) -> str:
        '''Сокращение ссылок'''
        try:
            response = requests.get(f'https://clck.ru/--?url={long_url}')
            response.raise_for_status()
            return response.text.strip()
        except:
            return long_url
    
    def gen_ai_response(self, model: str = "Qwen3 235B", messages: list = None) -> dict[str]:
        '''
        Отправляет запрос к API и возвращает словарь с полной информацией
        Args:
            model: Модель нейросети (Qwen3 235B или GPT OSS 120B)
            messages: Список сообщений в формате [{"role": "...", "content": "..."}]
        Returns:
            dict[str]: Словарь с ключами:
                - reasoning: Размышления модели
                - answer: Финальный ответ модели
                - status: Статус выполнения
                - cluster_info: Информация о кластере (если есть)
        '''
        try:
            if messages is None:
                raise ValueError("Забыли указать messages")
            else:
                model_to_cluster = {"Qwen3 235B": "hybrid", "GPT OSS 120B": "nvidia"}
                cluster_mode = model_to_cluster.get(model)
                if cluster_mode is None:
                    raise ValueError(f"Неизвестная модель: {model}\nДоступные модели: {list(model_to_cluster.keys())}")
                data = {"model": model, "clusterMode": cluster_mode, "messages": messages, "enableThinking": True}
                url = "https://chat.gradient.network/api/generate"
                response = requests.post(url, json=data, stream=True)
                result = {"reasoning": "", "answer": "", "status": "unknown", "cluster_info": None}
                for line in response.iter_lines():
                    if line:
                        try:
                            json_obj = json.loads(line.decode('utf-8'))
                            message_type = json_obj.get("type")
                            if message_type == "reply":
                                data_content = json_obj.get("data", {})
                                if "reasoningContent" in data_content:
                                    result["reasoning"] += data_content.get("reasoningContent", "")
                                if "content" in data_content:
                                    result["answer"] += data_content.get("content", "")
                            elif message_type == "jobInfo":
                                status = json_obj.get("data", {}).get("status")
                                result["status"] = status
                                if status == "completed":
                                    break
                            elif message_type == "clusterInfo":
                                result["cluster_info"] = json_obj.get("data", {})
                        except json.JSONDecodeError as e:
                            print(f"Ошибка декодирования JSON: {e}")
                            continue
                        except Exception as e:
                            print(f"Неожиданная ошибка: {e}")
                            continue
                return result
        except Exception as e:
            print(f"Deef(gen_ai_response): {e}")
            return {"reasoning": "Error", "answer": "Error", "status": "unknown", "cluster_info": None}
    
    def gen_gpt(self, messages: list = None) -> str:
        '''Генерация текста с помощью GPT-4o'''
        try:
            if messages is None:
                raise ValueError("Забыли указать messages")
            else:
                r = requests.post("https://italygpt.it/api/chat", json={"messages": messages, "stream": True}, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36", "Accept": "text/event-stream"})
                if r.status_code == 200:
                    return r.text
                else:
                    return "Error"
        except Exception as e:
            print(f"Deef(gen_gpt): {e}")
            return "Error"

    def speech(self, text: str = None, voice: str = "nova", path: str = "ozv.mp3") -> bool:
        '''Озвучивание текста'''
        try:
            if text is None:
                raise ValueError("`text` must be provided and non-empty.")
            if len(text) > 4096:
                raise ValueError("`text` length must not exceed 4096 characters.")
            if voice not in ["alloy", "ash", "ballad", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer", "verse"]:
                raise ValueError(f"Unsupported voice: {voice}. Supported: alloy, ash, ballad, coral, echo, fable, onyx, nova, sage, shimmer, verse")
            payload = {"input": text, "prompt": f"Voice: {voice}. Standard clear voice.", "voice": voice, "vibe": "null"}
            response = requests.post(
                url="https://www.openai.fm/api/generate",
                headers={
                    "accept": "*/*", "accept-encoding": "gzip, deflate, br, zstd",
                    "accept-language": "en-US,en;q=0.9,hi;q=0.8", "dnt": "1",
                    "origin": "https://www.openai.fm", "referer": "https://www.openai.fm/",
                    "user-agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")},
                data=payload,
                timeout=80)
            if response.status_code == 200:
                with open(path, "wb") as f:
                    f.write(response.content)
                return True
            else:
                return False
        except Exception as e:
            print(f"Deef(speech): {e}")
            return False


class ChatGPT:
    def __init__(self, url: str, headers: dict):
        self.url = url.rstrip("/")
        self.headers = headers

    def _make_request(self, method: str, endpoint: str, data: dict = None, files: dict = None) -> Union[dict, list]:
        try:
            url = f"{self.url}/{endpoint.lstrip('/')}"
            if files:
                response = requests.request(method=method, url=url, headers=self.headers, files=files, data=data)
            else:
                response = requests.request(method=method, url=url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"ChatGPT({endpoint}): {e}")
            return "Error"

    def generate_chat_completion(self, model: str, messages: list, temperature: float = None, max_tokens: int = None, stream: bool = False, **kwargs) -> Union[dict, list]:
        data = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens, "stream": stream, **kwargs}
        return self._make_request("POST", "chat/completions", data=data)

    def generate_image(self, prompt: str, n: int = 1, size: str = "1024x1024", response_format: str = "url", **kwargs) -> dict:
        data = {"prompt": prompt, "n": n, "size": size, "response_format": response_format, **kwargs}
        return self._make_request("POST", "images/generations", data=data)

    def generate_embedding(self, model: str, input_i: Union[str, list], user: str = None, **kwargs) -> dict:
        data = {"model": model, "input": input_i, "user": user, **kwargs}
        return self._make_request("POST", "embeddings", data=data)

    def generate_transcription(self, file: BinaryIO, model: str, language: str = None, prompt: str = None, response_format: str = "json", temperature: float = 0, **kwargs) -> Union[dict, str]:
        data = {"model": model, "language": language, "prompt": prompt, "response_format": response_format, "temperature": temperature, **kwargs}
        files = {"file": file}
        return self._make_request("POST", "audio/transcriptions", data=data, files=files)

    def generate_translation(self, file: BinaryIO, model: str, prompt: str = None, response_format: str = "json", temperature: float = 0, **kwargs) -> Union[dict, str]:
        data = {"model": model, "prompt": prompt, "response_format": response_format, "temperature": temperature, **kwargs}
        files = {"file": file}
        return self._make_request("POST", "audio/translations", data=data, files=files)
    
    def get_models(self):
        return self._make_request("GET", "models")