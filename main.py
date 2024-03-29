from cgi import test
import os
import random
import time
from datetime import datetime

# подключаем преобразование речи в текст и текста в речь
import listen_and_speak
# подключаем команды и имена ассистента
from commands import assistant_names, commands_dict
# подключаем пользовательские данные
from user_setup import User
# подключаем поисковые функции
import search_funcs
# подключаем сервисные функции
import service_funcs

# системное время
current_time = datetime.now()


# распознавание и воспроизведение речи
sr = listen_and_speak.Listener()
tts = listen_and_speak.Speaker()


# настройки пользователя
user = User(
    language='ru', 
    second_language='en', 
    homecity='Санкт-Петербург'
    )


# функции голосового помощника
def greetings(*args):
    # приветствие, случайное, в зависимости от времени суток
    greetings = ['добрый день', 'привет', 'здравствуйте',
                 'здарова', 'приветствую', 'добрый вечер']
    current_hour = current_time.hour

    if 5 < current_hour < 12:
        greetings = greetings[1:-1]
        greetings.append('доброе утро')  
    elif 12 < current_hour < 18:
        greetings = greetings[:-1]
    elif current_hour > 18:
        greetings = greetings[1:]
    tts.play_speech(random.choice(greetings))


def farewell_and_quit(*args):
    # прощание в зависимости от времени суток и выход из программы
    farewells = ['доброго дня', 'всего доброго', 'пока',
                 'до встречи', 'хорошего вечера']
    current_hour = current_time.hour
    if 5 < current_hour < 18:
        farewells = farewells[:-2]
    elif current_hour > 18:
        farewells = farewells[1:-1]
    elif 5 > current_hour > 22:
        farewells = farewells[1:-2]
        farewells.append('доброй ночи')
    tts.play_speech(random.choice(farewells))
    quit()


def create_task(*args):
    note = args[0]

    if note:
        with open('todo-list.txt', 'a', encoding='UTF-8') as file:
            file.write(f'- {note}\n')
        tts.play_speech(f'Задача "{note}" успешно добавлена в список дел.')
    else:
        tts.play_speech('Нет данных для добавления')


def play_music(*args):
    if os.path.exists('music'):
        files = os.listdir('music')
        random_file = f'music/{random.choice(files)}'
        tts.play_speech(f'Воспроизведение файла "{random_file.split("/")[-1]}"')
        os.system(f'start {random_file}')
    else:
        print('Добавьте в папку проекта папку "music".')


def what_a_time(*args):
    current_hour = current_time.hour
    current_minute = current_time.minute
    tts.play_speech(f'Сейчас {current_hour}:{current_minute}')


def timer(*args):
    time_to = args[0]
    local_time = 1 # по умолчанию 1 минуту
    multiplier = 60 # по умолчанию таймер ставим на минуты, потому множитель 60
    plur = 'минуту'
    if time_to:
        data = str(time_to).split(' ')
        for x in data:
            if x.isnumeric():
                local_time = float(x)
            if 'час' in x:
                multiplier = 3600 # чтобы получить нужное количество часов
                plur = x
            if 'минут' in x:
                multiplier = 60 # чтобы получить нужное количество минут
                plur = x
            if 'сек' in x:
                multiplier = 1 # чтобы получить нужное количество секунд
                plur = x    
    tts.play_speech(f'таймер установлен на {int(local_time)} {plur}')
    time.sleep(local_time * multiplier)
    tts.play_speech(f'таймер на {int(local_time)} {plur} закончился')


def search_on_wiki(*args):
    if not args:
        tts.play_speech('вы не сказали, что нужно найти')
    keyphrase = args[0]
    wk = search_funcs.Wikisearcher()
    answer = wk.get_wiki_info(user.language, keyphrase)
    tts.play_speech(answer)


def get_weather(*args):
    if not args or len(args[0]) < 2:
        city = user.homecity
    else:
        city = args[0]
    
    weather = search_funcs.Weatherer()
    answer = weather.get_weather_info(city)
    tts.play_speech(answer)


# упрощенный словарь для вызова функций
commands = {
    'greetings': greetings,
    'create_task': create_task,
    'play_music': play_music,
    'what_a_time': what_a_time,
    'timer': timer,
    'search_on_wiki': search_on_wiki,
    'get_weather': get_weather,
    'farewell_and_quit': farewell_and_quit,
}


# инвертируем словарь команд для упрощения и более быстрой работы
comm_dict = service_funcs.DictInverter.invert_commands_dict(commands_dict)


# основная функция
def main():
    while True:
        print('ожидаю...')
        matcher = service_funcs.Matcher()
        query: str = sr.listen_commands()
        if query:
            divided_query = query.split(' ', 1)
            command_options = ''
            if len(divided_query) > 1:
                assistant_name, command = divided_query
                for name in assistant_names:
                    if matcher.query_match(assistant_name, name):
                        assistant_name = name
                        for key in comm_dict.keys():
                            if key in command:
                                func = key
                                command_options = command.replace(key, '').strip()
                    if assistant_name not in assistant_names:
                        continue
                commands[comm_dict.get(func)](command_options)
            else:
                tts.play_speech('повторите запрос')


if __name__ == '__main__':
    main()