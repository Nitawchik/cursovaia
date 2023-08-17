import time
import requests
import os
import sys
from pprint import pprint
import pyprind
import json

class YaUploader:
    host = 'https://cloud-api.yandex.net:443'

    def __init__(self, token: str):
        self.token = token
        self.headers = {'Content-Type': 'application/json',
                   'Authorization': f'OAuth {self.token}'
                   }

    def create_folder(self):
        url = f'{self.host}/v1/disk/resources'
        params = {'path': 'VK', 'owerwrite': True}
        response = requests.put(url, params=params, headers=self.headers).json()
        # pprint(response)

    def sent_file(self, file_name, url_photo):
        with open(f'{file_name}.jpg', 'wb') as file:
            img = requests.get(url_photo)
            file.write(img.content)

        url = f'{self.host}/v1/disk/resources/upload'
        params = {'path': 'VK/'+ f'{file_name}.jpg', 'owerwrite': True}
        resp = requests.get(url, params=params, headers=self.headers).json()['href']

        response = requests.put(resp, data=open(f'{file_name}.jpg', 'rb'))

        os.remove(f'{file_name}.jpg')

    @my_log.make_log('YaUploader.log')
    def upload_photos(self, photos_dict):
        # Создаём папку на Яндекс Диске
        self.create_folder()

        photos_log = []
        for likes, photos in photos_dict.items():
            for photo in photos:
                photo_log = {}
                if len(photos) > 1:
                    file_name = str(likes) + ' ' + photo[0]
                else:
                    file_name = str(likes)
                # Загрузка на Яндекс Диск
                self.sent_file(file_name, photo[1])
                # Записываем инфу для лога
                photo_log['file_name'] = f'{file_name}.jpg'
                photo_log['size'] = 'z'
                photos_log.append(photo_log)
                bar.update()
        # Сохраняем лог
        with open('photos.json', 'w') as log:
            json.dump(photos_log, log, indent=4)

class VKphotos:
    Url = 'https://api.vk.com/method/photos.get'

    def __init__(self, token: str):
        self.token = token
        self.vk_id = int(input('Input ID: (press enter for default = 1517274)') or '1517274')

    @my_log.make_log('VKphotos.log')
    def get_photos(self, count_photos):
        params = {
            'owner_id': self.vk_id,
            'access_token': self.token,
            'v': '5.131',
            'album_id': 'profile',
            'rev': 1,
            'extended': 1,
            'count': count_photos
        }

        photos = requests.get(self.Url, params=params).json()['response']['items']
        photos_dict = {}
        i = 0
        for photo in photos:
            key = photo['likes']['count']
            sizes = photo['sizes']
            for size in sizes:
                if size['type'] == 'z':
                    url_photo = size['url']
                    break
            if key in photos_dict:
                photos_dict[key] = photos_dict[key] + [[(time.strftime('%Y_%m_%d', time.gmtime(photo['date']))), url_photo]]
            else:
                photos_dict.setdefault(key, [[time.strftime('%Y_%m_%d', time.gmtime(photo['date'])), url_photo]])
            bar.update()
        return photos_dict


if __name__ == '__main__':
    with open('token_vk.txt', 'r') as file_token_vk:
        token_vk = file_token_vk.read().strip()
    with open('token_ya.txt', 'r') as file_token_ya:
        token_ya = file_token_ya.read().strip()

    count_photos = int(input('How many photos? (press enter for default = 5)') or 5)

    bar = pyprind.ProgBar(count_photos*2, stream = sys.stdout)

    vk_photos = VKphotos(token_vk).get_photos(count_photos)
    ya_uploader = YaUploader(token_ya).upload_photos(vk_photos)

