"""PytSite Telegram Bot API Errors
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from requests import Response as _RequestResponse
from .reply_markup import ReplyMarkup as _ReplyMarkup


class Error(Exception):
    pass


class CommandExecutionError(Error):
    def __init__(self, msg: str, reply_markup: _ReplyMarkup = None):
        self.msg = msg
        self.reply_markup = reply_markup

    def __str__(self) -> str:
        return self.msg


class ApiRequestError(Error):
    def __init__(self, method: str, url: str, response: _RequestResponse):
        self._method = method
        self._url = url
        self._response = response

    @property
    def response(self) -> _RequestResponse:
        return self._response

    def __str__(self) -> str:
        return 'Error while performing {} request to {}\n' \
               'Response code: {}\n' \
               'Response content: {}'.format(self._method, self._url, self._response.status_code,
                                             self._response.content.decode('utf-8'))


class BotNotFound(Error):
    def __init__(self, token: str):
        self._token = token

    def __str__(self) -> str:
        return "Bot with token '{}' is not found on the Telegram's side".format(self._token)


class BotNotRegistered(Error):
    def __init__(self, uid: str):
        self._uid = uid

    def __str__(self) -> str:
        return "Bot with UID '{}' is not registered".format(self._uid)


class BotAlreadyRegistered(Error):
    def __init__(self, uid: str):
        self._uid = uid

    def __str__(self) -> str:
        return "Bot with UID '{}' is already registered".format(self._uid)


class FileNotFound(ApiRequestError):
    def __init__(self, file_id: str):
        self._id = file_id

    def __str__(self) -> str:
        return "File with ID '{}' is not found".format(self._id)


class ChatNotFound(ApiRequestError):
    def __init__(self, chat_id: str):
        self._id = chat_id

    def __str__(self) -> str:
        return "Chat with ID '{}' is not found".format(self._id)
