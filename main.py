import speech_recognition as s_r # распознавание речи в текст
from vosk import Model, KaldiRecognizer as Kaldi, SetLogLevel # оффлайн-распознавание
import pyttsx3 # синтез речи

import wave, json, os, webbrowser # работа с wav, json, файловой системой, браузером
import random # использование случайных фраз из наборов и возможно не только
import traceback # вывод traceback без остановки работы программы при отлове исключений
from datetime import datetime # для ответов в соответствии с системным временем суток

# немного машинного обучения
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC

# окрашивание сообщений
from termcolor import colored

# выделим файлы с настройками отдельно


# функции по отдельным категориям для удобства


# классы

class Vox:

    # настройки голосового помощника, включая имя, пол, язык речи
    name = ''
    sex = ''
    speech_lang = ''
    recognition_lang = ''


class Owner:
    """
    информация о владельце, включая имя, город, родной язык, второй язык для перевода
    """
    
    name = ''
    city = ''
    native_lang = ''
    second_lang = ''


class Translation:

    # интегрированный перевод строк ru, en

    with open('translations.json', 'r', encoding='UTF-8') as file:
        translations = json.load(file)

    def get_translation(self, text: str):
        """
        получение перевода строки из файла на нужный язык
        : param text: текст на перевод
        : return: интегрированный перевод
        """ 
        if text in self.translations:
            return self.translations[text][assistant.speech_lang]
        else:
            # если нет готового перевода, выводим сообщение об этом
            print(f'Нет переведенной фразы: {text}')
            return text


def setup_vox_voice():
    
    # Установка голоса по умолчанию, может меняться в зависимости от настроек системы

    voices = tts_engine.getProperty('voices')

    if assistant.speech_lang == 'ru':
        assistant.recognition_lang = 'ru-RU'
        # MS Irina - Ru
        tts_engine.setProperty('voice', voices[0].id)
    else:
        assistant.recognition_lang = 'en-US'
        if assistant.sex == 'female':
            # MS Zira - Eng
            tts_engine.setProperty('voice', voices[1].id)
        else:
            # MS David - Eng
            tts_engine.setProperty('voices', voices[2].id)


def play_speech(text_to_speech):

    # Воспроизведение ответов ассистента

    print(colored(str(text_to_speech), 'green'))
    tts_engine.say(str(text_to_speech))
    tts_engine.runAndWait()


def record_and_recognize(*args: tuple):

    # Запись и распознавание аудио
    with microphone:
        recognized_data = ''
        
        # регулирование уровня шума
        recognizer.adjust_for_ambient_noise(microphone, duration=2)

        try:
            print('Слушаю...')
            audio = recognizer.listen(microphone, 5, 5)

            with open('microphone-results.wav', 'wb') as file:
                file.write(audio.get_wav_data())

        except s_r.WaitTimeoutError:
            print('Проверьте, включен ли микрофон')
            traceback.print_exc()
            return

        # использование распознавания офлайн, не требует наличия интернета
        try:
            print('Обработка...')
            recognized_data = offline_recognition()
            
        except:
            try:
                recognized_data = recognizer.recognize_google(audio, language='ru').lower()
            
            except s_r.UnknownValueError:
                    pass

            # в случае не распознавания локально распознаем онлайн
            except s_r.RequestError:
                print('Пробую еще раз распознать офлайн')
                recognized_data = offline_recognition()

        return recognized_data


def offline_recognition():

    recognized_data = ''

    SetLogLevel(-1) # отключаем спам лога в терминал

    try:
        # проверка наличия модели нужного языка
        if not os.path.exists(f'models/vosk-model-small-{assistant.speech_lang}-0.22'):
            print('Пожалуйста загрузите модель языка отсюда:\n'
                  'https://alphacephei.com/vosk/models and unpack as "model" in the current folder.')
            exit(1)

        # распознавание записанного через микрофон аудио во избежание повторов
        wav_audio_file = wave.open('microphone-results.wav', 'rb')
        model = Model(f'models/vosk-model-small-{assistant.speech_lang}-0.22')
        offline_recognizer = Kaldi(model, wav_audio_file.getframerate())

        data = wav_audio_file.readframes(wav_audio_file.getnframes())
        if len(data) > 0:
            if offline_recognizer.AcceptWaveform(data):
                recognized_data = offline_recognizer.Result()

                # получение распознанного текста из json-строки
                recognized_data = json.loads(recognized_data)
                recognized_data = recognized_data['text']
                print(colored(recognized_data, 'blue'))
    except:
        print('Сервис распознавания недоступен')

    return recognized_data


def search_on_youtube(*args: tuple):

    # поиск видео на ютубе

    if not args[0]:
        return
    search_query = ' '.join(args[0])
    url = 'https://www.youtube.com/results?search_query=' + search_query
    webbrowser.get().open_new_tab(url)

    # для мультиязычности лучше создать отдельный класс для перевода из JSON-файла
    play_speech(
        f'Вот что есть по запросу {search_query} на ютубе'
        )


def search_standart_on_cntd(*args: tuple):

    # поиск стандартов в электронном фонде docs.cntd.ru
    if not args[0]:
        return
    search_query = ' '.join(args[0])
    url = 'https://docs.cntd.ru/search?q=' + search_query
    webbrowser.get().open_new_tab(url)

    play_speech(
        f'Вот что нашлось по запросу {voice_input[1]} {search_query}'
        )


def repeater(*args: tuple):
    
    # повторение услышанного
    try:
        if not args[0]:
            return
        text = ' '.join(args[0])
        play_speech(
            f'вы сказали: {text}'
        )
    except IndexError as err:
        play_speech('вы ничего не сказали для повторения')


def play_greetings(*args: tuple):
    """
    приветствие, случайное
    """
    greetings = ['доброе утро', 'добрый день',
                 'привет', 'здравствуйте', 'приветствую', 'добрый вечер']

    play_speech(f'{random.choice(greetings)}')


def failure_phrases(*args: tuple):
    """
    распознать команды не удалось или нет такой в функциях
    """
    fail_phrases = ['слушаю', 'не поняла запрос', 'непонятно']

    play_speech(f'{random.choice(fail_phrases)}')


def play_farewell_and_quit(*args: tuple):
    """
    прощание и выход из программы
    """
    farewells = ['доброго дня', 'всего доброго', 'пока',
                 'до встречи', 'хорошего вечера', 'доброй ночи']

    current_hour = datetime.now().hour
    if current_hour < 17:
        play_speech(f'{random.choice(farewells[:-2])}')
    elif current_hour > 17:
        play_speech(f'{random.choice(farewells[1:-1])}')
    elif current_hour > 22:
        farewells = farewells[1:-2]
        farewells.append('доброй ночи')
        play_speech(f'{random.choice(farewells)}')
    
    tts_engine.stop()
    quit()


config = {
    'intents': {
        "greeting": {
            "examples": ['привет', 'здравствуй', 'добрый день',
                         'hello', 'good morning'],
            "responses": play_greetings
        },
        'youtube_search': {
            'examples': ['video', 'youtube', 'watch', 'видео',
                         'ютуб', 'найди видео', 'покажи видео', 'find video',
                         'find on youtube', 'search on youtube'],
            'responses': search_on_youtube
        },
        'standarts_search': {
            'examples': ['найди мне гост', 'найди мне стандарт',
                         'найди гост', 'найди стандарт'],
            'responses': search_standart_on_cntd
        },
        'repeater': {
            'examples': ['повтори', 'repeat', 'повтори-ка', 'повторить', 'повтор'],
            'responses': repeater
        },
        "farewell": {
            "examples": ["пока", "до свидания", "увидимся", "до встречи",
                         "goodbye", "bye", "see you soon"],
        "responses": play_farewell_and_quit
        },
        #"google_search": {
        #    "examples": ["найди в гугл",
        #                 "search on google", "google", "find on google"],
        #    "responses": search_for_term_on_google
        #},
    },
    "failure_phrases": failure_phrases
}


def prepare_intent():
    """
    Подготовка модели для угадывания намерения пользователя
    """

    intent = []
    target_vector = []
    for intent_name, intent_data in config['intents'].items():
        for example in intent_data['examples']:
            intent.append(example)
            target_vector.append(intent_name)

    training_vector = vectorizer.fit_transform(intent)
    classifier_probability.fit(training_vector, target_vector)
    classifier.fit(training_vector, target_vector)


def get_intent(request):
    """
    Получение наиболее вероятного намерения в зависимости от запроса пользователя
    :param request: запрос пользователя
    :return наиболее вероятное намерение
    """

    best_intent = classifier.predict(vectorizer.transform([request]))[0]

    index_of_best_intent = list(classifier_probability.classes_).index(best_intent)
    probabilities = classifier_probability.predict_proba(vectorizer.transform([request]))[0]

    best_intent_probability = probabilities[index_of_best_intent]

    # при добавлении новых намерений НУЖНО уменьшать показатель, 
    # иначе будут распознаваться не все функции
    if best_intent_probability > 0.157:
        return best_intent


def prepare():
    """
    подготовка глобальных переменных к запуску приложения
    """

    global recognizer, microphone, tts_engine, person, assistant, translator, vectorizer, classifier, classifier_probability

    # инициализация распознавания и ввода речи
    recognizer = s_r.Recognizer()
    microphone = s_r.Microphone()

    # инициализация синтеза речи
    tts_engine = pyttsx3.init()

    # пользователь
    person = Owner()
    person.name = 'Nikita'
    person.city = 'Sankt-Peterburg'
    person.native_lang = 'ru'
    person.second_lang = 'en'

    # настройка ассистента
    assistant = Vox()
    assistant.name = ('пятница')
    assistant.sex = 'female'
    assistant.speech_lang = 'ru'

    setup_vox_voice()

    # переводчик ru-en
    translator = Translation()

    vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 3))
    classifier_probability = LogisticRegression()
    classifier = LinearSVC()
    prepare_intent()


if __name__ == '__main__':

    prepare()

    # инициализация распознавания и ввода речи
    recognizer = s_r.Recognizer()
    microphone = s_r.Microphone()

    # инициализация синтеза речи
    tts_engine = pyttsx3.init()

    # настройка ассистента
    assistant = Vox()
    assistant.name = ('пятница')
    assistant.sex = 'female'
    assistant.speech_lang = 'ru'

    # переводчик ru-en
    translator = Translation()

    setup_vox_voice()

    vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 3))
    classifier_probability = LogisticRegression()
    classifier = LinearSVC()
    prepare_intent()

    while True:

        # старт записи речи с последующим выводом распознанной речи
        # и удалением записанного в микрофон аудио
        voice_input = record_and_recognize()
        
        if os.path.exists('microphone-results.wav'):
            os.remove('microphone-results.wav')

        # выделение команд от аргументов
        # первое слово -  команда, остальные слова аргументы для поисковой фразы
        if voice_input:
            voice_input_parts = voice_input.split(' ')
            print(colored(voice_input_parts, 'yellow'), len(voice_input_parts))

            if len(voice_input_parts) == 1:

                intent = get_intent(voice_input)

                if intent:
                    config['intents'][intent]['responses']()
                else:
                    config['failure_phrases']()

            """
            в случае длинной фразы - выполняется поиск ключевой фразы
            и аргументов через каждое слово, пока не будет найдено совпадение
            """
            
            if len(voice_input_parts) > 1:
                for guess in range(len(voice_input_parts)):
                    intent = get_intent((' '.join(voice_input_parts[1:guess])).strip())
                    print(colored(guess, 'cyan'), intent, sep='\n')
                    print(colored((' '.join(voice_input_parts[0: guess])).strip(), 'blue'))

                    if intent:
                        command_options = [voice_input_parts[guess:len(voice_input_parts)]]
                        print(colored(command_options, 'magenta'))
                        config['intents'][intent]['responses'](*command_options)
                        break
                    if not intent and guess == len(voice_input_parts)-1:
                        config['failure_phrases']()