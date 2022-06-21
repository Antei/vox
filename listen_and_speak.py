import speech_recognition
from vosk import Model, KaldiRecognizer as Kaldi, SetLogLevel
import pyttsx3

import os
import json
import wave

class Listener:
    def __init__(self):
        self.mic = speech_recognition.Microphone()
        self.sr = speech_recognition.Recognizer()
        self.sr.pause_threshold = 0.5


    def listen_commands(self):
        rec_data = ''
        with self.mic:
            self.sr.adjust_for_ambient_noise(source=self.mic, duration=0.5)
            print('говорите...')
            audio = self.sr.listen(source=self.mic)
        try:
            rec_data = self.sr.recognize_google(audio_data=audio, language='ru-RU').lower()
        except speech_recognition.UnknownValueError:
            pass
        except speech_recognition.WaitTimeoutError:
            pass  
        except speech_recognition.RequestError:
            print('Нет сети, пробую распознать офлайн...')
            with open('audio_data.wav', 'wb') as file:
                file.write(audio.get_wav_data())
            off_rec = Offline_recognizer()
            rec_data = off_rec.offline_recognition()
        return rec_data


class Offline_recognizer:
    def __init__(self):
        SetLogLevel(-1) # отключаем спам лога в терминал
        

    def offline_recognition(self):
        recognized_data = ''
        try:
            # проверка наличия модели нужного языка
            if not os.path.exists(f'models/vosk-model-small-ru-0.22'):
                print('''Пожалуйста загрузите модель языка отсюда:\n
                        https://alphacephei.com/vosk/models\n
                        ...и распакуйте "model" в соответствующую папку.''')
                exit(1)
            # распознавание записанного аудио
            with wave.open('audio_data.wav', 'rb') as wav_file:
                self.model = Model(f'models/vosk-model-small-ru-0.22')
                self.offline_sr = Kaldi(self.model, wav_file.getframerate())
                data = wav_file.readframes(wav_file.getnframes())
                if len(data) > 0:
                    if self.offline_sr.AcceptWaveform(data):
                        recognized_data = self.offline_sr.Result()
                        recognized_data = json.loads(recognized_data)
                        recognized_data = recognized_data['text']
        except:
            print('Ошибка распознавания')
        if os.path.exists('audio_data.wav'):
            os.remove('audio_data.wav')
        return recognized_data


class Speaker:
    def __init__(self):
        # настройки преобразования текста в речь
        self.engine = pyttsx3.init()

    def play_speech(self, text_to_speech):
        # Воспроизведение речи
        self.engine.say(str(text_to_speech))
        self.engine.runAndWait()

    def stop_speech(self):
        self.engine.stop()