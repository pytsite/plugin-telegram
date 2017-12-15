"""PytSite Telegram Plugin Controllers
"""
import json as _json
from pytsite import routing as _routing
from . import _api, types as _types

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


class PostHook(_routing.Controller):
    """Webhook Controller
    """

    def exec(self):
        _api.dispense_bot(self.arg('bot_uid')).process_update(_types.Update(_json.loads(self.request.data)))
