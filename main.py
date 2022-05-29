import speech_recognition as s_r # распознавание речи в текст
from vosk import Model, KaldiRecognizer as Kaldi # оффлайн-распознавание
import pyttsx3 # синтез речи
import wave, json, os, webbrowser # работа с wav, json, файловой системой, браузером

class Vox:

    # настройки голосового помощника, включая имя, пол, язык речи
    name = ''
    sex = ''
    speech_lang = ''
    recognition_lang = ''


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

    if assistant.speech_lang == 'en':
        assistant.recognition_lang = 'en-US'
        if assistant.sex == 'female':
            # MS Zira - Eng
            tts_engine.setProperty('voice', voices[1].id)
        else:
            # MS David - Eng
            tts_engine.setProperty('voices', voices[2].id)
    else:
        assistant.recognition_lang = 'ru-RU'
        # MS Irina - Ru
        tts_engine.setProperty('voice', voices[0].id)


def play_vox_assistant_speech(text_to_speech):

    # Воспроизведение ответов ассистента

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

            with open('microphone-results.wav', 'wb') as speech:
                speech.write(audio.get_wav_data())

        except s_r.WaitTimeoutError:
            print('Проверьте, включен ли микрофон')
            record_and_recognize()

        # использование распознавания через гугл, требует наличия интернета
        try:
            print('Обдумываю услышанное...')
            recognized_data = recognizer.recognize_google(audio, language='ru').lower()

        except s_r.UnknownValueError:
            pass

        # в случае проблем с доступом в интернет выдаем ошибку
        except s_r.RequestError:
            print('Пробую распознать без сети')
            recognized_data = offline_recognition()

        return recognized_data


def offline_recognition():

    # переключение на оффлайн-распознавание речи

    recognized_data = ''

    try:
        # проверка наличия модели нужного языка
        if not os.path.exists('models/vosk-model-small-ru-0.22'):
            print('Пожалуйста загрузите модель языка отсюда:\n'
                  'https://alphacephei.com/vosk/models and unpack as "model" in the current folder.')
            exit(1)

        # распознавание записанного через микрофон аудио во избежание повторов
        wav_audio_file = wave.open('microphone-results.wav', 'rb')
        model = Model('models/vosk-model-small-ru-0.22')
        offline_recognizer = Kaldi(model, wav_audio_file.getframerate())

        data = wav_audio_file.readframes(wav_audio_file.getnframes())
        if len(data) > 0:
            if offline_recognizer.AcceptWaveform(data):
                recognized_data = offline_recognizer.Result()
                print(recognized_data)

                # получение распознанного текста из json-строки
                recognized_data = json.loads(recognized_data)
                recognized_data = recognized_data['text']
                print(recognized_data)
    except:
        print('Сервис распознавания недоступен')

    return recognized_data


# команды ассистенту

def search_on_youtube(*args: tuple):

    # поиск видео на ютубе

    if not args[0]:
        return
    search_query = ' '.join(args[0])
    url = 'https://www.youtube.com/results?search_query=' + search_query
    webbrowser.get().open_new_tab(url)

    # для мультиязычности лучше создать отдельный класс для перевода из JSON-файла
    play_vox_assistant_speech(translator.get_translation(
        f'Вот что есть по запросу {search_query} на ютубе'
        ))


def search_standart_on_cntd(*args: tuple):

    # поиск стандартов в электронном фонде docs.cntd.ru
    if not args[0]:
        return
    search_query = ' '.join(args[0])
    url = 'https://docs.cntd.ru/search?q=' + search_query
    webbrowser.get().open_new_tab(url)

    play_vox_assistant_speech(translator.get_translation(
        f'Вот что нашлось по запросу {voice_input[1]} {search_query}'
        ))


def repeater(*args: tuple):
    
    # повторение услышанного
    if not args[0]:
        return
    text = ' '.join(args[0])
    play_vox_assistant_speech(
        f'повторяю, вы сказали: {text}'
    )


commands = {
    #("hello", "hi", "morning", "привет"): play_greetings,
    #("bye", "goodbye", "quit", "exit", "stop", "пока"): play_farewell_and_quit,
    #("search", "google", "find", "найди"): search_for_term_on_google,
    ('video', 'youtube', 'watch', 'видео', 'ютуб'): search_on_youtube,
    ('гост', 'стандарт', 'снип', 'iso', 'gost',): search_standart_on_cntd,
    ('повтори', 'repeat', 'повтори-ка', 'повторить', 'повтор'): repeater,
    #("wikipedia", "definition", "about", "определение", "википедия"): search_on_wikipedia, # 'https://ru.wikipedia.org/w/index.php?search='
    #("translate", "interpretation", "translation", "перевод", "перевести", "переведи"): get_translation,
    #("language", "язык"): change_language,
    #("weather", "forecast", "погода", "прогноз"): get_weather_forecast,
}


def execute_named_commands(command_name: str, *args: list):

    # Выполнение заданной пользователем команды с дополнительными аргументами

    for key in commands.keys():
        if command_name in key:
            commands[key](*args)
        else:
            print('команда не найдена')


# задел


if __name__ == '__main__':

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

    while True:

        # старт записи речи с последующим выводом распознанной речи
        # и удалением записанного в микрофон аудио
        voice_input = record_and_recognize()
        try:
            os.remove('microphone-results.wav')
        except FileNotFoundError:
            pass
        print(voice_input)

        # выделение команд от аргументов
        # первое слово - команда активации, второе - команда, остальные слова аргументы для поисковой фразы
        voice_input = voice_input.split(' ')
        
        if len(voice_input) > 1:
            print(voice_input[0])
            if voice_input[0] in assistant.name:
                command = voice_input[1]

                command_args = [str(ask_part) for ask_part in voice_input[2:len(voice_input)]]
                print(command, command_args, sep='\n')
                execute_named_commands(command, command_args)
        if len(voice_input) == 1 and voice_input[0] in assistant.name:
            play_vox_assistant_speech('я вас внимательно слушаю')