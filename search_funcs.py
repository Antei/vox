import wikipedia as wiki

import re


class Wikisearcher:
    # очистка текста статьи и ограничение объема текста
    def get_info(self, lang: str, request: str):
        wiki.set_lang(lang)
        try:
            self.wp = wiki.page(request) # контент страницы
            text: str = self.wp.content[:500] # первые n символов
            text_array = text.split('.') # разбиение по точкам
            text_array = text_array[:-1] # отброс всего после последней точки
            text_final = '' # пустая переменная для возвращаемого текста
            for i in text_array:
                if not('==' in i):
                    # если в строке осталось больше трех символов, добавляем в возвращаемый текст и прибавляем убранные точки
                    if (len((i.strip())) > 3):
                        text_final = text_final + i + '.'
            # убираем разметку и лишние пробелы
            text_final = re.sub('\([^()]*\)', '', text_final)
            text_final = re.sub('\{[^\{\}]*\}', '', text_final)
            text_final = text_final.replace(' ,', ',')
            text_final = text_final.replace('.', '. ')
            return text_final
        except Exception as e:
            if str(e).find(f'{request} may refer to:'):
                return f'{request} встречается в разных статьях. Дополните запрос.'
            return 'Не нашлось информации об этом.'