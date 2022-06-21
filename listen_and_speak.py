import speech_recognition
import pyttsx3


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
        self.engine = pyttsx3.init()

    def play_speech(self, text_to_speech):
        # Воспроизведение речи
        self.engine.say(str(text_to_speech))
        self.engine.runAndWait()

    def stop_speech(self):
        self.engine.stop()