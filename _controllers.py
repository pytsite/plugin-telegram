"""PytSite Telegram Plugin Controllers
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

import json
from pytsite import routing, logger
from . import _api, types, error


class PostHook(routing.Controller):
    """Webhook Controller
    """

    def exec(self):
        try:
            _api.dispense_bot(self.arg('bot_uid')).process_update(types.Update(json.loads(self.request.data)))
        except error.BotNotRegistered as e:
            logger.warn(str(e))
        except Exception as e:
            logger.error(e)
