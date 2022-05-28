import webbrowser
import speech_recognition as s_r # распознавание речи в текст
from vosk import Model, KaldiRecognizer as Kaldi # оффлайн-распознавание
import pyttsx3 # синтез речи
import wave, json, os # работа с wav, json, файловой системой

class Vox:

    # настройки голосового помощника, включая имя, пол, язык речи
    name = ''
    sex = ''
    speech_lang = ''
    recognition_lang = ''


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
            return

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
        if not os.path.exists('models/vosk-model-small-ru-0.4'):
            print('Пожалуйста загрузите модель языка отсюда:\n'
                  'https://alphacephei.com/vosk/models and unpack as "model" in the current folder.')
            exit(1)

        # распознавание записанного через микрофон аудио во избежание повторов
        wav_audio_file = wave.open('microphone-results.wav', 'rb')
        model = Model('models/vosk-model-small-ru-0.4')
        offline_recognizer = Kaldi(model, wav_audio_file.getframerate())

        data = wav_audio_file.readframes(wav_audio_file.getnframes())
        if len(data) > 0:
            if offline_recognizer.AcceptWaveform(data):
                recognized_data = offline_recognizer.Result()

                # получение распознанного текста из json-строки
                recognized_data = json.loads(recognized_data)
                recognized_data = recognized_data['text']
    except:
        print('Сервис распознавания недоступен')

    return recognized_data


# команды ассистенту

def search_on_youtube(*args: tuple):

    # поиск видео на ютубе

    if not args[0]:
        return
    print(args[0])
    search_query = ' '.join(args[0])
    url = 'https://www.youtube.com/results?search_query=' + search_query
    webbrowser.get().open(url)

    # для мультиязычности лучше создать отдельный класс для перевода из JSON-файла
    return 'Вот что я нашла по запросу' + search_query + 'на youtube'


def search_standart_on_cntd(*args: tuple):

    # поиск стандартов в электронном фонде docs.cntd.ru
    if not args[0]:
        return
    search_query = ' '.join(args[0])
    url = 'https://docs.cntd.ru/search?q=' + search_query
    webbrowser.get().open(url)

    return 'Вот что нашлось по запросу' + voice_input[0] + search_query


commands = {
    #("hello", "hi", "morning", "привет"): play_greetings,
    #("bye", "goodbye", "quit", "exit", "stop", "пока"): play_farewell_and_quit,
    #("search", "google", "find", "найди"): search_for_term_on_google,
    ('video', 'youtube', 'watch', 'видео', 'ютуб'): search_on_youtube,
    ('гост', 'стандарт', 'снип', 'ту'): search_standart_on_cntd,
    #("wikipedia", "definition", "about", "определение", "википедия"): search_on_wikipedia,
    #("translate", "interpretation", "translation", "перевод", "перевести", "переведи"): get_translation,
    #("language", "язык"): change_language,
    #("weather", "forecast", "погода", "прогноз"): get_weather_forecast,
}


def execute_named_commands(command_name: str, *args: list):

    # Выполнение заданной пользователем команды с дополнительными аргументами

    for key in commands.keys():
        if command_name in key:
            play_vox_assistant_speech(commands[key](*args))
        else:
            #play_vox_assistant_speech('Я такого пока не умею')
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
    assistant.name = 'Nora'
    assistant.sex = 'female'
    assistant.speech_lang = 'ru'

    setup_vox_voice()

    while True:

        # старт записи речи с последующим выводом распознанной речи
        # и удалением записанного в микрофон аудио
        voice_input = record_and_recognize()
        os.remove('microphone-results.wav')
        print(voice_input)

        # выделение команд от аргументов
        # первое слово - основная команда, остальные слова аргументы для поисковой фразы
        voice_input = voice_input.split(' ')
        command = voice_input[0]

        command_args = [str(ask_part) for ask_part in voice_input[1:len(voice_input)]]
        execute_named_commands(command, command_args)