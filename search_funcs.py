import wikipedia as wiki


class Wikisearcher:
    # очистка текста статьи и ограничение объема текста
    def get_info(self, lang: str, request: str):
        wiki.set_lang(lang)
        try:
            self.wp = wiki.summary(request, sentences=7) # контент страницы
            text: str = self.wp.split('==')
            text = ' '.join(line.strip() for line in text)
            return text
        except Exception as e:
            if str(e).find(f'{request} may refer to:'):
                return f'{request} встречается в разных статьях. Дополните запрос.'
            return 'Не нашлось информации об этом.'