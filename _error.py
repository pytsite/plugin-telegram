"""PytSite Telegram Bot API Errors
"""
from requests import Response as _RequestResponse

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


class Error(Exception):
    pass


class HttpRequestError(Error):
    def __init__(self, method: str, url: str, response: _RequestResponse):
        self._method = method
        self._url = url
        self._response = response

    def __str__(self) -> str:
        return 'Error while performing {} request to {}\n' \
               'Response code: {}\n' \
               'Response content: {}'.format(self._method, self._url, self._response.status_code,
                                             self._response.content.decode('utf-8'))
