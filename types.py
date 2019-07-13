"""PytSite Telegram Bot Types
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from typing import Optional, Union, Type
from abc import ABC, abstractmethod
from datetime import datetime


class JSONable(ABC):
    @abstractmethod
    def as_jsonable(self):
        pass


class TelegramType:
    def __init__(self, data=None):
        self._data = data

    def __str__(self) -> str:
        return '{}: {}'.format(self.__class__.__name__, self._data)


class NotImplementedType:
    def __init__(self, *args, **kwargs):
        raise RuntimeError('{} is not implemented yet'.format(self.__class__.__name__))


class Array(TelegramType):
    def __init__(self, data: Union[list, dict], item_type: Type):
        if not isinstance(data, (list, tuple)):
            raise TypeError('{} expects list or tuple, got {}: {}'.format(self.__class__.__name__, type(data), data))

        super().__init__(data)
        self._items = [item_type(item) for item in data]

    def __getitem__(self, index: int):
        return self._items[index]


class File(TelegramType):
    def __init__(self, data: dict):
        super().__init__(data)

        self._file_id = data['file_id']  # type: str
        self._file_size = data['file_size']  # type: Optional[int]
        self._file_path = data['file_path']  # type: Optional[str]

    @property
    def file_id(self) -> str:
        return self._file_id

    @property
    def file_size(self) -> Optional[int]:
        return self._file_size

    @property
    def file_path(self) -> Optional[str]:
        return self._file_path


class PhotoSize(TelegramType):
    def __init__(self, data: dict):
        super().__init__(data)

        self._file_id = data['file_id']  # type: str
        self._width = data['width']  # type: int
        self._height = data['height']  # type: int
        self._file_size = data.get('file_size')  # type: Optional[int]

    @property
    def file_id(self) -> str:
        return self._file_id

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def file_size(self) -> Optional[int]:
        return self._file_size


class PhotoSizeArray(Array):
    def __init__(self, data: Union[list, tuple]):
        super().__init__(data, PhotoSize)


class User(TelegramType):
    def __init__(self, data: dict):
        super().__init__(data)

        try:
            self._id = data['id']  # type: int
            self._is_bot = data['is_bot']  # type: bool
            self._first_name = data['first_name']  # type: str
            self._last_name = data.get('last_name')  # type: Optional[str]
            self._username = data.get('username')  # type: Optional[str]
            self._language_code = data.get('language_code')  # type: Optional[str]

        except KeyError as e:
            raise KeyError("Key '{}' is not found in data set: {}".format(e, data))

    @property
    def id(self) -> int:
        return self._id

    @property
    def is_bot(self) -> bool:
        return self._is_bot

    @property
    def first_name(self) -> str:
        return self._first_name

    @property
    def last_name(self) -> Optional[str]:
        return self._last_name

    @property
    def username(self) -> Optional[str]:
        return self._username

    @property
    def language_code(self) -> Optional[str]:
        return self._language_code


class UserArray(Array):
    def __init__(self, data: Union[list, dict]):
        super().__init__(data, User)


class Location(TelegramType):
    def __init__(self, data: dict):
        super().__init__(data)

        self._longitude = data['longitude']  # type: float
        self._latitude = data['latitude']  # type: float

    @property
    def longitude(self) -> float:
        return self._longitude

    @property
    def latitude(self) -> float:
        return self._latitude


class InlineQuery(TelegramType):
    def __init__(self, data: dict):
        super().__init__(data)

        self._id = data['id']  # type: str
        self._from = User(data['from'])
        self._location = Location(data['location']) if 'location' in data else None
        self._query = data['query']  # type: str
        self._offset = data['offset']  # type: str

    @property
    def id(self) -> str:
        return self._id

    @property
    def sender(self) -> Optional[User]:
        return self._from

    @property
    def location(self) -> Optional[Location]:
        return self._location

    @property
    def query(self) -> str:
        return self._query

    @property
    def offset(self) -> str:
        return self._offset


class ChosenInlineResult(TelegramType):
    def __init__(self, data: dict):
        super().__init__(data)

        self._result_id = data['result_id']  # type: str
        self._from = User(data['from'])
        self._location = Location(data['location']) if 'location' in data else None
        self._inline_message_id = data['inline_message_id']  # type: str
        self._query = data['query']  # type: str

    @property
    def result_id(self) -> str:
        return self._result_id

    @property
    def sender(self) -> Optional[User]:
        return self._from

    @property
    def location(self) -> Optional[Location]:
        return self._location

    @property
    def inline_message_id(self) -> str:
        return self._inline_message_id

    @property
    def query(self) -> str:
        return self._query


class CallbackGame(NotImplementedType, JSONable):
    pass


class ShippingAddress(TelegramType):
    def __init__(self, data):
        super().__init__(data)

        self._country_code = data['country_code']
        self._state = data['state']
        self._city = data['city']
        self._street_line1 = data['street_line1']
        self._street_line2 = data['street_line2']
        self._post_code = data['post_code']

    @property
    def country_code(self) -> str:
        return self._country_code

    @property
    def state(self) -> str:
        return self._state

    @property
    def city(self) -> str:
        return self._city

    @property
    def street_line1(self) -> str:
        return self._street_line1

    @property
    def street_line2(self) -> str:
        return self._street_line2

    @property
    def post_code(self) -> str:
        return self._post_code


class ShippingQuery(TelegramType):
    def __init__(self, data):
        super().__init__(data)

        self._id = data['id']  # type: str
        self._from = User(data['from'])
        self._invoice_payload = data['invoice_payload']  # type: str
        self._shipping_address = ShippingAddress(data['shipping_address'])

    @property
    def id(self) -> str:
        return self._id

    @property
    def sender(self) -> User:
        return self._from

    @property
    def invoice_payload(self) -> str:
        return self._invoice_payload

    @property
    def shipping_address(self) -> ShippingAddress:
        return self._shipping_address


class OrderInfo(TelegramType):
    def __init__(self, data):
        super().__init__(data)

        self._name = data.get('name')  # type: Optional['str']
        self._phone_number = data.get('phone_number')  # type: Optional['str']
        self._email = data.get('email')  # type: Optional['str']
        self._shipping_address = ShippingAddress(data['shipping_address']) if 'shipping_address' in data else None

    def name(self) -> Optional[str]:
        return self._name

    def phone_number(self) -> Optional[str]:
        return self._phone_number

    def email(self) -> Optional[str]:
        return self._email

    def shipping_address(self) -> Optional[ShippingAddress]:
        return self._shipping_address


class PreCheckoutQuery(TelegramType):
    def __init__(self, data):
        super().__init__(data)

        self._id = data['id']  # type: str
        self._from = User(data['from'])
        self._currency = data['currency']  # type: str
        self._total_amount = data['total_amount']  # type: int
        self._invoice_payload = data['invoice_payload']  # type: str
        self._shipping_option_id = data.get('shipping_option_id')  # type: Optional[str]
        self._order_info = OrderInfo(data['order_info']) if 'order_info' in data else None

    @property
    def id(self) -> str:
        return self._id

    @property
    def sender(self) -> User:
        return self._from

    @property
    def currency(self) -> str:
        return self._currency

    @property
    def total_amount(self) -> int:
        return self._total_amount

    @property
    def invoice_payload(self) -> str:
        return self._invoice_payload

    @property
    def shipping_option_id(self) -> str:
        return self._shipping_option_id

    @property
    def order_info(self) -> Optional[OrderInfo]:
        return self._order_info


class ChatPhoto(TelegramType):
    def __init__(self, data: dict):
        super().__init__(data)

        self._small_file_id = data['small_file_id']  # type: str
        self._big_file_id = data['big_file_id']  # type: str

    @property
    def small_file_id(self) -> str:
        return self._small_file_id

    @property
    def big_file_id(self) -> str:
        return self._big_file_id


class Document(TelegramType):
    def __init__(self, data: dict):
        super().__init__(data)

        self._file_id = data['file_id']  # type: str
        self._thumb = PhotoSize(data['thumb']) if 'thumb' in data else None
        self._file_name = data.get('file_name')  # type: Optional[str]
        self._mime_type = data.get('mime_type')  # type: Optional[str]
        self._file_size = data.get('file_size')  # type: Optional[int]

    @property
    def file_id(self) -> str:
        return self._file_id

    @property
    def thumb(self) -> Optional[PhotoSize]:
        return self._thumb

    @property
    def file_name(self) -> Optional[str]:
        return self._file_name

    @property
    def mime_type(self) -> Optional[str]:
        return self._mime_type

    @property
    def file_size(self) -> Optional[int]:
        return self._file_size


class Game(NotImplementedType):
    pass


class MaskPosition(TelegramType):
    def __init__(self, data: dict):
        super().__init__(data)

        self._point = data['point']  # type: str
        self._x_shift = data['x_shift']  # type: float
        self._y_shift = data['y_shift']  # type: float
        self._scale = data['scale']  # type: float

    @property
    def point(self) -> str:
        return self._point

    @property
    def x_shift(self) -> float:
        return self._x_shift

    @property
    def y_shift(self) -> float:
        return self._y_shift

    @property
    def scale(self) -> float:
        return self._scale


class Sticker(TelegramType):
    def __init__(self, data: dict):
        super().__init__(data)

        self._file_id = data['file_id']  # type: str
        self._width = data['width']  # type: int
        self._height = data['height']  # type: int
        self._thumb = PhotoSize(data['thumb']) if 'thumb' in data else None
        self._emoji = data.get('emoji')  # type: Optional[str]
        self._set_name = data.get('set_name')  # type: Optional[str]
        self._mask_position = MaskPosition(data['mask_position']) if 'mask_position' in data else None
        self._file_size = data.get('file_size')  # type: Optional[int]

    @property
    def file_id(self) -> str:
        return self._file_id

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def thumb(self) -> Optional[PhotoSize]:
        return self._thumb

    @property
    def emoji(self) -> Optional[str]:
        return self._emoji

    @property
    def set_name(self) -> Optional[str]:
        return self._set_name

    @property
    def mask_position(self) -> Optional[MaskPosition]:
        return self._mask_position

    @property
    def file_size(self) -> Optional[int]:
        return self._file_size


class VideoNote(TelegramType):
    def __init__(self, data: dict):
        super().__init__(data)

        self._file_id = data['file_id']  # type: str
        self._length = data['length']  # type: int
        self._duration = data['duration']  # type: int
        self._thumb = PhotoSize(data['thumb']) if 'thumb' in data else None
        self._file_size = data.get('file_size')  # type: Optional[int]

    @property
    def file_id(self) -> str:
        return self._file_id

    @property
    def length(self) -> int:
        return self._length

    @property
    def duration(self) -> int:
        return self._duration

    @property
    def thumb(self) -> Optional[PhotoSize]:
        return self._thumb

    @property
    def file_size(self) -> Optional[int]:
        return self._file_size


class Video(TelegramType):
    def __init__(self, data: dict):
        super().__init__(data)

        self._file_id = data['file_id']  # type: str
        self._width = data['width']  # type: int
        self._height = data['height']  # type: int
        self._duration = data['duration']  # type: int
        self._thumb = PhotoSize(data['thumb']) if 'thumb' in data else None
        self._mime_type = data.get('mime_type')  # type: Optional[str]
        self._file_size = data.get('file_size')  # type: Optional[int]

    @property
    def file_id(self) -> str:
        return self._file_id

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def duration(self) -> int:
        return self._duration

    @property
    def thumb(self) -> Optional[PhotoSize]:
        return self._thumb

    @property
    def mime_type(self) -> Optional[str]:
        return self._mime_type

    @property
    def file_size(self) -> Optional[int]:
        return self._file_size


class Audio(TelegramType):
    def __init__(self, data: dict):
        super().__init__(data)

        self._file_id = data['file_id']  # type: str
        self._duration = data['duration']  # type: int
        self._performer = data.get('performer')  # type: Optional[str]
        self._title = data.get('title')  # type: Optional[str]
        self._mime_type = data.get('mime_type')  # type: Optional[str]
        self._file_size = data.get('file_size')  # type: Optional[int]

    @property
    def file_id(self) -> str:
        return self._file_id

    @property
    def duration(self) -> int:
        return self._duration

    @property
    def performer(self) -> Optional[str]:
        return self._performer

    @property
    def title(self) -> Optional[str]:
        return self._title

    @property
    def mime_type(self) -> Optional[str]:
        return self._mime_type

    @property
    def file_size(self) -> Optional[int]:
        return self._file_size


class Voice(TelegramType):
    def __init__(self, data: dict):
        super().__init__(data)

        self._file_id = data['file_id']  # type: str
        self._duration = data['duration']  # type: int
        self._mime_type = data.get('mime_type')  # type: Optional[str]
        self._file_size = data.get('file_size')  # type: Optional[int]

    @property
    def file_id(self) -> str:
        return self._file_id

    @property
    def duration(self) -> int:
        return self._duration

    @property
    def mime_type(self) -> Optional[str]:
        return self._mime_type

    @property
    def file_size(self) -> Optional[int]:
        return self._file_size


class Contact(NotImplementedType):
    pass


class Venue(TelegramType):
    def __init__(self, data: dict):
        super().__init__(data)

        self._location = Location(data['location'])
        self._title = data['title']  # type: str
        self._address = data['address']  # type: str
        self._foursquare_id = data['foursquare_id']  # type: Optional[str]

    @property
    def location(self) -> Location:
        return self._location

    @property
    def title(self) -> str:
        return self._title

    @property
    def address(self) -> str:
        return self._address

    @property
    def foursquare_id(self) -> str:
        return self._foursquare_id


class Invoice(NotImplementedType):
    pass


class SuccessfulPayment(NotImplementedType):
    pass


class MessageEntity(TelegramType):
    def __init__(self, data: dict):
        super().__init__(data)

        self._type = data['type']  # type: str
        self._offset = data['offset']  # type: int
        self._length = data['length']  # type: int
        self._url = data.get('url')  # type: Optional[str]
        self._user = User(data) if 'user' in data else None

    @property
    def type(self) -> str:
        return self._type

    @property
    def offset(self) -> int:
        return self._offset

    @property
    def length(self) -> int:
        return self._length

    @property
    def url(self) -> Optional[str]:
        return self._url

    @property
    def user(self) -> Optional[User]:
        return self._user


class MessageEntityArray(Array):
    def __init__(self, data: Union[list, tuple]):
        super().__init__(data, MessageEntity)


class Chat(TelegramType):
    def __init__(self, data: dict):
        super().__init__(data)

        self._id = data['id']  # type: int
        self._type = data['type']  # type: str
        self._title = data.get('title')  # type: Optional[str]
        self._username = data.get('username')  # type: Optional[str]
        self._first_name = data.get('first_name')  # type: Optional[str]
        self._last_name = data.get('last_name')  # type: Optional[str]
        self._all_members_are_administrators = data.get('all_members_are_administrators')  # type: Optional[bool]
        self._photo = ChatPhoto(data['photo']) if 'photo' in data else None
        self._description = data.get('description')  # type: Optional[str]
        self._invite_link = data.get('invite_link')  # type: Optional[str]
        self._pinned_message = data.get('pinned_message')  # type: Optional[Message]
        self._sticker_set_name = data.get('sticker_set_name')  # type: Optional[str]
        self._can_set_sticker_set = data.get('can_set_sticker_set')  # type: Optional[bool]

    @property
    def id(self) -> int:
        return self._id

    @property
    def type(self) -> str:
        return self._type

    @property
    def title(self) -> Optional[str]:
        return self._title

    @property
    def username(self) -> Optional[str]:
        return self._username

    @property
    def first_name(self) -> Optional[str]:
        return self._first_name

    @property
    def last_name(self) -> Optional[str]:
        return self._last_name

    @property
    def all_members_are_administrators(self) -> Optional[bool]:
        return self._all_members_are_administrators

    @property
    def photo(self) -> Optional[ChatPhoto]:
        return self._photo

    @property
    def description(self) -> Optional[str]:
        return self._description

    @property
    def invite_link(self) -> Optional[str]:
        return self._invite_link

    @property
    def pinned_message(self):
        """
        :rtype: Optional[Message]
        """
        return self._pinned_message

    @property
    def sticker_set_name(self) -> Optional[str]:
        return self._sticker_set_name

    @property
    def can_set_sticker_set(self) -> Optional[bool]:
        return self._can_set_sticker_set


class ChatMember(TelegramType):
    def __init__(self, data: dict):
        super().__init__(data)

        self._user = User(data['user'])
        self._status = data['status']  # type: str
        self._until_date = datetime.fromtimestamp(data['until_date']) if 'until_date' in data else None
        self._can_be_edited = data.get('can_be_edited')  # type: Optional[bool]
        self._can_change_info = data.get('can_change_info')  # type: Optional[bool]
        self._can_post_messages = data.get('can_post_messages')  # type: Optional[bool]
        self._can_edit_messages = data.get('can_edit_messages')  # type: Optional[bool]
        self._can_delete_messages = data.get('can_delete_messages')  # type: Optional[bool]
        self._can_invite_users = data.get('can_invite_users')  # type: Optional[bool]
        self._can_restrict_members = data.get('can_restrict_members')  # type: Optional[bool]
        self._can_pin_messages = data.get('can_pin_messages')  # type: Optional[bool]
        self._can_promote_members = data.get('can_promote_members')  # type: Optional[bool]
        self._can_send_messages = data.get('can_send_messages')  # type: Optional[bool]
        self._can_send_media_messages = data.get('can_send_media_messages')  # type: Optional[bool]
        self._can_send_other_messages = data.get('can_send_other_messages')  # type: Optional[bool]
        self._can_add_web_page_previews = data.get('can_add_web_page_previews')  # type: Optional[bool]

    @property
    def user(self) -> User:
        return self._user

    @property
    def status(self) -> str:
        return self._status

    @property
    def until_date(self) -> Optional[datetime]:
        return self._until_date

    @property
    def can_be_edited(self) -> bool:
        return self._can_be_edited

    @property
    def can_change_info(self) -> bool:
        return self._can_change_info

    @property
    def can_post_messages(self) -> bool:
        return self._can_post_messages

    @property
    def can_edit_messages(self) -> bool:
        return self._can_edit_messages

    @property
    def can_delete_messages(self) -> bool:
        return self._can_delete_messages

    @property
    def can_invite_users(self) -> bool:
        return self._can_invite_users

    @property
    def can_restrict_members(self) -> bool:
        return self._can_restrict_members

    @property
    def can_pin_messages(self) -> bool:
        return self._can_pin_messages

    @property
    def can_promote_members(self) -> bool:
        return self._can_promote_members

    @property
    def can_send_messages(self) -> bool:
        return self._can_send_messages

    @property
    def can_send_media_messages(self) -> bool:
        return self._can_send_media_messages

    @property
    def can_send_other_messages(self) -> bool:
        return self._can_send_other_messages

    @property
    def can_add_web_page_previews(self) -> bool:
        return self._can_add_web_page_previews


class ChatMemberArray(Array):
    def __init__(self, data: Union[list, tuple]):
        super().__init__(data, ChatMember)


class Message(TelegramType):
    """Telegram Update Object

    https://core.telegram.org/bots/api#message
    """

    def __init__(self, data: dict):
        super().__init__(data)

        self._message_id = data['message_id']  # type: int
        self._from = User(data['from']) if 'from' in data else None
        self._date = datetime.fromtimestamp(data['date']) if 'date' in data else None
        self._chat = Chat(data['chat'])
        self._forward_from = User(data['forward_from']) if 'forward_from' in data else None
        self._forward_from_chat = Chat(data['forward_from_chat']) if 'forward_from_chat' in data else None
        self._forward_from_message_id = data.get('forward_from_message_id')  # type: Optional[int]
        self._forward_signature = data.get('forward_signature')  # type: Optional[str]
        self._forward_date = datetime.fromtimestamp(data['forward_date']) if 'forward_date' in data else None
        self._reply_to_message = Message(data['reply_to_message']) if 'reply_to_message' in data else None
        self._edit_date = datetime.fromtimestamp(data['edit_date']) if 'edit_date' in data else None
        self._media_group_id = data.get('media_group_id')  # type: str
        self._author_signature = data.get('author_signature')  # type: str
        self._text = data.get('text')  # type: Optional[str]
        self._entities = MessageEntityArray(data['entities']) if 'entities' in data else None
        self._caption_entities = MessageEntityArray(
            data['caption_entities']) if 'caption_entities' in data else None
        self._audio = Audio(data['audio']) if 'audio' in data else None
        self._document = Document(data['document']) if 'document' in data else None
        self._game = Game(data['game']) if 'game' in data else None
        self._photo = PhotoSizeArray(data['photo']) if 'photo' in data else None
        self._sticker = Sticker(data['sticker']) if 'sticker' in data else None
        self._video = Video(data['video']) if 'video' in data else None
        self._voice = Voice(data['voice']) if 'voice' in data else None
        self._video_note = VideoNote(data['video_note']) if 'video_note' in data else None
        self._caption = data.get('caption')  # type: Optional[str]
        self._contact = Voice(data['contact']) if 'contact' in data else None
        self._location = Location(data['location']) if 'location' in data else None
        self._venue = Location(data['venue']) if 'venue' in data else None
        self._new_chat_members = UserArray(data['new_chat_members']) if 'new_chat_members' in data else None
        self._left_chat_member = User(data['left_chat_member']) if 'left_chat_member' in data else None
        self._new_chat_title = data.get('new_chat_title')  # type: Optional[str]
        self._new_chat_photo = PhotoSizeArray(data['new_chat_photo']) if 'new_chat_photo' in data else None
        self._delete_chat_photo = data.get('delete_chat_photo')  # type: Optional[bool]
        self._group_chat_created = data.get('group_chat_created')  # type: Optional[bool]
        self._supergroup_chat_created = data.get('supergroup_chat_created')  # type: Optional[bool]
        self._channel_chat_created = data.get('channel_chat_created')  # type: Optional[bool]
        self._migrate_to_chat_id = data.get('migrate_to_chat_id')  # type: Optional[int]
        self._migrate_from_chat_id = data.get('migrate_from_chat_id')  # type: Optional[int]
        self._pinned_message = Message(data['pinned_message']) if 'pinned_message' in data else None
        self._invoice = Invoice(data['invoice']) if 'invoice' in data else None
        self._successful_payment = SuccessfulPayment(
            data['successful_payment']) if 'successful_payment' in data else None

    @property
    def message_id(self) -> int:
        return self._message_id

    @property
    def sender(self) -> Optional[User]:
        return self._from

    @property
    def date(self) -> datetime:
        return self._date

    @property
    def chat(self) -> Chat:
        return self._chat

    @property
    def forward_from(self) -> Optional[User]:
        return self._forward_from

    @property
    def forward_from_chat(self) -> Optional[Chat]:
        return self._forward_from_chat

    @property
    def forward_from_message_id(self) -> Optional[int]:
        return self._forward_from_message_id

    @property
    def forward_signature(self) -> Optional[str]:
        return self._forward_signature

    @property
    def forward_date(self) -> Optional[datetime]:
        return self._forward_date

    @property
    def reply_to_message(self):
        """
        :rtype: Optional[Message]
        """
        return self._reply_to_message

    @property
    def edit_date(self) -> Optional[datetime]:
        return self._edit_date

    @property
    def media_group_id(self) -> Optional[str]:
        return self._media_group_id

    @property
    def author_signature(self) -> Optional[str]:
        return self._author_signature

    @property
    def text(self) -> Optional[str]:
        return self._text

    @property
    def entities(self) -> Optional[MessageEntityArray]:
        return self._entities

    @property
    def caption_entities(self) -> Optional[MessageEntityArray]:
        return self._caption_entities

    @property
    def audio(self) -> Optional[Audio]:
        return self._audio

    @property
    def document(self) -> Optional[Document]:
        return self._document

    @property
    def game(self) -> Optional[Game]:
        return self._game

    @property
    def photo(self) -> Optional[PhotoSizeArray]:
        return self._photo

    @property
    def sticker(self) -> Optional[Sticker]:
        return self._sticker

    @property
    def video(self) -> Optional[Video]:
        return self._video

    @property
    def voice(self) -> Optional[Voice]:
        return self._voice

    @property
    def video_note(self) -> Optional[VideoNote]:
        return self._video_note

    @property
    def caption(self) -> Optional[str]:
        return self._caption

    @property
    def contact(self) -> Optional[Contact]:
        return self._contact

    @property
    def location(self) -> Optional[Location]:
        return self._location

    @property
    def venue(self) -> Optional[Venue]:
        return self._venue

    @property
    def new_chat_members(self) -> Optional[UserArray]:
        return self._new_chat_members

    @property
    def left_chat_member(self) -> Optional[User]:
        return self._left_chat_member

    @property
    def new_chat_title(self) -> Optional[str]:
        return self._new_chat_title

    @property
    def new_chat_photo(self) -> Optional[PhotoSizeArray]:
        return self._new_chat_photo

    @property
    def delete_chat_photo(self) -> Optional[bool]:
        return self._delete_chat_photo

    @property
    def group_chat_created(self) -> Optional[bool]:
        return self._group_chat_created

    @property
    def supergroup_chat_created(self) -> Optional[bool]:
        return self._supergroup_chat_created

    @property
    def channel_chat_created(self) -> Optional[bool]:
        return self._channel_chat_created

    @property
    def migrate_to_chat_id(self) -> Optional[int]:
        return self._migrate_to_chat_id

    @property
    def migrate_from_chat_id(self) -> Optional[int]:
        return self._migrate_from_chat_id

    @property
    def pinned_message(self):
        """
        :rtype: Optional[Message]
        """
        return self._pinned_message

    @property
    def invoice(self) -> Optional[Invoice]:
        return self._invoice

    @property
    def successful_payment(self) -> Optional[SuccessfulPayment]:
        return self._successful_payment


class CallbackQuery(TelegramType):
    def __init__(self, data):
        super().__init__(data)

        self._id = data['id']  # type: str
        self._from = User(data['from'])
        self._message = Message(data['message']) if 'message' in data else None
        self._inline_message_id = data.get('inline_message_id')  # type: Optional[str]
        self._chat_instance = data.get('chat_instance')  # type: Optional[str]
        self._query_data = data.get('data')  # type: Optional[str]
        self._game_short_name = data.get('game_short_name')  # type: Optional[str]

    @property
    def id(self) -> str:
        return self._id

    @property
    def sender(self):
        return self._from

    @property
    def message(self) -> Optional[Message]:
        return self._message

    @property
    def inline_message_id(self) -> Optional[str]:
        return self._inline_message_id

    @property
    def chat_instance(self) -> Optional[str]:
        return self._chat_instance

    @property
    def data(self) -> Optional[str]:
        return self._query_data

    @property
    def game_short_name(self) -> Optional[str]:
        return self._game_short_name


class Update(TelegramType):
    """Telegram Update Object

    https://core.telegram.org/bots/api#update
    """

    def __init__(self, data: dict):
        super().__init__(data)

        self._update_id = data['update_id']
        self._message = Message(data['message']) if 'message' in data else None
        self._edited_message = Message(data['edited_message']) if 'edited_message' in data else None
        self._channel_post = Message(data['channel_post']) if 'channel_post' in data else None
        self._edited_channel_post = Message(data['edited_channel_post']) if 'edited_channel_post' in data else None
        self._inline_query = InlineQuery(data['inline_query']) if 'inline_query' in data else None
        self._chosen_inline_result = ChosenInlineResult(
            data['chosen_inline_result']) if 'chosen_inline_result' in data else None
        self._callback_query = CallbackQuery(data['callback_query']) if 'callback_query' in data else None
        self._shipping_query = ShippingQuery(data['shipping_query']) if 'shipping_query' in data else None
        self._pre_checkout_query = PreCheckoutQuery(
            data['pre_checkout_query']) if 'pre_checkout_query' in data else None

    @property
    def update_id(self) -> int:
        return self._update_id

    @property
    def message(self) -> Optional[Message]:
        return self._message

    @property
    def edited_message(self) -> Optional[Message]:
        return self._edited_message

    @property
    def channel_post(self) -> Optional[Message]:
        return self._channel_post

    @property
    def edited_channel_post(self) -> Optional[Message]:
        return self._edited_channel_post

    @property
    def inline_query(self) -> Optional[InlineQuery]:
        return self._inline_query

    @property
    def chosen_inline_result(self) -> Optional[ChosenInlineResult]:
        return self._chosen_inline_result

    @property
    def callback_query(self) -> Optional[CallbackQuery]:
        return self._callback_query

    @property
    def shipping_query(self) -> Optional[ShippingQuery]:
        return self._shipping_query

    @property
    def pre_checkout_query(self) -> Optional[PreCheckoutQuery]:
        return self._pre_checkout_query
