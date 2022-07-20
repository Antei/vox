from itertools import chain, product
import re

import nltk

# сервисные функции программы

class Pluralizer:
    pass

class Unpacker:
    pass

class DictInverter:
    # инвертируем словарь комманд в удобоисполняемый
    def invert_commands_dict(commands_dict: dict):
        inverted_commands_dict = dict(chain.from_iterable(product(v, [k]) for k, v in commands_dict.items()))
        return inverted_commands_dict

class Matcher:
    # унифицирование текста на предмет опечаток
    def __init__(self):
        pass
    
    def prepare_query(self, text: str):
    # приведение к нижнему регистру на всякий случай
        text = text.strip().lower()
        re_not_word = r'\w\s'
        text = re.sub(re_not_word, '', text)
        return text


    def query_match(self, query: str, func_name: str):
        # приведение к единому регистру
        query = self.prepare_query(query)
        func_name = self.prepare_query(func_name)

        # если пример найден в запросе и наоборот
        if query.find(func_name) != -1:
            return True

        if func_name.find(query) != -1:
            return True

        difference = nltk.edit_distance(query, func_name)
        percent_of_difference = round(difference / len(func_name), 2)
        # если разница в символах составляет не более 33% (ниже как 0.33) то считаем что запрос и команда совпадают
        return percent_of_difference < 0.33


    def get_intent(self, text: str, comms: dict):
        # поиск команды в словаре команд
        for intent in comms:
            if self.query_match(text, intent):
                self.intent, self.text = intent, text
                return self.intent, self.text