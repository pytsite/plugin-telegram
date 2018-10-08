"""PytSite Telegram Plugin Controllers
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

import json as _json
from pytsite import routing as _routing, logger as _logger
from . import _api, types as _types, error as _error


class PostHook(_routing.Controller):
    """Webhook Controller
    """

    def exec(self):
        try:
            _api.dispense_bot(self.arg('bot_uid')).process_update(_types.Update(_json.loads(self.request.data)))
        except _error.BotNotRegistered as e:
            _logger.warn(str(e))
        except Exception as e:
            _logger.error(e)
