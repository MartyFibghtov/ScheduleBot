# -*- coding: utf-8 -*-

import RUZ_HSE_API as ruz
import formater as f
from toks import main_token
import codes


import logging
import pprint
import re
from datetime import timedelta
from datetime import date as d
import datetime
import shelve


#VK IMPORTS
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import vk_api


vk_session = vk_api.VkApi(token=main_token) #bot
longpoll = VkBotLongPoll(vk_session, 199174829)
vk = vk_session.get_api()


logging.basicConfig(filename="sample.log", level=logging.ERROR, filemode="w")

FILENAME = "../users"










def send(peer_id, text, keyboard=None):
    vk_session.method('messages.send', {'peer_id': peer_id, 'message': text, 'random_id': get_random_id(), 'keyboard':keyboard})

def handle_user(peer_id, msg):

        # Незнакомый пользователь получает статус нового
        if peer_id not in users_db:
            users_db[peer_id] = {'code': codes.NEW_USER, 'email': None}

        # Код юзера показывает как с ним взаимодействовать
        user_code = users_db[peer_id]['code']

        # Пользователь впервые к нам попал, запрашиваем email. Меняем статус.
        if user_code == codes.NEW_USER:
            send(peer_id, 'Добрый день! Чтобы мы могли найти ваше расписание, сообщите вашу корпоративную почту')
            users_db[peer_id] = {'code': codes.WAITING_FOR_EMAIL, 'email': None}


        # Ждем от пользователя email. Просим подтверждение
        elif user_code == codes.WAITING_FOR_EMAIL:
            email = msg.strip()
            if ruz.email_is_valid(email):
                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button("Да", color=VkKeyboardColor.PRIMARY)
                keyboard.add_button("Нет", color=VkKeyboardColor.PRIMARY)

                send(peer_id, "%s, сохранить эту почту?" % email, keyboard=keyboard.get_keyboard())
                users_db[peer_id] = {'code': codes.WAITING_FOR_EMAIL_CONFIRMATION, 'email': email}
            else:
                send(peer_id, "Такого пользователя я не знаю ;( \n Проверьте правильность введенных данных")


        elif user_code == codes.WAITING_FOR_EMAIL_CONFIRMATION:
            # Подтверждает почту
            if msg == 'да':
                email = users_db[peer_id]['email']
                users_db[peer_id] = {'code': codes.REGISTRATED, 'email': email}
                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button('Расписание', color=VkKeyboardColor.PRIMARY)
                keyboard.add_line()
                keyboard.add_button('Где пара?', color=VkKeyboardColor.POSITIVE)
                keyboard.add_line()
                keyboard.add_button('Забыть меня', color=VkKeyboardColor.NEGATIVE)

                send(peer_id, 'Принято!\n Расписание - выводит ваше расписание на сегодня\n Где пара? - присылает ссылку на ближайшую пару \n Забыть меня - удаляет бота из беседы', keyboard=keyboard.get_keyboard())


            elif msg == 'нет':
                send(peer_id, 'Хорошо, сообщите вашу корпоративную почту')
                users_db[peer_id] = {'code': codes.WAITING_FOR_EMAIL, 'email': None}
            else:
                send(peer_id, 'Простите, я вас не поняла :(')
                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button("Да", color=VkKeyboardColor.PRIMARY)
                keyboard.add_button("Нет", color=VkKeyboardColor.PRIMARY)

                send(peer_id, "%s, сохранить эту почту?" % email, keyboard=keyboard.get_keyboard())


        elif user_code >= codes.REGISTRATED:
            # Знаем почту пользователя
            user_email = users_db[peer_id]['email']
            if "расписание" in msg:
                today = d.today()
                formated_today = today.strftime("%Y.%m.%d")
                schedule = ruz.get_student_schedule(user_email, formated_today, formated_today, "1")

                # Клавиатура других дней
                keyboard = VkKeyboard(one_time=True)
                dates = {}
                weekdays_dict = {   0:"ПН",
                                    1:"ВТ",
                                    2:"СР",
                                    3:"ЧТ",
                                    4:"ПТ",
                                    5:"СБ",
                                    6:"ВС"}

                for days in range(0, 7):

                    date = today + timedelta(days=days)
                    weekday_text = weekdays_dict[date.weekday()]
                    # На основе словаря генерим название на русском

                    formated_date = weekday_text + " " + date.strftime("%d.%m")
                    # 'ПТ 27.11'

                    full_date = date.strftime("%Y.%m.%d")
                    # '2020.11.29'

                    dates.setdefault(formated_date.lower(), full_date)
                    keyboard.add_button(formated_date, color=VkKeyboardColor.PRIMARY)

                    if days == 2 or days == 5:
                        keyboard.add_line()

                keyboard.add_button("Меню", color=VkKeyboardColor.POSITIVE)


                send(peer_id, f.format_schedule_one_day(schedule), keyboard=keyboard.get_keyboard())

                users_db[peer_id] = {'code': codes.IN_SCHEDULE, 'email': user_email, 'dates': dates, 'keyboard':keyboard.get_keyboard()}


            elif "где пара" in msg or 'ссылка' in msg:
                def get_curr_lessons(email_temp):
                    today = d.today()
                    formated_today = today.strftime("%Y.%m.%d")
                    schedule = ruz.get_student_schedule(email_temp, formated_today, formated_today, "1")
                    new_schedule = []
                    for lesson in schedule:
                        hh_start = int(lesson['date_start'].split("T")[1].split(":")[0])+3 # 12:30
                        mm_start = int(lesson['date_start'].split("T")[1].split(":")[1])

                        now  = datetime.datetime.now()
                        lesson_start = now.replace(hour=hh_start, minute=mm_start)
                        duration = now - lesson_start
                        duration_in_s = duration.total_seconds()
                        minutes = divmod(duration_in_s, 60)[0]

                        if -16 < minutes and 50 > minutes:
                             new_schedule.append(lesson)

                    return new_schedule

                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button('Расписание', color=VkKeyboardColor.PRIMARY)
                keyboard.add_line()
                keyboard.add_button('Где пара?', color=VkKeyboardColor.POSITIVE)
                keyboard.add_line()
                keyboard.add_button('Забыть меня', color=VkKeyboardColor.NEGATIVE)

                send(peer_id, f.format_schedule_active(get_curr_lessons(user_email)), keyboard=keyboard.get_keyboard())


            elif user_code == codes.IN_SCHEDULE:
                if msg in users_db[peer_id]['dates']:
                    formated_date = users_db[peer_id]['dates'][msg]
                    schedule = ruz.get_student_schedule(user_email, formated_date, formated_date, "0")
                    #pprint.pprint(schedule)
                    send(peer_id, f.format_schedule_one_day(schedule), keyboard=users_db[peer_id]['keyboard'])


            if "меню" in msg:
                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button('Расписание', color=VkKeyboardColor.PRIMARY)
                keyboard.add_line()
                keyboard.add_button('Где пара?', color=VkKeyboardColor.POSITIVE)
                keyboard.add_line()
                keyboard.add_button('Забыть меня', color=VkKeyboardColor.NEGATIVE)
                send(peer_id, 'Меню:\n Расписание - выводит ваше расписание на сегодня\n Где пара? - присылает ссылку на ближайшую пару \n Забыть меня - удаляет бота из беседы', keyboard=keyboard.get_keyboard())
                users_db[peer_id] = {'code': codes.REGISTRATED, 'email': user_email}





            if "забыть меня" in msg:
                del users_db[peer_id]

                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button('Начать', color=VkKeyboardColor.PRIMARY)
                send(peer_id, 'До встречи!', keyboard=keyboard.get_keyboard())


def handle_chat(peer_id, msg):

    # Незнакомый чат получает статус нового
    if peer_id not in users_db:
        users_db[peer_id] = {'code': codes.NEW_CHAT, 'group_id': None}

    # Код чата показывает как с ним взаимодействовать
    user_code = users_db[peer_id]['code']
    logging.error(user_code)

    # Чат впервые к нам попал, запрашиваем email. Меняем статус.
    if user_code == codes.NEW_CHAT:
        send(peer_id, 'Добрый день! Чтобы мы могли найти ваше расписание, сообщите название вашей группы')
        users_db[peer_id] = {'code': codes.WAITING_FOR_CHAT_NAME, 'group_id': None}


    # Ждем от чата название группы. Просим подтверждение.
    elif user_code == codes.WAITING_FOR_CHAT_NAME:
        group_name = msg.strip()
        group_list = ruz.get_groups_list(group_name)
        num_of_rets = len(group_list)

        if num_of_rets == 1:
                group = group_list[0]
                group_label = group['label']
                group_id = group['id']
                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button("Да", color=VkKeyboardColor.PRIMARY)
                keyboard.add_button("Нет", color=VkKeyboardColor.PRIMARY)

                send(peer_id, "%s, сохранить эту группу?\n - Да \n - Нет" % group_label, keyboard=keyboard.get_keyboard())
                users_db[peer_id] = {'code': codes.WAITING_FOR_CHAT_NAME_CONFIRMATION, 'group_id': group_id, 'group_label': group_label}

        elif num_of_rets == 0:
                send(peer_id, "Такой группы я не знаю 😕 \n Проверьте правильность введенных данных")

        elif num_of_rets > 1:
                send(peer_id, "Уточните название группы, под ваш запрос подходит %s групп 🤔" % num_of_rets)

    elif user_code == codes.WAITING_FOR_CHAT_NAME_CONFIRMATION:
        # Подтверждает название группы
        group_id = users_db[peer_id]['group_id']
        group_label = users_db[peer_id]['group_label']
        if 'да' in msg:
            users_db[peer_id] = {'code': codes.CHAT_REGISTRATED, 'group_id': group_id}
            keyboard = VkKeyboard(one_time=False)
            keyboard.add_button('/расписание', color=VkKeyboardColor.PRIMARY)
            keyboard.add_line()
            keyboard.add_button('/ссылка', color=VkKeyboardColor.POSITIVE)
            keyboard.add_line()
            keyboard.add_button('/удалить бота', color=VkKeyboardColor.NEGATIVE)
            send(peer_id, 'Принято! \n Список доступных команд: \n/расписание - выводит расписание группы на сегодня\n /cсылка - присылает ссылку на ближайшую пару \n /удалитьБота - удаляет бота из беседы', keyboard=keyboard.get_keyboard())


        elif 'нет' in msg:
            send(peer_id, 'Хорошо, сообщите название вашей группы')
            users_db[peer_id] = {'code': codes.WAITING_FOR_CHAT_NAME, 'group_id': None}

        else:
            send(peer_id, 'Простите, я вас не поняла :(')
            send(peer_id, "%s, сохранить эту группу?\n Да \n Нет" % group_label)


    elif user_code >= codes.CHAT_REGISTRATED:
        # Знаем ID чата
        group_id = users_db[peer_id]['group_id']
        if "/расписание" in msg:
            today = d.today()
            formated_today = today.strftime("%Y.%m.%d")
            schedule = ruz.get_group_schedule(group_id, formated_today, formated_today, "1")
            send(peer_id, f.format_schedule_one_day(schedule))


        elif "/ссылка" in msg:

            def get_curr_lessons(group_id_temp):
                today = d.today()
                formated_today = today.strftime("%Y.%m.%d")
                schedule = ruz.get_group_schedule(group_id_temp, formated_today, formated_today, "1")
                new_schedule = []
                for lesson in schedule:
                    hh_start = int(lesson['date_start'].split("T")[1].split(":")[0])+3 # 12:30
                    mm_start = int(lesson['date_start'].split("T")[1].split(":")[1])

                    now  = datetime.datetime.now()
                    lesson_start = now.replace(hour=hh_start, minute=mm_start)
                    duration = now - lesson_start
                    duration_in_s = duration.total_seconds()
                    minutes = divmod(duration_in_s, 60)[0]

                    if -16 < minutes and 85 > minutes:
                         new_schedule.append(lesson)

                return new_schedule





            send(peer_id, f.format_schedule_active(get_curr_lessons(group_id)))



        elif "/удалитьбота" in msg:
            del users_db[peer_id]
            send(peer_id, 'До встречи!')




while True:
    try:
        users_db = shelve.open(FILENAME)

        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW and event.obj['message']['text']:




                msg = event.obj['message']['text'].lower()
                peer_id = str(event.obj['message']['peer_id'])

                with open('../history.csv', mode='a') as csv_file:
                    time = datetime.Now.ToString("MM/dd/yyyy HH:mm")
                    writer = csv.DictWriter(csv_file)
                    writer.writerow([peer_id, msg, time])

                if int(peer_id) > 2000000000:
                    # Беседа

                    msg = msg.replace('[club199174829|@hseplanandschedule]', '')
                    msg = re.sub(r'[\s,.]', '', msg)
                    print(msg)

                    handle_chat(peer_id, msg)

                else:
                    # Юзер

                    handle_user(peer_id, msg)

    except Exception as e:
        logging.error(e, exc_info=True)
        users_db.close()
