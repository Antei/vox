import speech_recognition
import os
import random
import pyttsx3
from datetime import datetime
import time
from threading import Thread


sr = speech_recognition.Recognizer()
sr.pause_threshold = 0.5


def listen_commands():

    try:
        with speech_recognition.Microphone() as mic:
            sr.adjust_for_ambient_noise(source=mic, duration=0.5)
            audio = sr.listen(source=mic)
            rec_data = sr.recognize_google(audio_data=audio, language='ru-RU').lower()
        return rec_data

    except speech_recognition.UnknownValueError:
        return 'Ошибка распознавания'

    except speech_recognition.WaitTimeoutError:
        return
    
    except speech_recognition.RequestError:
        return 'Нет сети'


def play_speech(text_to_speech):

    # Воспроизведение ответов ассистента

    tts_engine = pyttsx3.init()

    tts_engine.say(str(text_to_speech))
    tts_engine.runAndWait()


def greetings():

    # приветствие, случайное, в зависимости от времени суток

    greetings = ['добрый день', 'привет', 'здравствуйте',
                 'приветствую', 'добрый вечер']
    current_hour = current_time.hour

    if 5 < current_hour < 11:
        greetings = greetings[2:-1]
        greetings.append('доброе утро')
        return play_speech(random.choice(greetings))
    elif 11 < current_hour < 17:
        return play_speech(random.choice(greetings[:-1]))
    elif current_hour > 17:
        return play_speech(random.choice(greetings[1:]))


def create_task():

    play_speech('что нужно добавить в заметку?')

    note = listen_commands()

    if note != 'Ошибка распознавания' or None:
        with open('todo-list.txt', 'a', encoding='UTF-8') as file:
            file.write(f'- {note}\n')

        return play_speech(f'Задача "{note}" успешно добавлена в список дел.')
    else:
        return play_speech('Нет данных для добавления')


def play_music():

    if os.path.exists('music'):
        files = os.listdir('music')
        random_file = f'music/{random.choice(files)}'
        play_speech(f'Воспроизведение файла "{random_file.split("/")[-1]}"')
        os.system(f'start {random_file}')
    else:
        print('Добавьте в папку проекта папку "music".')

    return


def what_a_time():

    current_hour = current_time.hour
    current_minute = current_time.minute
    return play_speech(f'Сейчас {current_hour}:{current_minute}')


def timer():

    play_speech('на сколько ставить таймер?')

    time_to = listen_commands()

    local_time = 5 # по умолчанию 5 минут
    multiplier = 60 # по умолчанию таймер ставим на минуты, потому множитель 60
    plur = 'минут'

    if time_to != 'Ошибка распознавания':
        data = str(time_to).split(' ')
        for x in data:
            if x.isnumeric():
                local_time = int(x)
            if x in {'часов', 'часа', 'час'}:
                multiplier = 3600 # чтобы получить нужное количество часов
                plur = x
            if x in {'минут', 'минуты', 'минуту'}:
                multiplier = 60 # чтобы получить нужное количество минут
                plur = x
            if x in {'секунд', 'секунду', 'секунды'}:
                multiplier = 1 # чтобы получить нужное количество секунд
                plur = x    
    
    play_speech(f'таймер установлен на {str(local_time)} {plur}')
    print(local_time * multiplier)
    time.sleep(local_time * multiplier)
    return play_speech(f'таймер на {str(local_time)} {plur} закончился')


def play_farewell_and_quit():
    
    # прощание в зависимости от времени суток и выход из программы
    
    farewells = ['доброго дня', 'всего доброго', 'пока',
                 'до встречи', 'хорошего вечера']
    current_hour = current_time.hour

    if current_hour < 17:
        play_speech(random.choice(farewells[:-2]))
    elif current_hour > 17:
        play_speech(random.choice(farewells[1:-1]))
    elif current_hour > 22:
        farewells = farewells[1:-2]
        farewells.append('доброй ночи')
        play_speech(random.choice(farewells))
    
    #tts_engine.stop()
    quit()


commands_list = {
    'commands': {
        greetings: {'привет', 'здравствуй', 'доброе утро', 
                      'добрый день', 'добрый вечер', 'здарова'},
        create_task: {'добавь задачу', 'заметка', 'добавь в список дел', 'создай запись', 
                        'добавь заметку', 'создай заметку', 'добавь запись'},
        play_music: {'включи музыку', 'включи что-нибудь из музыки'},
        what_a_time: {'сколько времени', 'который час'},
        play_farewell_and_quit: {'пора спать', 'пока', 
                                 'доброй ночи', 'выключайся'},
        timer: {'поставь таймер', 'включи таймер', 'таймер'}
        },
    'assistant_names': ['пятница', 'friday', 'эй пятница']
}


def main():

    print('ожидаю...')
    query = listen_commands()
    data = str(query).split(" ")

    if data[0] in commands_list['assistant_names']:
        for key, value in commands_list['commands'].items():
            if ' '.join(data[1:]) in value:                
                if key == timer:
                    th = Thread(target=timer, args=()) # создаем новый поток для таймера
                    th.start()
                else:
                    key()


if __name__ == '__main__':

    #tts_engine = pyttsx3.init()
    current_time = datetime.now()

    while True:

        main()