# объекты для данных и настроек пользователей

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    name: str = 'Unknown'
    surname: str = 'Unknown'
    homecity: str = 'Unknown'
    age: str or int = 'Unknown'
    sex: str = 'Unknown'
    speciality: str = 'Unknown'
    language: str = 'Unknown'
    second_language: str = 'Unknown'