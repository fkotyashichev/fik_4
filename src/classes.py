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


class Vacancy_list:
    """Класс для работы с уже найденными вакансиями"""
    vacancy = []
    data = '1'
    __slots__ = ('source', 'vacancy_name', 'url', 'city', 'requirement', 'currency', 'salary_from', 'salary_to')

    def __init__(self, source="internet", vacancy_name="net", url="http://ssilki.net", city="(Город не указан)", requirement="Не указано требований", currency="(Валюта не указана)", salary_from=0.0, salary_to="(Предельная зарплата не указана)"):
        self.source = source
        self.vacancy_name = vacancy_name
        self.url = url
        self.city = city
        self.requirement = requirement
        self.currency = currency
        self.salary_from = salary_from
        self.salary_to = salary_to
        Vacancy_list.vacancy.append(self)

    def __str__(self):
        return (f"\nНа сайте: {self.source} мы нашли вакансию: {self.vacancy_name} \nс зарплатой от "
                f"{self.salary_from} "
                f"{self.currency}"
                f" до {self.salary_to} {self.currency}.\n"
                f"В городе {self.city if not None else 'город не указан'}. \n"
                f"Требования/описание вакансии: {self.requirement} \n"
                f"Вакансия находится по ссылке: {self.url} \n")

    @classmethod
    def reed_json(cls, filename):
        """Считывает все найденные ранее вакансии из json файла"""
        reader = json.loads(open(filename).read())
        line = reader[-1]
        for value in line.values():
            cls.data = value
        for line in reader[:-1]:
            source = line['source']
            vacancy_name = line['name']
            url = line['url']
            city = line['city']
            requirement = line['requirement']
            currency = line['currency']
            salary_from = line['salary_from']
            salary_to = line['salary_to']
            Vacancy_list(source, vacancy_name, url, city, requirement, currency, salary_from, salary_to)

    @classmethod
    def save_json(cls):
        """Сохраняем отобранные вакансии в файл, названный по запросу"""
        filename = cls.data.split(' ')
        filename = '_'.join(filename) + '.json'
        list_vacancy = []
        for i in range(cls.__len__()):
            if cls.vacancy[i].source in ['HeadHunter', 'SuperJob']:
                info = {
                    'source': cls.vacancy[i].source,
                    'name': cls.vacancy[i].vacancy_name,
                    'city': cls.vacancy[i].city,
                    'salary_from': cls.vacancy[i].salary_from,
                    'salary_to': cls.vacancy[i].salary_to,
                    'currency': cls.vacancy[i].currency,
                    'url': cls.vacancy[i].url,
                    "requirement": cls.vacancy[i].requirement,
                }
                list_vacancy.append(info)

        with open(filename, 'w+', encoding="UTF-8") as f:
            json.dump(list_vacancy, f, indent=2, ensure_ascii=False)

    @classmethod
    def __len__(cls):
        return len(cls.vacancy)

    @classmethod
    def delete_vacancy(cls, prev, tail=-1):
        if cls.__len__ > 0 and prev < cls.__len__:
            del cls.vacancy[prev:tail]

    def __gt__(self, other):
        return self.salary_from > other.salary_from

    @classmethod
    def get_vacancy_by_salary(cls, salary_from):
        cls.sorted_vacancy_by_salary()
        cls.vacancy = list(filter(lambda vac: vac.salary_from > salary_from, cls.vacancy))

    @classmethod
    def sorted_vacancy_by_salary(cls):
        for x in range(cls.__len__()-1):
            for y in range(x+1, cls.__len__()):
                if not cls.vacancy[x] > cls.vacancy[y]:
                    a = cls.vacancy[x]
                    cls.vacancy[x] = cls.vacancy[y]
                    cls.vacancy[y] = a

    @classmethod
    def top_vacancy(cls, n: int):
        cls.sorted_vacancy_by_salary()
        cls.vacancy = cls.vacancy[:n]
