from abc import ABC, abstractmethod
import json
import os

import requests


class Engine(ABC):
    @abstractmethod
    def get_request(self):
        pass

    def __init__(self, data: str):
        """Инициализирует класс где data - название по которому будет происходить поиск"""
        self.data = data
        self.request = self.get_request()


class SJ(Engine):
    def get_request(self):
        """Возвращает вакансии с сайта SuperJob"""
        url = "https://api.superjob.ru/2.0/vacancies/"
        params = {'keyword': self.data, "count": 200}
        my_auth_data = {"X-Api-App-Id": os.environ['SuperJob_api_key']}
        response = requests.get(url, headers=my_auth_data, params=params)
        vacancies = response.json()['objects']
        return vacancies

    class HH(Engine):
        def get_request(self):
            """Возвращает вакансии с сайта HeadHunter"""
            try:
                vacancies = []
                for page in range(1, 3):
                    params = {
                        "text": f"{self.data}",
                        "area": 113,
                        "page": page,
                        "per_page": 100,
                    }
                    vacancies.extend(requests.get('https://api.hh.ru/vacancies', params=params).json()["items"])
                return vacancies
            except requests.exceptions.ConnectTimeout:
                print('Oops. Connection timeout occured!')
            except requests.exceptions.ReadTimeout:
                print('Oops. Read timeout occured')
            except requests.exceptions.ConnectionError:
                print('Seems like dns lookup failed..')
            except requests.exceptions.HTTPError as err:
                print('Oops. HTTP Error occured')
                print('Response is: {content}'.format(content=err.response.content))

