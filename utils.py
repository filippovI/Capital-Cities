import random

from cities_dicts import CD


def shuffle_dict(data: dict):
    # Создаем словарь перемешанных вопросов и ответов
    cities: dict = {}

    # Список вариантов материков
    data_list: list = [i for i in data["name"].strip(' ').split(' ') if i]

    # Исходя из списка вариантов и основного словаря со столицами CD обновляем cities
    for i in data_list:
        cities.update(CD[int(i)])
    keys: list = list(cities.keys())
    random.shuffle(keys)
    return list({k: cities[k] for k in keys}.keys()), list({k: cities[k] for k in keys}.values())

