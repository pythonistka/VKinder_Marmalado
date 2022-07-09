from random import randrange
from secret_token import vk_token
import vk_api
import math
from vk_api.longpoll import VkLongPoll, VkEventType
import pprint

token = vk_token

vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })

# Просим ввести пользователя дополнительную информацию, если она отсутствовала:
def ask_question(user_id, question) -> str:
    question_text = f"Пожалуйста, введите ваш {question}: "
    # Спрашиваем пользователя вопрос
    write_msg(user_id, question_text)
    # Читаем ответ
    result = ""
    for answer_event in longpoll.listen():
        if answer_event.type != VkEventType.MESSAGE_NEW or not answer_event.to_me:
            continue
        result = answer_event.text
        break
    if not result:
        return ask_question(user_id, question)
    else:
        return result.strip().lower()


# Запрашиваем город
def get_user_city(user_id) -> dict:
    city = {}
    result = vk.method("users.get", {"user_id": user_id, "fields": {"city"}})[0]
    if 'city' in result:
        city = result['city']
    else:
        question = "город"
        result = ask_question(user_id, question)
        city['title'] = result

    return city


# Запрашиваем пол
def get_user_sex(user_id):
    result = vk.method("users.get", {"user_id": user_id, "fields": {"sex"}})[0]
    if 'sex' in result and result['sex'] != 0:
        return int(result['sex'])
    # запрашиваем пол
    question = "пол"
    result = ask_question(user_id, question)
    if result == "м" or result == "мужской" or result == "муж":
        return 2
    else:
        return 1


# Конвертируем дату в возраст
def get_user_age_from_date(date_str: str) -> int:
    from datetime import datetime
    b_date = datetime.strptime(date_str, '%d.%m.%Y')
    age = math.floor((datetime.today() - b_date).days / 365)
    return age


# Запрашиваем возраст
def get_user_age(user_id):
    result = vk.method("users.get", {"user_id": user_id, "fields": {"bdate"}})[0]
    if 'bdate' in result and len(result['bdate']) > 5:
        age = get_user_age_from_date(date_str=result['bdate'])
        return age
    else:
        result = ""
        while not result.isdigit():
            result = ask_question(user_id, "возраст")
        return result

message_id = 0
print("Start")
for event in longpoll.listen():
    if event.type != VkEventType.MESSAGE_NEW or not event.to_me:
        continue

    if message_id == 0:
        text = "Добро пожаловать в сервис знакомств Marmalado!\n"
        text += "Для начала поиска пары введите цифру 1"
        write_msg(event.user_id, text)
        message_id = message_id + 1
        continue

    answer_of_user = event.text

    if answer_of_user == "1":
        text = "Для поиска пары, мы проанализиуем ваши данные..."
        write_msg(event.user_id, text)
        # получаем id пользователя
        user_id = event.user_id
        write_msg(user_id, f"[+] Ваш id пользователя: {user_id}")
        # получить город
        user_city = get_user_city(user_id)
        write_msg(user_id, f"[+] Ваш город: {user_city}")
        # получить пол
        user_sex = get_user_sex(user_id)
        user_sex = "Женский" if user_sex == 1 else "Мужской"
        write_msg(user_id, f"[+] Ваш пол: {user_sex}")
        # получить возраст
        user_age = get_user_age(user_id)
        write_msg(user_id, f"[+] Ваш возраст: {user_age}")

        write_msg(user_id, "\n\nТеперь пришло время подобрать вам пару. Готовы?")

    elif answer_of_user == "пока":
        write_msg(event.user_id, "Пока((")
    else:
        write_msg(event.user_id, "Не поняла вашего ответа...")
    message_id = message_id + 1


