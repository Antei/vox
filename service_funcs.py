from itertools import chain, product

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