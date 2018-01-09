"""PytSite Telegram Plugin Controllers
"""
import json as _json
from pytsite import routing as _routing, logger as _logger
from . import _api, types as _types, error as _error

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


class PostHook(_routing.Controller):
    """Webhook Controller
    """

    def exec(self):
        try:
            _api.dispense_bot(self.arg('bot_uid')).process_update(_types.Update(_json.loads(self.request.data)))
        except _error.BotNotRegistered as e:
            _logger.warn(str(e))
