import speech_recognition
import os
import random
import pyttsx3
from termcolor import colored
from datetime import datetime

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
    
    except speech_recognition.RequestError:
        return 'Нет сети'


def play_speech(text_to_speech):

    # Воспроизведение ответов ассистента

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
        play_speech(random.choice(greetings))
    elif 11 < current_hour < 17:
        play_speech(random.choice(greetings[:-1]))
    elif current_hour > 17:
        play_speech(random.choice(greetings[1:]))


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

    files = os.listdir('music')
    random_file = f'music/{random.choice(files)}'
    play_speech(f'Воспроизведение файла "{random_file.split("/")[-1]}"')
    os.system(f'start {random_file}')

    return


def what_a_time():

    current_hour = current_time.hour
    current_minute = current_time.minute
    return play_speech(f'Сейчас {current_hour}:{current_minute}')


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
    
    tts_engine.stop()
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
                                 'доброй ночи', 'выключайся'}
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
                key()


if __name__ == '__main__':

    tts_engine = pyttsx3.init()
    current_time = datetime.now()

    while True:

        main()