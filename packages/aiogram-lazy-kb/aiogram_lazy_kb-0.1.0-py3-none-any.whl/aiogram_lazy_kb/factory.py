from typing import List, Union, Dict, Tuple
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

class LazyKeyboard:
    """
    Фабрика для быстрого создания клавиатур в aiogram 3.x
    """

    @staticmethod
    def reply(
        buttons: List[str],
        sizes: Union[int, List[int]] = 2,
        placeholder: str = None,
        one_time: bool = False,
        is_persistent: bool = False
    ) -> ReplyKeyboardMarkup:
        """
        Создает Reply клавиатуру (кнопки под полем ввода).
        
        :param buttons: Список текстов для кнопок ['Привет', 'Пока']
        :param sizes: Кол-во кнопок в ряду (int) или схема рядов (List[int]), например [2, 1]
        :param placeholder: Текст-подсказка в поле ввода
        :param one_time: Скрыть клавиатуру после нажатия
        """
        builder = ReplyKeyboardBuilder()
        
        for text in buttons:
            builder.add(KeyboardButton(text=text))
            
        # Если sizes это одно число, делаем сетку
        if isinstance(sizes, int):
            builder.adjust(sizes)
        else:
            # Если sizes это список [2, 1], строим по схеме
            builder.adjust(*sizes)
            
        return builder.as_markup(
            resize_keyboard=True, 
            input_field_placeholder=placeholder,
            one_time_keyboard=one_time,
            is_persistent=is_persistent
        )

    @staticmethod
    def inline(
        data: Union[Dict[str, str], List[Tuple[str, str]]],
        sizes: Union[int, List[int]] = 2
    ) -> InlineKeyboardMarkup:
        """
        Создает Inline клавиатуру (кнопки под сообщением).
        
        :param data: Словарь {'Текст': 'callback_data'} или Список кортежей [('Текст', 'url_или_callback')]
        :param sizes: Кол-во кнопок в ряду (int) или схема рядов (List[int])
        """
        builder = InlineKeyboardBuilder()
        
        # Приводим входные данные к списку кортежей для унификации
        items = data.items() if isinstance(data, dict) else data
        
        for text, value in items:
            if "://" in value:
                # Если похоже на ссылку, делаем URL-кнопку
                builder.add(InlineKeyboardButton(text=text, url=value))
            else:
                # Иначе callback_data
                builder.add(InlineKeyboardButton(text=text, callback_data=value))
                
        if isinstance(sizes, int):
            builder.adjust(sizes)
        else:
            builder.adjust(*sizes)
            
        return builder.as_markup()
