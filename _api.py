"""PytSite Telegram Bot API
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

import requests as _requests
from typing import Type as _Type, Dict as _Dict, Tuple as _Tuple
from pytsite import util as _util, router as _router
from . import _bot, error as _error

# Registered bots
_BOTS = {}  # type: _Dict[str, _Tuple[_Type, str]]


def register_bot(token: str, bot_class: _Type, set_webhook: bool = True, max_connections: int = 40,
                 allowed_updates: list = None):
    """Register a new bot
    """
    if not token:
        raise ValueError("Bot's token is empty")

    uid = _util.md5_hex_digest(_router.server_name() + token)
    if uid in _BOTS:
        raise ValueError("Bot with token '{}' is already registered".format(token))

    if not isinstance(bot_class, type):
        raise TypeError('Class expected, got {}'.format(type(bot_class).__name__))

    if not issubclass(bot_class, _bot.Bot):
        raise TypeError("{} expected, got {}".format(_bot.Bot.__class__, bot_class.__name__))

    _BOTS[uid] = (bot_class, token, set_webhook)

    if set_webhook:
        _set_webhook(token, uid, max_connections, allowed_updates)


def unregister_bot(token: str):
    """Unregister a bot
    """
    if not token:
        raise ValueError("Bot's token is not registered")

    uid = _util.md5_hex_digest(_router.server_name() + token)
    if uid in _BOTS:
        if _BOTS[uid][2]:
            _delete_webhook(token)
        del _BOTS[uid]


def dispense_bot(uid: str) -> _bot.Bot:
    """Instantiate a bot
    """
    try:
        return _BOTS[uid][0](_BOTS[uid][1])

    except KeyError:
        raise _error.BotNotRegistered(uid)


def request(bot_token: str, endpoint: str, params: dict = None, data: dict = None, method: str = 'GET'):
    """Perform a request to the Telegram API
    """
    url = 'https://api.telegram.org/bot{}/{}'.format(bot_token, endpoint)
    resp = _requests.request(method, url, params=params, data=data)

    if not resp.ok:
        raise _error.ApiRequestError(method, url, resp)

    return resp.json()['result']


def _set_webhook(bot_token: str, bot_uid: str, max_connections: int = 40, allowed_updates: list = None) -> bool:
    """Specify an URL and receive incoming updates via an outgoing webhook

    https://core.telegram.org/bots/api#setwebhook
    """
    hook_url = _router.rule_url('telegram@bot_hook', {'bot_uid': bot_uid}, scheme='https')
    if _get_webhook_info(bot_token)['url'] != hook_url:
        try:
            return request(bot_token, 'setWebhook', {
                'url': hook_url,
                'max_connections': max_connections,
                'allowed_updates': allowed_updates or [],
            })

        except _error.ApiRequestError as e:
            if e.response.status_code == 404:
                raise _error.BotNotFound(bot_token)

            raise e


def _get_webhook_info(bot_token: str) -> dict:
    """Get current webhook status

    https://core.telegram.org/bots/api#getwebhookinfo
    """
    try:
        return request(bot_token, 'getWebhookInfo')

    except _error.ApiRequestError as e:
        if e.response.status_code == 404:
            raise _error.BotNotFound(bot_token)

        raise e


def _delete_webhook(bot_token: str) -> bool:
    """Remove webhook integration

    https://core.telegram.org/bots/api#deletewebhook
    """
    try:
        return request(bot_token, 'deleteWebhook')

    except _error.ApiRequestError as e:
        if e.response.status_code == 404:
            raise _error.BotNotFound(bot_token)

        raise e
