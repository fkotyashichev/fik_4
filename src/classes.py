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

    @abstractmethod
    def to_json(self):
        pass


class SJ(Engine):
    def get_request(self):
        """Возвращает вакансии с сайта SuperJob"""
        url = "https://api.superjob.ru/2.0/vacancies/"
        params = {'keyword': self.data, "count": 200}
        my_auth_data = {"X-Api-App-Id": os.environ['SuperJob_api_key']}
        response = requests.get(url, headers=my_auth_data, params=params)
        vacancies = response.json()['objects']
        return vacancies

    @property
    def get_vacancy(self):
        """Взяли все ранее найденные вакансии с SuperJob и записали их в переменную с полями: наименование вакансии,
        город, зарплатная вилка, описание требований и url вакансии"""
        try:
            list_vacancy = []
            for i in range(len(self.request)):
                info = {
                    'source': 'SuperJob',
                    'name': self.request[i]['profession'],
                    'city': "(Город не указан)" if self.request[i]['town'] == None else self.request[i]['town']['title'],
                    'salary_from': 0.0 if self.request[i]['payment_from'] == 0 else self.request[i]['payment_from'],
                    'salary_to': "(Предельная зарплата не указана)" if (self.request[i]['payment_to'] == 0 or self.request[i]['payment_to'] == None) else self.request[i]['payment_to'],
                    'currency': "(Валюта не указана)" if self.request[i]['currency'] == None else self.request[i]['currency'],
                    "requirement": self.request[i]['candidat'],
                    'url': self.request[i]['link'],
                }
                list_vacancy.append(info)
            return list_vacancy
        except Exception:
            print("Error")
        else:
            print("Выполняем поиск на сайте SuperJob")

    def to_json(self):
        writer = self.get_vacancy
        data = {"data": self.data}
        writer.append(data)
        with open('sjvacancy.json', 'w') as f:
            json.dump(writer, f, indent=2)


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

    @property
    def get_vacancy(self):
        """Взяли все ранее найденные вакансии с HeadHunter
        и записали их в переменную с полями: наименование вакансии,
        город, зарплатная вилка, описание требований и url вакансии"""

        list_vacancy = []
        for i in range(len(self.request)):
            if self.request[i]['snippet']['requirement'] is not None:
                s = self.request[i]['snippet']['requirement']
                for x, y in ("<highlighttext>", ""), ("</highlighttext>", ""):
                    s = s.replace(x, y)
            info = {
                'source': 'HeadHunter',
                'name': self.request[i]['name'],
                'city': "(Город не указан)" if (self.request[i]['address']) == None else self.request[i]['address']['city'],
                'salary_from': 0.0 if (self.request[i]['salary'] == None or self.request[i]['salary']['from'] == 0 or self.request[i]['salary']['from'] == None) else self.request[i]['salary']['from'],
                'salary_to': "(Предельная зарплата не указана)" if (self.request[i]['salary'] == None or self.request[i]['salary']['to'] == None) else
                self.request[i]['salary']['to'],
                'currency': "(Валюта не указана)" if self.request[i]['salary'] == None else f"{self.request[i]['salary']['currency']}",
                'url': self.request[i]['alternate_url'],
                "requirement": s,
            }
            list_vacancy.append(info)
        return list_vacancy

    def to_json(self):
        writer = self.get_vacancy
        data = {"data": self.data}
        writer.append(data)
        with open('hhvacancy.json', 'w') as f:
            json.dump(writer, f, indent=2)

