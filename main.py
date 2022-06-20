import os
import random
import time
from datetime import datetime
from threading import Thread
import itertools

import pyttsx3
import speech_recognition

# подключаем команды ассистента
from commands import assistant_names, commands_dict

current_time = datetime.now()


class Listener:
    def __init__(self):
        self.mic = speech_recognition.Microphone()
        self.sr = speech_recognition.Recognizer()
        self.sr.pause_threshold = 0.5

    def listen_commands(self):
        try:
            with self.mic:
                self.sr.adjust_for_ambient_noise(source=self.mic, duration=0.5)
                print('говорите...')
                audio = self.sr.listen(source=self.mic)
                rec_data = self.sr.recognize_google(audio_data=audio, language='ru-RU').lower()
            return rec_data
        except speech_recognition.UnknownValueError:
            pass
        except speech_recognition.WaitTimeoutError:
            pass  
        except speech_recognition.RequestError:
            print('Нет сети')


class Speaker:
    def __init__(self):
        # настройки преобразования текста в речь
        self.tts = pyttsx3.init()

    def play_speech(self, text_to_speech):
        # Воспроизведение речи
        self.tts.say(str(text_to_speech))
        self.tts.runAndWait()

    def stop_speech(self):
        self.tts.stop()


def greetings():
    # приветствие, случайное, в зависимости от времени суток
    greetings = ['добрый день', 'привет', 'здравствуйте',
                 'приветствую', 'добрый вечер']
    current_hour = current_time.hour

    if 5 < current_hour < 11:
        greetings = greetings[2:-1]
        greetings.append('доброе утро')
        Speaker().play_speech(random.choice(greetings))
    elif 11 < current_hour < 17:
        Speaker().play_speech(random.choice(greetings[:-1]))
    elif current_hour > 17:
        Speaker().play_speech(random.choice(greetings[1:]))


def create_task():
    Speaker().play_speech('что нужно добавить в заметку?')

    note = Listener().listen_commands()

    if note:
        with open('todo-list.txt', 'a', encoding='UTF-8') as file:
            file.write(f'- {note}\n')
        Speaker().play_speech(f'Задача "{note}" успешно добавлена в список дел.')
    else:
        Speaker().play_speech('Нет данных для добавления')


def play_music():
    if os.path.exists('music'):
        files = os.listdir('music')
        random_file = f'music/{random.choice(files)}'
        Speaker().play_speech(f'Воспроизведение файла "{random_file.split("/")[-1]}"')
        os.system(f'start {random_file}')
    else:
        print('Добавьте в папку проекта папку "music".')


def what_a_time():
    current_hour = current_time.hour
    current_minute = current_time.minute
    Speaker().play_speech(f'Сейчас {current_hour}:{current_minute}')


def timer():
    Speaker().play_speech('на сколько ставить таймер?')

    time_to = Listener().listen_commands()

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
    
    Speaker().play_speech(f'таймер установлен на {int(local_time)} {plur}')
    time.sleep(local_time * multiplier)
    Speaker().play_speech(f'таймер на {int(local_time)} {plur} закончился')


def farewell_and_quit():
    # прощание в зависимости от времени суток и выход из программы
    farewells = ['доброго дня', 'всего доброго', 'пока',
                 'до встречи', 'хорошего вечера']
    current_hour = current_time.hour

    if current_hour < 17:
        Speaker().play_speech(random.choice(farewells[:-2]))
    elif current_hour > 17:
        Speaker().play_speech(random.choice(farewells[1:-1]))
    elif current_hour > 22:
        farewells = farewells[1:-2]
        farewells.append('доброй ночи')
        Speaker().play_speech(random.choice(farewells))
    
    Speaker().stop_speech()
    quit()


def invert_commands_dict(commands_dict):
    inverted_commands_dict = dict(itertools.chain.from_iterable(itertools.product(v, [k]) for k, v in commands_dict.items()))
    return inverted_commands_dict


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
        query = Listener().listen_commands()
        if query:
            divided_query = str(query).split(' ', 1)
            if len(divided_query) > 1:
                assistant_name, command = divided_query
                print(assistant_name, command, sep='\n')
                if assistant_name not in assistant_names:
                    continue
                commands[comm_dict.get(command)]()
            else:
                Speaker().play_speech('повторите запрос')


if __name__ == '__main__':
    main()