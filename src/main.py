from src.classes import HH, SJ, Vacancy_list


def poisk():
    """Функция для поиска по запросу пользователя.
    возвращаем где пользователь хочет искать"""
    while True:
        user_answer = input("Выберите где искать профессию\n1.HH\n2.SJ\n3.HH u SJ\n")
        if not user_answer.isdigit():
            continue
        elif 1 <= int(user_answer) <= 3:
            break
        else:
            continue

    user_poisk = input("Введите ключ по которому будем искать профессию\n")
    sj_api = SJ(user_poisk)
    hh_api = HH(user_poisk)
    sj_api.to_json()
    hh_api.to_json()
    return int(user_answer)


def action_with_info(vacancy_list: Vacancy_list):
    while True:
        user_answer = input("Выберите действие:\n1.Отфильтровать по минимальной з/п\n2.Вывести топ\n")
        if user_answer.isdigit():
            if int(user_answer) == 1:
                user_salary = input("Введите минимальную з/п числом\n")
                while not user_salary.isdigit():
                    user_salary = input("Введите минимальную з/п числом\n")

                vacancy_list.get_vacancy_by_salary(int(user_salary))

            if int(user_answer) == 2:

                while True:
                    user_top = input(f"ВВедите число до {len(vacancy_list)} вакасиний сколько вывести на экран\n")
                    if not user_top.isdigit() or int(user_top) <= 0 or int(user_top) > len(vacancy_list):
                        print("Давайте попробуем еще раз.")
                    else:
                        vacancy_list.top_vacancy(int(user_top))
            if int(user_answer) == 1 or int(user_answer) == 2:
                break
    for i in range(len(vacancy_list)):
        print(vacancy_list.vacancy[i])

    user_answer_save = input("Сохранить в файл изменения?\nНапишите Да\n или Нет\n")
    if user_answer_save.lower() == 'да':
        vacancy_list.save_json()


def main():
    user_answer = poisk()

    vacancy_list = Vacancy_list()
    if user_answer == 1 or user_answer == 3:
        vacancy_list.reed_json("hhvacancy.json")
    if user_answer == 2 or user_answer == 3:
        vacancy_list.reed_json("sjvacancy.json")

    action_with_info(vacancy_list)


if __name__ == "__main__":
    main()
