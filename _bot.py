"""PytSite Telegram Bot
"""
import requests as _requests
from . import _error

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


class Bot:
    def __init__(self, token: str):
        self._token = token

    def _request(self, endpoint: str, params: dict = None, data: dict = None, method: str = 'GET') -> dict:
        url = 'https://api.telegram.org/bot{}/{}'.format(self._token, endpoint)
        resp = _requests.request(method, url, params=params, data=data)

        if not resp.ok:
            raise _error.HttpRequestError(method, url, resp)

        return resp.json()['result']

    def get_updates(self):
        """Receive incoming updates using long polling

        https://core.telegram.org/bots/api#getupdates
        """
        pass

    def set_webhook(self, url: str):
        """Specify an URL and receive incoming updates via an outgoing webhook
        """
        pass

    def delete_webhook(self):
        """Remove webhook integration
        """
        pass

    def webhook_info(self) -> str:
        """Get information about the current status of a webhook
        """

    def get_me(self):
        """A simple method for testing your bot's auth token

        https://core.telegram.org/bots/api#getme
        """
        return self._request('getMe')

    def send_message(self, chat_id: str, text: str, **kwargs):
        """Method to send text messages

        https://core.telegram.org/bots/api#sendmessage
        """

        return self._request('sendMessage', {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': kwargs.get('parse_mode', 'html'),
            'disable_web_page_preview': kwargs.get('disable_web_page_preview', False),
            'disable_notification': kwargs.get('disable_notification', False),
            'reply_to_message_id': kwargs.get('reply_to_message_id'),
        })
