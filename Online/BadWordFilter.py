import re
import html as html1
from lxml import html
from typing import List
import asyncio
from config import bad_words

class FilterBadWords:
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
            '@': 'а', '*': '*', '1': 'и', 'i': 'и', '!': 'и',
            '3': 'з', '$': 'с', '0': 'о', 'z': 'з', '&': 'з',
            '4': 'ч', '6': 'б', '9': 'я', 'p': 'р', 'd': 'д'
        }
        text = text.lower()
        for k, v in replacements.items():
            text = text.replace(k, v)
        # Убираем любые символы, кроме букв, цифр, пробелов и специальных символов
        text = re.sub(r'[^а-яa-z0-9\s*@!$]', '', text)
        return text

    @staticmethod
    def build_regex(bad_word: str) -> re.Pattern:
        pattern = bad_word \
            .replace('а', '[аa@]') \
            .replace('и', '[иi1!]') \
            .replace('о', '[оo0]') \
            .replace('з', '[з3z&]') \
            .replace('с', '[с$s]') \
            .replace('е', '[еeё]') \
            .replace('д', '[дd]') \
            .replace('п', '[пp]') \
            .replace('я', '[я9]') \
            .replace('ч', '[ч4]') \
            .replace('б', '[б6]')
        # Добавляем поддержку произвольных символов между буквами, включая спецсимволы
        pattern = re.sub(r'(?<!\\)', r'.*?', pattern)
        return re.compile(pattern, re.IGNORECASE)

    @staticmethod
    async def check_bad_words(text: str, bad_words_patterns: List[re.Pattern]) -> bool:
        normalized_text = FilterBadWords.normalize_text(text)
        return any(pattern.search(normalized_text) for pattern in bad_words_patterns)

    @staticmethod
    async def filter_bad_words(texts: List[str]) -> List[str]:
        texts = [text for text in texts if text is not None]
        bad_words_patterns = [FilterBadWords.build_regex(word) for word in bad_words if word.strip()]
        results = await asyncio.gather(*[FilterBadWords.check_bad_words(text, bad_words_patterns) for text in texts])
        return [text for text, has_bad_word in zip(texts, results) if has_bad_word]