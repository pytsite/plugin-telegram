"""PytSite Telegram Bot API Plugin
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

# Public API
from . import error, types, reply_markup
from ._api import register_bot, unregister_bot, dispense_bot
from ._bot import Bot


def plugin_load():
    from pytsite import lang

    lang.register_package(__name__)


def plugin_load_uwsgi():
    from pytsite import router
    from . import _controllers

    router.handle(_controllers.PostHook, '/telegram/hook/<bot_uid>', 'telegram@bot_hook', methods='POST')
