"""PytSite Telegram Plugin Reply Markups
"""
from typing import Type as _Type, List as _List
from abc import abstractmethod as _abstractmethod
from . import types

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


class AbstractKeyboardButton(types.JSONable):
    """Abstract Keyboard Button
    """
    pass


class Button(AbstractKeyboardButton):
    """Normal Keyboard Button

    https://core.telegram.org/bots/api#keyboardbutton
    """

    def __init__(self, text: str, request_contact: bool = False, request_location: bool = False):
        self._text = text
        self._request_contact = request_contact
        self._request_location = request_location

    def as_jsonable(self) -> dict:
        return {
            'text': self._text,
            'request_contact': self._request_contact,
            'request_location': self._request_location
        }


class InlineButton(AbstractKeyboardButton):
    """Inline Keyboard Button

    https://core.telegram.org/bots/api#inlinekeyboardbutton
    """

    def __init__(self, text: str, url: str = None, callback_data: str = None, switch_inline_query: str = None,
                 switch_inline_query_current_chat: str = None, callback_game: types.CallbackGame = None,
                 pay: bool = False):
        if not (url or callback_data):
            raise RuntimeError('One of the optional arguments must be specified')

        self._text = text
        self._url = url
        self._callback_data = callback_data
        self._switch_inline_query = switch_inline_query
        self._switch_inline_query_current_chat = switch_inline_query_current_chat
        self._callback_game = callback_game
        self._pay = pay

    def as_jsonable(self) -> dict:
        return {
            'text': self._text,
            'url': self._url or '',
            'callback_data': self._callback_data or '',
            'switch_inline_query': self._switch_inline_query or '',
            'switch_inline_query_current_chat': self._switch_inline_query_current_chat or '',
            'callback_game': self._callback_game or {},
            'pay': self._pay,
        }


class Keyboard(types.JSONable):
    """Normal Keyboard Buttons Container
    """

    def __init__(self, buttons: _List[_List[AbstractKeyboardButton]] = None, _expected_button_type: _Type = Button):
        """Init
        """
        if buttons is None:
            buttons = [[]]

        if not isinstance(buttons, list):
            raise TypeError('List of lists of KeyboardButton expected, got {}'.format(type(buttons)))

        for row in buttons:
            if not isinstance(row, list):
                raise TypeError('List of KeyboardButton expected, got {}'.format(type(row)))

            for btn in row:
                if not isinstance(btn, _expected_button_type):
                    raise TypeError("{} expected, got {}".format(_expected_button_type, type(btn)))

        self._expected_button_type = _expected_button_type
        self._buttons = buttons

    def __len__(self):
        r = 0
        for row in self._buttons:
            r += len(row)

        return r

    def append_row(self):
        """Append a row
        """
        self._buttons.append([])

        return self

    def append_button(self, button: AbstractKeyboardButton, row: int = None):
        """Append a button to a row
        """
        if not isinstance(button, self._expected_button_type):
            raise TypeError("{} expected, got {}".format(self._expected_button_type, type(button)))

        if row is None:
            row = len(self._buttons) - 1

        try:
            self._buttons[row].append(button)

        except IndexError:
            raise IndexError('There is no row at index {}'.format(row))

        return self

    def as_jsonable(self) -> list:
        r = []

        for row in self._buttons:
            r_row = []

            for btn in row:
                r_row.append(btn.as_jsonable())

            r.append(r_row)

        return r


class InlineKeyboard(Keyboard):
    """Inline Keyboard Buttons Container
    """

    def __init__(self, buttons: _List[_List] = None):
        super().__init__(buttons, InlineButton)


class ReplyMarkup(types.JSONable):
    """Base Class for Reply Markup
    """

    @_abstractmethod
    def as_jsonable(self):
        pass


class ReplyKeyboardMarkup(ReplyMarkup):
    """Custom Keyboard With Reply Options

    https://core.telegram.org/bots/api#replykeyboardmarkup
    """

    def __init__(self, keyboard: Keyboard, resize_keyboard: bool = True, one_time_keyboard: bool = True,
                 selective: bool = False):
        self._keyboard = keyboard
        self._resize_keyboard = resize_keyboard
        self._one_time_keyboard = one_time_keyboard
        self._selective = selective

    def as_jsonable(self) -> dict:
        return {
            'keyboard': self._keyboard.as_jsonable(),
            'resize_keyboard': self._resize_keyboard,
            'one_time_keyboard': self._one_time_keyboard,
            'selective': self._selective,
        }


class InlineKeyboardMarkup(ReplyMarkup):
    """Inline Keyboard

    https://core.telegram.org/bots/api#inlinekeyboardmarkup
    """

    def __init__(self, inline_keyboard: Keyboard):
        self._inline_keyboard = inline_keyboard

    def as_jsonable(self) -> dict:
        return {
            'inline_keyboard': self._inline_keyboard.as_jsonable()
        }


class ReplyKeyboardRemove(ReplyMarkup):
    """Remove Reply Keyboard

    Upon receiving a message with this object, Telegram clients will remove the current custom keyboard and display
    the default letter-keyboard

    https://core.telegram.org/bots/api#replykeyboardremove
    """

    def __init__(self, selective: bool = False):
        self._selective = selective

    def as_jsonable(self):
        return {
            'remove_keyboard': True,
            'selective': self._selective
        }


class ForceReply(ReplyMarkup):
    """Force Reply

    https://core.telegram.org/bots/api#forcereply
    """

    def __init__(self, selective: bool = False):
        self._selective = selective

    def as_jsonable(self):
        return {
            'force_reply': True,
            'selective': self._selective
        }
