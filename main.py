import os
import random
import time
from datetime import datetime
import itertools

# подключаем преобразование речи в текст и текста в речь
from listen_and_speak import Listener, Speaker
# подключаем команды и имена ассистента
from commands import assistant_names, commands_dict


current_time = datetime.now()
sr = Listener()
tts = Speaker()


def greetings():
    # приветствие, случайное, в зависимости от времени суток
    greetings = ['добрый день', 'привет', 'здравствуйте',
                 'приветствую', 'добрый вечер']
    current_hour = current_time.hour

    if 5 < current_hour < 11:
        greetings = greetings[2:-1]
        greetings.append('доброе утро')
        tts.play_speech(random.choice(greetings))
    elif 11 < current_hour < 17:
        tts.play_speech(random.choice(greetings[:-1]))
    elif current_hour > 17:
        tts.play_speech(random.choice(greetings[1:]))


def create_task():
    tts.play_speech('что нужно добавить в заметку?')
    note = sr.listen_commands()

    if note:
        with open('todo-list.txt', 'a', encoding='UTF-8') as file:
            file.write(f'- {note}\n')
        tts.play_speech(f'Задача "{note}" успешно добавлена в список дел.')
    else:
        tts.play_speech('Нет данных для добавления')


def play_music():
    if os.path.exists('music'):
        files = os.listdir('music')
        random_file = f'music/{random.choice(files)}'
        tts.play_speech(f'Воспроизведение файла "{random_file.split("/")[-1]}"')
        os.system(f'start {random_file}')
    else:
        print('Добавьте в папку проекта папку "music".')


def what_a_time():
    current_hour = current_time.hour
    current_minute = current_time.minute
    tts.play_speech(f'Сейчас {current_hour}:{current_minute}')


def timer():
    tts.play_speech('на сколько ставить таймер?')
    time_to = sr.listen_commands()
    local_time = 1 # по умолчанию 1 минуту
    multiplier = 60 # по умолчанию таймер ставим на минуты, потому множитель 60
    plur = 'минуту'
    if time_to:
        data = str(time_to).split(' ')
        for x in data:
            if x.isnumeric():
                local_time = float(x)
            if x in {'часов', 'часа', 'час'}:
                multiplier = 3600 # чтобы получить нужное количество часов
                plur = x
            if x in {'минут', 'минуты', 'минуту'}:
                multiplier = 60 # чтобы получить нужное количество минут
                plur = x
            if x in {'секунд', 'секунду', 'секунды'}:
                multiplier = 1 # чтобы получить нужное количество секунд
                plur = x    
    tts.play_speech(f'таймер установлен на {int(local_time)} {plur}')
    time.sleep(local_time * multiplier)
    tts.play_speech(f'таймер на {int(local_time)} {plur} закончился')


def farewell_and_quit():
    # прощание в зависимости от времени суток и выход из программы
    farewells = ['доброго дня', 'всего доброго', 'пока',
                 'до встречи', 'хорошего вечера']
    current_hour = current_time.hour
    if current_hour < 17:
        tts.play_speech(random.choice(farewells[:-2]))
    elif current_hour > 17:
        tts.play_speech(random.choice(farewells[1:-1]))
    elif current_hour > 22:
        farewells = farewells[1:-2]
        farewells.append('доброй ночи')
        tts.play_speech(random.choice(farewells))
    tts.stop_speech()
    quit()


def invert_commands_dict(commands_dict):
    inverted_commands_dict = dict(itertools.chain.from_iterable(itertools.product(v, [k]) for k, v in commands_dict.items()))
    return inverted_commands_dict


# упрощенный словарь для вызова функций
commands = {
    'greetings': greetings,
    'create_task': create_task,
    'play_music': play_music,
    'what_a_time': what_a_time,
    'timer': timer,
    'farewell_and_quit': farewell_and_quit,
}


# основная функция
def main():
    comm_dict = invert_commands_dict(commands_dict)
    while True:
        print('ожидаю...')
        query = sr.listen_commands()
        if query:
            divided_query = str(query).split(' ', 1)
            if len(divided_query) > 1:
                assistant_name, command = divided_query
                print(assistant_name, command, sep='\n')
                if assistant_name not in assistant_names:
                    continue
                commands[comm_dict.get(command)]()
            else:
                tts.play_speech('повторите запрос')
        if os.path.exists('audio_data.wav'):
            os.remove('audio_data.wav')


if __name__ == '__main__':
    main()