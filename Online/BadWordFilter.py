import re
import html as html1
from lxml import html
from typing import List
import asyncio
from Ofline.config import bad_words,white_list


class FilterBadWords:
    def __init__(self):
        # Создаем паттерны для всех плохих слов
        self.bad_words_patterns = set([
            FilterBadWords.generate_regex_for_any_word(word)
            for word in bad_words if word.strip()
        ])


    @staticmethod
    async def edit_content(content):
        async def edit_text(text_escaped):
            if not text_escaped:
                return ""
            unescaped_text = html1.unescape(text_escaped)
            try:
                text = html.fromstring(unescaped_text)
                return text.text_content()
            except html.etree.ParserError:
                return unescaped_text

        return await asyncio.gather(*(edit_text(item) for item in content))

    @staticmethod
    def normalize_text(text: str) -> str:
        if text is None:
            return ""
        replacements = {
            '@': 'а',
            '1': 'и',
            '!': 'и',
            '3': 'з',
            '$': 'с',
            '0': 'о',
            '&': 'з',
            '4': 'ч',
            '6': 'б',
            '9': 'я',
            "a": "а",
            "b": "б",
            "v": "в",
            "g": "г",
            "d": "д",
            "e": "е",
            "yo": "ё",
            "zh": "ж",
            "z": "з",
            "i": "и",
            "j": "й",
            "k": "к",
            "l": "л",
            "m": "м",
            "n": "н",
            "o": "о",
            "p": "п",
            "r": "р",
            "s": "с",
            "t": "т",
            "u": "у",
            "f": "ф",
            "h": "х",
            "ts": "ц",
            "ch": "ч",
            "sh": "ш",
            "shch": "щ",
            "y": "у",  # упрощенно
            "yu": "ю",
            "ya": "я",
            "": "ь",  # мягкий знак
            "'": "ъ",  # твердый знак
            "je": "э",
            "e'": "э",
        }
        text = text.lower().strip()
        for char in list(text):
            replacement = replacements.get(char, char)
            text = text.replace(char, replacement)
        # Оставляем только буквы и пробелы
        text = re.sub(r'[^а-яa-z\s]', '', text)
        return text

    @staticmethod
    def generate_regex_for_any_word(word: str) -> re.Pattern:
        """
        Генерирует регулярное выражение для слова с учетом возможных повторений букв.
        Границы слова делаем опциональными, чтобы ловить склейки.
        """
        # Экранируем слово, затем для каждого символа разрешаем повторение
        escaped = re.escape(word)
        regex = r"\b"  # опциональная граница в начале
        for char in escaped:
            regex += f"{char}+"
        regex += r"\b"  # опциональный мягкий знак и граница в конце
        return re.compile(regex, re.IGNORECASE | re.VERBOSE)

    @staticmethod
    async def check_bad_words(text: str, bad_words_patterns: set) -> bool:
        normalized_text = FilterBadWords.normalize_text(text)
        if normalized_text in white_list:
            return False
        elif normalized_text in bad_words:
            return True
        for pattern in bad_words_patterns:
            if pattern.search(normalized_text):
                print(f"⚠️ Совпадение (regex): '{normalized_text}' под {pattern.pattern}")
                return True
        return False

    async def filter_bad_words(self, texts: List[str]) -> bool:
        texts = [text for text in texts if text is not None]
        words = set()
        # Добавляем как целые строки, так и разбиваем предложения на отдельные слова
        for sentence in texts:
            words.add(sentence)
            for word in sentence.split():
                words.add(word)
        results = await asyncio.gather(*[
            self.check_bad_words(word, self.bad_words_patterns) for word in words
        ])
        return any(results)