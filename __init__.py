"""PytSite Telegram Bot API Plugin
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

# Public API
from . import error, types, reply_markup
from ._api import register_bot, unregister_bot, dispense_bot
from ._bot import Bot


def plugin_load_wsgi():
    from pytsite import router
    from . import _controllers

    router.handle(_controllers.PostHook, '/telegram/hook/<bot_uid>', 'telegram@bot_hook', methods='POST')
