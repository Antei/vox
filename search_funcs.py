import wikipedia as wiki
import os
from dotenv import load_dotenv
from pyowm import OWM
import traceback
from pyowm.utils.config import get_default_config


# загрузка файла .env
load_dotenv(".env\.env")


class Wikisearcher:
    # очистка текста статьи и ограничение объема текста
    def get_wiki_info(self, lang: str, request: str):
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


class Weatherer:

    def get_weather_info(self, request_city):
        config_dict = get_default_config()
        config_dict['language'] = 'ru'
        self.city = request_city

        try:
            # использование API-ключа, помещённого в .env-файл
            weather_api_key = os.getenv("OWM_API_KEY")
            self.ow_map = OWM(weather_api_key)

            # запрос данных о текущем состоянии погоды в указанном городе
            wm = self.ow_map.weather_manager()
            observation = wm.weather_at_place(self.city)
            weather = observation.weather
        except:
            traceback.print_exc()
            return 'Ошибка, не найдены данные о погоде'

        # разбиение данных на части для удобства
        status = weather.detailed_status # облачность
        temperature = int(weather.temperature('celsius')["temp"])
        wind_speed = int(weather.wind()["speed"])
        pressure = int(weather.pressure["press"] / 1.333)  # перевод из гПА в мм рт.ст

        result = f'''Погода в {self.city}: 
                     Температура: {temperature} по Цельсию,
                     Скорость ветра: {wind_speed} метра в секунду, 
                     {status}.'''

        return result