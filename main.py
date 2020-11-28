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
import shelve


#VK IMPORTS
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import vk_api


vk_session = vk_api.VkApi(token=main_token) #bot
longpoll = VkBotLongPoll(vk_session, 199174829)
vk = vk_session.get_api()


logging.basicConfig(filename="sample.log", level=logging.INFO, filemode="w")

FILENAME = "users"










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

                send(peer_id, 'Принято!', keyboard=keyboard.get_keyboard())


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


            #elif msg == "  "
            elif user_code == codes.IN_SCHEDULE:
                if msg in users_db[peer_id]['dates']:
                    formated_date = users_db[peer_id]['dates'][msg]
                    schedule = ruz.get_student_schedule(user_email, formated_date, formated_date, "0")
                    #pprint.pprint(schedule)
                    send(peer_id, f.format_schedule_one_day(schedule), keyboard=users_db[peer_id]['keyboard'])


            if msg == "меню":
                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button('Расписание', color=VkKeyboardColor.PRIMARY)
                keyboard.add_line()
                keyboard.add_button('Где пара?', color=VkKeyboardColor.POSITIVE)
                keyboard.add_line()
                keyboard.add_button('Забыть меня', color=VkKeyboardColor.NEGATIVE)
                send(peer_id, 'Меню:', keyboard=keyboard.get_keyboard())
                users_db[peer_id] = {'code': codes.REGISTRATED, 'email': user_email}




            if msg == "забыть меня":
                del users_db[peer_id]

                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button('Начать', color=VkKeyboardColor.PRIMARY)
                send(peer_id, 'До встречи!', keyboard=keyboard.get_keyboard())





while True:
    try:
        users_db = shelve.open(FILENAME)

        for event in longpoll.listen():
            #pprint.pprint(event.type)

            if event.type == VkBotEventType.MESSAGE_NEW and event.obj['message']['text']:

                msg = event.obj['message']['text'].lower()
                peer_id = str(event.obj['message']['peer_id'])

                #users_db = shelve.open(FILENAME)

                if int(peer_id) > 2000000000:
                    # Беседа
                    #print("Chat")
                    send(peer_id, "Извините, пока работают только личные сообщения", None)

                    #handle_chat()
                else:
                    # Юзер
                    #print("User")

                    #send(peer_id, "User", None)

                    handle_user(peer_id, msg)
    except Exception as e:
        print(e)
        db.close()
