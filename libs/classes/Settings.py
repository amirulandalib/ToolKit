import typing as p
from copy import deepcopy

from aiogram.utils.callback_data import CallbackData

from .Buttons import Button, MenuButton

clb_data = CallbackData("chat_settings", "chat_id", "lang")

ElementType = p.Union[str, bool]
ListType = p.List[ElementType]
DictType = p.Dict[str, ElementType]
SettingType = p.Dict[str, p.Union[ListType, DictType]]


class _ElementIter:
    def __init__(self, values: p.Union[DictType, ListType]):
        self.values = values

    def __iter__(self):
        value: p.Optional[ElementType] = None
        key: ElementType
        num: int
        for num, key in enumerate(self.values):
            if isinstance(self.values, dict):
                value = self.values[key]
            yield num, key, value


class _Settings:
    def __init__(self, title: str, text: str, key: str, *elements, undo: bool = False, row: int = 1):
        ParametersType = p.List[p.Union[ListSettings, DictSettings, Elements, Button]]

        self.title = title
        self.text = text
        self.key = key
        self.undo = undo
        self.row = row
        self.elements: ParametersType = list(elements)

        self.settings: SettingType = None
        self.menu: MenuButton = None

        self.data = CallbackData(key, "chat_id", "lang")
        self.chat_id = None
        self.lang = None

    def add(self, *elements):
        self.elements += elements
        return self

    def get_menu(self, settings: SettingType, chat_id: int, lang: str):
        menu = MenuButton(self.text, self.title, self.data.new(chat_id=chat_id, lang=lang),
                          make_unique=False, undo=self.undo, row=self.row)

        if isinstance(self, Settings):
            values = settings
        elif self.key not in settings:
            settings[self.key] = {}
            values = settings[self.key]
        else:
            values = settings[self.key]

        menu.add(
            *self.get_buttons(values, chat_id, lang)
        )

        self.menu = menu
        self.settings = values
        self.chat_id = chat_id
        self.lang = lang
        return menu

    def update_buttons(self):
        self.menu.buttons.clear()

        self.menu.add(
            *self.get_buttons(self.settings, self.chat_id, self.lang)
        )

        return self.menu

    def get_buttons(self, values: p.Union[ListType, DictType], chat_id: int, lang: str):
        buttons = []
        for elem in self.elements:
            if isinstance(elem, Elements):
                buttons += elem.buttons(values)
                continue
            elif isinstance(elem, Button):
                button = elem
            elif isinstance(elem, _Settings):
                button = elem.get_menu(values, chat_id, lang)
                button.storage["current_element"] = elem
                button.storage["current_menu"] = button
            else:
                continue
            buttons.append(button)

        return buttons

    @property
    def copy(self):
        return deepcopy(self)


class Elements:
    def __init__(self, text: str, data: str):
        """
        text и data "{num} {key} {value}"
        """
        self.text = text
        self.data = data

    def buttons(self, values: p.Union[DictType, ListType]):
        buttons = []
        values = _ElementIter(values)
        for num, key, value in values:
            text = self.format_text(num, key, value)
            data = self.format_data(num, key, value)
            buttons.append(Button(text, data))

        return buttons

    def format_data(self, num: int, key: str, value: ElementType):
        return self.data.format(
            num=num,
            key=key,
            value=value
        )

    def format_text(self, num: int, key: str, value: ElementType):
        return self.text.format(
            num=num,
            key=key,
            value=value
        )


class ListSettings(_Settings):
    def __init__(self, title: str, text: str, key: str, *elements, undo: bool = True, row: int = 1):
        super().__init__(title, text, key, *elements, undo=undo, row=row)


class DictSettings(_Settings):
    def __init__(self, title: str, text: str, key: str, *elements, undo: bool = True, row: int = 1):
        super().__init__(title, text, key, *elements, undo=undo, row=row)


class Settings(_Settings):

    def __init__(self, title: str, text: str, key: str, *elements, undo: bool = True, row: int = 1):
        super().__init__(title, text, key, *elements, undo=undo, row=row)

    def save(self, chat):
        chat.settings = self.settings

    def get_menu(self, settings: SettingType, chat_id: int, lang: str,
                 edit: bool = False, text: p.Optional[str] = None):
        self.text = text or self.text
        return super().get_menu(settings, chat_id, lang)
