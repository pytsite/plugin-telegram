"""PytSite Telegram Bot
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

import json as _json
from typing import Union as _Union, Mapping as _Mapping
from werkzeug.utils import cached_property as _cached_property
from pytsite import cache as _cache, reg as _reg, logger as _logger, lang as _lang, util as _util
from . import _api, types as _types, reply_markup as _reply_markup, error as _error

_cache_pool = _cache.create_pool('telegram.bot_state')


class Bot:
    def __init__(self, token: str):
        """Init
        """
        if not token:
            raise ValueError('Empty token')

        self._id = _util.md5_hex_digest(str(self.__class__))
        self._state_ttl = _reg.get('telegram.bot_state_ttl', 86400)
        self._token = token
        self._me = None
        self._sender = None  # type: _types.User
        self._chat = None  # type: _types.Chat
        self._last_message_id = None  # type: int
        self._command_aliases = {}

    @property
    def token(self) -> str:
        """Get bot's token
        """
        return self._token

    @_cached_property
    def id(self) -> int:
        """Get bot's ID
        """
        return self.get_me().id

    @_cached_property
    def username(self) -> str:
        """Get bot's username
        """
        return self.get_me().username

    @property
    def chat(self) -> _types.Chat:
        """Get current chat ID
        """
        if not self._chat:
            raise ValueError('Chat is not set yet')

        return self._chat

    @property
    def sender(self) -> _types.User:
        """Get current message sender's ID
        """
        if not self._sender:
            raise ValueError('Sender is not set yet')

        return self._sender

    @property
    def last_message_id(self) -> int:
        """Get last message ID
        """
        if not self._last_message_id:
            raise ValueError('Last message ID is not set yet')

        return self._last_message_id

    @property
    def command_name(self) -> str:
        return self.get_var('_command')

    @command_name.setter
    def command_name(self, value: str):
        self.set_var('_command', value)

    @property
    def command_step(self) -> int:
        """Get current command's step
        """
        return self.get_var('_command_{}_step'.format(self.command_name))

    @command_step.setter
    def command_step(self, value: int):
        """Set current command's step
        """
        self.set_var('_command_{}_step'.format(self.command_name), value)

    @property
    def vars(self) -> _Mapping:
        """Get state variables
        """
        return _cache_pool.get_hash('{}.{}'.format(self._id, self.chat.id))

    def set_command_alias(self, command: str, alias: str):
        if alias in self._command_aliases:
            raise ValueError("Command alias '{}' already defined")

        self._command_aliases[alias] = command

    def get_var(self, key: str, default=None):
        """Get a value of a state variable
        """
        try:
            return _cache_pool.get_hash_item('{}.{}'.format(self._id, self.chat.id), key, default)
        except _cache.error.KeyNotExist:
            return default

    def set_var(self, key: str, value):
        """Set a value of a state variable
        """
        k = '{}.{}'.format(self._id, self.chat.id)
        try:
            _cache_pool.put_hash_item(k, key, value)
        except _cache.error.KeyNotExist:
            _cache_pool.put_hash(k, {key: value})

        return self

    def del_var(self, key: str):
        """Delete a state variable
        """
        try:
            _cache_pool.rm_hash_item('{}.{}'.format(self._id, self.chat.id), key)
        except _cache.error.KeyNotExist:
            pass

        return self

    def reset(self):
        """Reset entire bot's state
        """
        _cache_pool.rm('{}.{}'.format(self._id, self.chat.id))
        _cache_pool.rm('{}.{}'.format(self._id, self.chat.id))

        return self

    def process_update(self, update: _types.Update):
        """Process incoming update from Telegram
        """
        if update.message or update.edited_message:
            message = update.message or update.edited_message
            self._sender = message.sender
            self._chat = message.chat
            self._last_message_id = message.message_id
            self._process_private_message(message)

        elif update.channel_post or update.edited_channel_post:
            post = update.channel_post or update.edited_channel_post
            self._sender = post.sender
            self._chat = post.chat
            self._last_message_id = post.message_id
            self.handle_channel_post(post)

        elif update.inline_query:
            self._sender = update.inline_query.sender
            self.handle_inline_query(update.inline_query)

        elif update.chosen_inline_result:
            self._sender = update.chosen_inline_result.sender
            self.handle_chosen_inline_result(update.chosen_inline_result)

        elif update.callback_query:
            self._sender = update.callback_query.sender
            if update.callback_query.message:
                self._chat = update.callback_query.message.chat
            self._process_callback_query(update.callback_query)

        elif update.shipping_query:
            self._sender = update.shipping_query.sender
            self.handle_shipping_query(update.shipping_query)

        elif update.pre_checkout_query:
            self._sender = update.pre_checkout_query.sender
            self.handle_pre_checkout_query(update.pre_checkout_query)

        else:
            raise RuntimeError("Unsupported update request from telegram: {}".format(update))

    def _request(self, endpoint: str, params: dict = None, data: dict = None, method: str = 'GET'):
        """Perform a request to the Telegram API
        """
        return _api.request(self._token, endpoint, params, data, method)

    def _process_private_message(self, msg: _types.Message):
        """Process an incoming private message
        """
        # New command received
        if msg.text and (msg.text.startswith('/') or msg.text in self._command_aliases):
            if msg.text.startswith('/'):
                cmd_name = msg.text[1:].split(' ')[0]
                if cmd_name in self._command_aliases:
                    self.call_command(self._command_aliases[cmd_name], msg, 0)
                else:
                    self.call_command(cmd_name, msg, 0)
            else:
                self.call_command(self._command_aliases[msg.text], msg, 0)

        # Simple message received
        else:
            # Try to restore current command from state
            if self.command_name:
                self.call_command(self.command_name, msg)

            # No current command, simply handle message
            else:
                self.handle_private_message(msg)

    def _process_callback_query(self, query: _types.CallbackQuery):
        # Try to restore current command from state
        if self.command_name:
            self.call_command(self.command_name, query)
        else:
            self.handle_private_message(query)

    def finish_command(self):
        """Clear command related state variables
        """
        self.command_name = None
        self.command_step = 0

        return self

    def call_command(self, name: str, msg: _Union[_types.Message, _types.CallbackQuery], step: int = None):
        """Process an incoming command
        """
        self.command_name = name
        if step is not None:
            self.command_step = step

        try:
            cmd_method = 'cmd_{}'.format(name)
            if hasattr(self, cmd_method):
                getattr(self, cmd_method)(msg)
            else:
                self.handle_command(name, msg)

        except _error.CommandExecutionError as e:
            _logger.error(e)
            self.send_message(e.msg, reply_markup=e.reply_markup)

    def handle_private_message(self, msg: _Union[_types.Message, _types.CallbackQuery]):
        """Hook
        """
        _logger.debug('{}: Private message received: {}'.format(self.__class__, msg))

    def handle_command(self, name: str, msg: _Union[_types.Message, _types.CallbackQuery]):
        """Hook
        """
        _logger.debug('{}: Command received: {}'.format(self.__class__, msg))

        raise _error.CommandExecutionError(_lang.t('telegram@unknown_command', {'command': name}))

    def handle_channel_post(self, msg: _types.Message):
        """Hook
        """
        _logger.debug('{}: Channel post received: {}'.format(self.__class__, msg))

    def handle_inline_query(self, query: _types.InlineQuery):
        """Hook
        """
        _logger.debug('{}: Inline query received: {}'.format(self.__class__, query))

    def handle_chosen_inline_result(self, result: _types.ChosenInlineResult):
        """Hook
        """
        _logger.debug('{}: Chosen inline result received: {}'.format(self.__class__, result))

    def handle_callback_query(self, query: _types.CallbackQuery):
        """Hook
        """
        _logger.debug('{}: Callback query received: {}'.format(self.__class__, query))

    def handle_shipping_query(self, query: _types.ShippingQuery):
        """Hook
        """
        _logger.debug('{}: Shipping query received: {}'.format(self.__class__, query))

    def handle_pre_checkout_query(self, query: _types.PreCheckoutQuery):
        """Hook
        """
        _logger.debug('{}: Pre checkout query received: {}'.format(self.__class__, query))

    def get_me(self) -> _types.User:
        """A simple method for testing bot's auth token

        https://core.telegram.org/bots/api#getme
        """
        if self._me:
            return self._me

        self._me = _types.User(self._request('getMe'))

        return self._me

    def send_message(self, text: str, chat_id: _Union[int, str] = None, parse_mode: str = 'HTML',
                     disable_web_page_preview: bool = False, disable_notification: bool = False,
                     reply_to_message_id: int = None, reply_markup: _reply_markup.ReplyMarkup = None) -> _types.Message:
        """Send text message

        https://core.telegram.org/bots/api#sendmessage
        """
        if parse_mode not in ('HTML', 'Markdown'):
            parse_mode = 'HTML'

        msg = _types.Message(self._request('sendMessage', {
            'chat_id': chat_id or self.chat.id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': disable_web_page_preview,
            'disable_notification': disable_notification,
            'reply_to_message_id': reply_to_message_id,
            'reply_markup': _json.dumps(reply_markup.as_jsonable()) if reply_markup else '',
        }))

        self._last_message_id = msg.message_id

        return msg

    def edit_message_text(self, text: str, chat_id: _Union[int, str] = None, message_id: int = None,
                          inline_message_id: str = None, parse_mode: str = 'HTML',
                          disable_web_page_preview: bool = False,
                          reply_markup: _reply_markup.ReplyMarkup = None) -> _types.Message:
        """Edit text of a message

        https://core.telegram.org/bots/api#editmessagetext
        """

        if parse_mode not in ('HTML', 'Markdown'):
            parse_mode = 'HTML'

        return _types.Message(self._request('editMessageText', {
            'text': text,
            'chat_id': chat_id,
            'message_id': message_id,
            'inline_message_id': inline_message_id,
            'parse_mode': parse_mode,
            'disable_web_page_preview': disable_web_page_preview,
            'reply_markup': _json.dumps(reply_markup.as_jsonable()) if reply_markup else '',
        }))

    def edit_message_caption(self, caption: str = None, chat_id: _Union[int, str] = None, message_id: int = None,
                             inline_message_id: str = None, reply_markup: _reply_markup.ReplyMarkup = None):
        """Edit caption of a message

        https://core.telegram.org/bots/api#editmessagecaption
        """
        return self._request('editMessageCaption', {
            'caption': caption,
            'chat_id': chat_id,
            'message_id': message_id,
            'inline_message_id': inline_message_id,
            'reply_markup': _json.dumps(reply_markup.as_jsonable()) if reply_markup else '',
        })

    def edit_message_reply_markup(self, chat_id: _Union[int, str] = None, message_id: int = None,
                                  inline_message_id: str = None, reply_markup: _reply_markup.ReplyMarkup = None):
        """Edit reply markup of a message

        https://core.telegram.org/bots/api#editmessagereplymarkup
        """
        return self._request('editMessageReplyMarkup', {
            'chat_id': chat_id,
            'message_id': message_id,
            'inline_message_id': inline_message_id,
            'reply_markup': _json.dumps(reply_markup.as_jsonable()) if reply_markup else '',
        })

    def answer_callback_query(self, callback_query_id: str, text: str = None, show_alert: bool = False, url: str = None,
                              cache_time: int = 0):
        """Send answer to callback query sent from inline keyboards

        https://core.telegram.org/bots/api#answercallbackquery
        """
        return self._request('answerCallbackQuery', {
            'callback_query_id': callback_query_id,
            'text': text,
            'show_alert': show_alert,
            'url': url,
            'cache_time': cache_time,
        })

    def delete_message(self, chat_id: _Union[int, str], message_id: int):
        """Delete a message

        https://core.telegram.org/bots/api#deletemessage
        """
        return self._request('deleteMessage', {
            'chat_id': chat_id or self.chat.id,
            'message_id': message_id,
        })

    def send_photo(self, photo_file_id: str, chat_id: _Union[int, str] = None, caption: str = None,
                   disable_notification: bool = None, reply_to_message_id: int = None,
                   reply_markup: _reply_markup.ReplyMarkup = None) -> _types.Message:
        """Send a photo

        https://core.telegram.org/bots/api#sendphoto
        """
        msg = _types.Message(self._request('sendPhoto', {
            'chat_id': chat_id or self.chat.id,
            'photo': photo_file_id,
            'caption': caption,
            'disable_notification': disable_notification,
            'reply_to_message_id': reply_to_message_id,
            'reply_markup': _json.dumps(reply_markup.as_jsonable()) if reply_markup else '',
        }))

        self._last_message_id = msg.message_id

        return msg

    def _sanitize_chat_id(self, chat_id: _Union[int, str]) -> _Union[int, str]:
        if isinstance(chat_id, str):
            if ' ' in chat_id:
                chat_id = chat_id.split(' ')[0]

            if not chat_id.startswith('@'):
                chat_id = '@' + chat_id

        return chat_id

    def get_chat(self, chat_id: _Union[int, str]) -> _types.Chat:
        """Get up to date information about the chat

        https://core.telegram.org/bots/api#getchat
        """
        chat_id = self._sanitize_chat_id(chat_id)

        try:
            return _types.Chat(self._request('getChat', {
                'chat_id': chat_id,
            }))

        except _error.ApiRequestError as e:
            if 'chat not found' in str(e) or 'bot was kicked':
                raise _error.ChatNotFound(chat_id)
            else:
                raise e

    def get_chat_administrators(self, chat_id: _Union[int, str]) -> _types.ChatMemberArray:
        """Get a list of administrators in a chat

        https://core.telegram.org/bots/api#getchatadministrators
        """
        chat_id = self._sanitize_chat_id(chat_id)

        try:
            return _types.ChatMemberArray(self._request('getChatAdministrators', {
                'chat_id': chat_id,
            }))

        except _error.ApiRequestError as e:
            if 'chat not found' in str(e):
                raise _error.ChatNotFound(chat_id)

    def get_chat_member(self, chat_id: _Union[int, str], user_id: int) -> _types.ChatMember:
        """Get information about a member of a chat

        https://core.telegram.org/bots/api#getchatmember
        """
        chat_id = self._sanitize_chat_id(chat_id)

        try:
            return _types.ChatMember(self._request('getChatMember', {
                'chat_id': chat_id,
                'user_id': user_id,
            }))

        except _error.ApiRequestError as e:
            if 'chat not found' in str(e):
                raise _error.ChatNotFound(chat_id)

    def can_post_messages(self, chat_id: _Union[str, int]) -> bool:
        """Check if the bot can post messages to a chat
        """
        try:
            return self.get_chat_member(chat_id, self.id).can_post_messages

        except _error.ChatNotFound:
            return False

    def get_file(self, file_id: str) -> _types.File:
        try:
            return _types.File(self._request('getFile', {
                'file_id': file_id,
            }))
        except _error.ApiRequestError as e:
            _logger.error(e)
            raise _error.FileNotFound(file_id)

    def get_file_url(self, file: _types.File) -> str:
        return 'https://api.telegram.org/file/bot{}/{}'.format(self._token, file.file_path)
