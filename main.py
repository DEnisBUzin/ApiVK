import requests as rq
from urllib.parse import *
import json
from pprint import pprint
from typing import List, Dict
from datetime import date
import datetime
import logging

logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w", encoding='UTF-8')
# Нужно написать программу, которая будет:
# Получать фотографии с профиля. Для этого нужно использовать метод photos.get.
# Сохранять фотографии максимального размера(ширина/высота в пикселях) на Я.Диске.
# Для имени фотографий использовать количество лайков.
# Сохранять информацию по фотографиям в json-файл с результатами.

# Пользователь вводит:
# id пользователя vk;
# токен с Полигона Яндекс.Диска. Важно: Токен публиковать в github не нужно

# Обязательные требования к программе:
# Использовать REST API Я.Диска и ключ, полученный с полигона.
# Для загруженных фотографий нужно создать свою папку.
# Сохранять указанное количество фотографий(по умолчанию 5) наибольшего размера (ширина/высота в пикселях) на Я.Диске
# Сделать прогресс-бар или логирование для отслеживания процесса программы.
# Код программы должен удовлетворять PEP8.
# У программы должен быть свой отдельный репозиторий.
# Все зависимости должны быть указаны в файле requiremеnts.txt.
# # идентификатор пользователя vk
# https://oauth.vk.com/authorize?client_id=51864540&display=page&redirect_uri=http://example.com/callback&scope=friends&response_type=token&v=5.131&state=123456
# https://api.vk.com/method/

class ApiVKCopyPhoto:
    BASE_URL_VK = 'https://api.vk.com/method'
    BASE_URL_YANDEX = 'https://cloud-api.yandex.net'
    TOKEN = 'vk1.a.EwfLgnxLjmQasGnbEzsEh1azPKZQhnNzBtDr4dL7NNbypDqBne5SVMj26JO_nT2VgLyIWypMrGrLjjACc_EelbxrY_Rh6sUAMn7ylll6JtEKSCWtR6MzLxXTMpoo_jKduUkZ63XD3Nd81B40lCi4d4w8636Q4ds5eKMhIwHSgzyq6PP5yw7doAtG_3yoHNjL'

    def __init__(self, user_id: int, tokenYandex: str):
        self.token = tokenYandex
        self.user_id = user_id

    def  get_common_params(self) -> Dict:
        return {
            'access_token': self.TOKEN,
            'v': '5.199',
        }

    def get_photos(self, count_photos=5) -> Dict:
        '''Получение списка фотографий'''
        params = self.get_common_params()
        params.update({'album_id': 'profile',
                       'owner_id': self.user_id,
                       'extended': True,
                       'photo_sizes': 1,
                       'count': count_photos
                       })
        response = rq.get(f'{self.BASE_URL_VK}/photos.get', params=params)
        try:
            logging.info('Соединение установлено')
            return response.json()['response']['items']
        except KeyError:
            logging.critical('Необходимо обновить токен')


    def get_max_size_photos(self, count=5) -> Dict:
        '''Выбор из списка фотографии максимального размера'''
        dictMaxSizePhotos = {}
        for item in self.get_photos(count):
            val = item['sizes'][-1]['url']
            key = item['likes']['count']
            dictMaxSizePhotos.update({key: val})
        if len(dictMaxSizePhotos) < count:
            logging.warning(f'Количество фотографий в профиле пользователя меньше {count}')
            return dictMaxSizePhotos
        else:
            logging.info(f'Фотографии в количестве {count} успешно получены')
            return dictMaxSizePhotos

    def make_json(self, count=5):
        '''Создание JSON-файла с информацией о фотографиях'''
        lst_get_photos = self.get_photos(count)
        with open(f'inf_photo{date.today()}.json', 'w') as creat_json:
            lst_json = []
            for i in lst_get_photos:
                name = i['likes']['count']
                data = {
                    'file_name': f'{name}.jpg',
                    'size': i['sizes'][-1]['type']
                    }
                lst_json.append(data)
            json.dump(lst_json,creat_json)
            logging.info(f'Файл {creat_json} создан в текущей директории')

    def save_photos(self):
        '''Сохраняет фото в текущую директорию'''
        dict_save_photos = self.get_max_size_photos()
        self.make_json()
        for keyName, valURL in dict_save_photos.items():
            response = rq.get(valURL)
            name_image = f'{keyName}.jpg'
            with open(name_image, 'wb') as img:
                img.write(response.content)

    def make_dir_to_disk(self):
        url_make_dir = f'{self.BASE_URL_YANDEX}/v1/disk/resources'
        params = {
            'path': date.today()
        }
        headers = {
            'Authorization': self.token
        }
        response = rq.put(url_make_dir,
                          params=params,
                          headers=headers)
        logging.info(f'Новая папка {date.today()} создана')

    def upload_photos_to_disk(self):
        self.make_dir_to_disk()
        url_upload = f'{self.BASE_URL_YANDEX}/v1/disk/resources/upload'
        dict_save_photos = self.get_max_size_photos()
        headedrs = {
            'Authorization': self.token
        }
        for name_photo, url_photo in dict_save_photos.items():
            name = f'{name_photo}.jpg'
            params = {
                'url': url_photo,
                'path': f'{date.today()}/{name}'
            }
            response = rq.post(url_upload,
                              params=params,
                              headers=headedrs)
            logging.info(f'Фотография успешно загружена')
        logging.info(f'Все фотографии успешно загружены')


if __name__ == '__main__':
    tokenYandex = 'y0_AgAAAABRbtGzAADLWwAAAAD7zcDpAAAwW56ow4xEqZLaaAmgwKaOlirmLw'
    user_id = 120236056
    vk = ApiVKCopyPhoto(user_id, tokenYandex)
    vk.upload_photos_to_disk()


