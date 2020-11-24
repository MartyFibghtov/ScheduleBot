# -*- coding: utf-8 -*-

import RUZ_HSE_API as ruz

import logging
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api import VkUpload
from toks import main_token
import codes
import pprint
import re

from datetime import date, timedelta



import shelve

FILENAME = "users"


def send_pic(image, vk_id):
    attachments = []
    upload_image = upload.photo_messages(photos=image)[0]
    attachments.append('photo{}_{}'.format(upload_image['owner_id'], upload_image['id']))
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Меню', color=VkKeyboardColor.POSITIVE)
    vk_session.method('messages.send', {'user_id': vk_id, 'message':"", 'random_id': get_random_id(), 'keyboard':keyboard.get_keyboard(), 'attachment':','.join(attachments)})



def format_students_list(students_list):
    res = ""
    for i in range(len(students_list)):
        res += "%s. %s - %s \n" % (str(i+1), students_list[i]['label'], students_list[i]['description'])


    return res


def format_schedule_one_day(schedule):
    if len(schedule) == 0:
        return "В этот день нет пар, отдыхаем!"
    res = schedule[0]['date']+"\n\n"

    for lesson in schedule:
        res += """%s
        %s - %s
        %s
        %s
        %s""" % (lesson['discipline'], lesson['beginLesson'], lesson['endLesson'], lesson['auditorium'], lesson['lecturer'], lesson['building'])
        if lesson['url1'] != None:
            res += "\nURL:" + lesson['url1']

        res += "\n\n"

    return res




# add filemode="w" to overwrite
logging.basicConfig(filename="sample.log", level=logging.INFO, filemode="w")
vk_session = vk_api.VkApi(token = main_token)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)
upload = VkUpload(vk_session)

def sender(vk_id, text, keyboard):
    vk_session.method('messages.send', {'user_id': vk_id, 'message': text, 'random_id': get_random_id(), 'keyboard':keyboard})

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:

            msg = event.text.lower()
            vk_id = str(event.user_id)
            users_db = shelve.open(FILENAME)


            if vk_id not in users_db:
                users_db[vk_id] = {'code': codes.NO_INFO, 'student_id':None, 'students_list': None}


            user_code = users_db[vk_id]['code']
            print(user_code)




            if msg == 'начать':
                sender(vk_id, '''Добрый день! Чтобы мы могли найти ваше расписание, сообщите ваше Фамилию и Имя''', keyboard=None)
                users_db[vk_id] = {'code': codes.WAITING_FOR_NAME, 'student_id': None, 'students_list': None}

            elif user_code == codes.WAITING_FOR_NAME:
                students_list = ruz.get_students_list(msg)
                if len(students_list) == 0:
                    sender(vk_id, 'Студент не найден, проверьте корректность введенных данных.\n Ошибка может возникать, если сначала ввести имя, а не фамилию', keyboard=None)
                elif len(students_list) >= 15:
                    sender(vk_id, 'Распространенная фамилия)\n Напишите ваше ФИО', keyboard=None)
                else:

                    keyboard = VkKeyboard(one_time=True)
                    try:
                        for i in range(1, len(students_list)+1):
                            keyboard.add_button(i, color=VkKeyboardColor.PRIMARY)
                            if i%4==0:
                                keyboard.add_line()
                    except:
                        pass

                    sender(vk_id, 'Выберите себя в списке, отправьте только число:\n\n%s' % format_students_list(students_list), keyboard=keyboard.get_keyboard()) # прикрепить клаву с цифрами
                    users_db[vk_id] = {'code': codes.WAITING_FOR_NAME_CHOICE, 'student_id':None, 'students_list': students_list}


            elif user_code == codes.WAITING_FOR_NAME_CHOICE:
                try:
                    nums = int(''.join(re.findall(r'\d+', msg))) - 1
                    student_id = users_db[vk_id]['students_list'][nums]['id']
                    users_db[vk_id] = {'code': codes.REGISTRATED, 'student_id': student_id, 'students_list': None}

                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('Расписание', color=VkKeyboardColor.PRIMARY)
                    keyboard.add_line()
                    keyboard.add_button('Навигация', color=VkKeyboardColor.POSITIVE)
                    keyboard.add_line()
                    keyboard.add_button('Забыть меня', color=VkKeyboardColor.NEGATIVE)


                    sender(vk_id, 'Принято!', keyboard=keyboard.get_keyboard())

                except:
                    students_list = users_db[vk_id]['students_list']
                    keyboard = VkKeyboard(one_time=True)
                    try:
                        for i in range(1, len(students_list)+1):
                            keyboard.add_button(i, color=VkKeyboardColor.PRIMARY)
                            if i%4==0:
                                keyboard.add_line()
                    except:
                        pass

                    sender(vk_id, 'Отправьте только число', keyboard=keyboard.get_keyboard())



            elif "расписание" in msg:
                try:
                    student_id = users_db[vk_id]['student_id']
                except:
                    student_id = None

                if student_id == None:
                    sender(vk_id, 'Вы не зарегистрированы', keyboard=None)
                else:
                    today = date.today()
                    formated_today = today.strftime("%Y.%m.%d")
                    student_id = users_db[vk_id]['student_id']
                    schedule = ruz.get_student_schedule(student_id, formated_today, formated_today, "1")


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
                        formated_date = weekday_text + " " + date.strftime("%d.%m")
                        full_date = date.strftime("%Y.%m.%d")
                        dates.setdefault(formated_date.lower(), full_date)
                        keyboard.add_button(formated_date, color=VkKeyboardColor.PRIMARY)

                        if days == 2 or days == 5:
                            keyboard.add_line()

                    keyboard.add_button("Меню", color=VkKeyboardColor.POSITIVE)


                    sender(vk_id, format_schedule_one_day(schedule), keyboard=keyboard.get_keyboard())

                    users_db[vk_id] = {'code': codes.IN_SCHEDULE, 'student_id': student_id, 'dates': dates, 'keyboard':keyboard.get_keyboard()}
                    # Отправить клаву с остальными днями недели

            elif user_code == codes.IN_SCHEDULE:

                if msg in users_db[vk_id]['dates']:
                    users_db[vk_id]['dates']
                    formated_date = users_db[vk_id]['dates'][msg]
                    schedule = ruz.get_student_schedule(student_id, formated_date, formated_date, "1")
                    sender(vk_id, format_schedule_one_day(schedule), keyboard=users_db[vk_id]['keyboard'])



            if msg == "навигация":
                if user_code != codes.REGISTRATED:
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('Начать', color=VkKeyboardColor.PRIMARY)
                    sender(vk_id, 'Вы не зарегистрированы, отправьте боту "Начать"', keyboard=keyboard.get_keyboard())
                else:
                    temp_dict = users_db[vk_id]
                    temp_dict.setdefault('navigation',codes.IN_NAVIGATION)
                    users_db[vk_id] = temp_dict

                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('Шаболовка', color=VkKeyboardColor.PRIMARY)
                    keyboard.add_line()
                    keyboard.add_button('Меню', color=VkKeyboardColor.POSITIVE)
                    sender(vk_id, 'Выберите здание:', keyboard=keyboard.get_keyboard())

            elif msg == "шаболовка":
                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button('Меню', color=VkKeyboardColor.POSITIVE)
                sender(vk_id, 'Введите номер аудитории', keyboard=keyboard.get_keyboard())
                temp_dict = users_db[vk_id]
                temp_dict['navigation'] = codes.IN_NAVIGATION_SHA
                users_db[vk_id] = temp_dict

            elif users_db[vk_id].get('navigation') == codes.IN_NAVIGATION_SHA:
                try:
                    if "к9" in msg or "к10" in msg:
                        image = "./buildings/SHA/910/910.PNG"
                        send_pic(image, vk_id)
                    elif len(msg)==4 and msg != 'меню':
                        try:
                            image = "./buildings/SHA/%s/%s.PNG" % (msg[0], msg[1])
                            send_pic(image, vk_id)
                        except Exception as e:
                            keyboard = VkKeyboard(one_time=True)
                            keyboard.add_button('Меню', color=VkKeyboardColor.PRIMARY)
                            sender(vk_id, 'Аудитория не найдена', keyboard=keyboard.get_keyboard())
                except Exception as e:

                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('Меню', color=VkKeyboardColor.PRIMARY)
                    sender(vk_id, e, keyboard=keyboard.get_keyboard())


            if msg == "меню":
                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button('Расписание', color=VkKeyboardColor.PRIMARY)
                keyboard.add_line()
                keyboard.add_button('Навигация', color=VkKeyboardColor.POSITIVE)
                keyboard.add_line()
                keyboard.add_button('Забыть меня', color=VkKeyboardColor.NEGATIVE)
                temp_dict = users_db[vk_id]
                try:
                    temp_dict['navigation'] = codes.NOT_IN_NAVIGATION
                except:
                    pass

                users_db[vk_id] = temp_dict
                sender(vk_id, 'Меню:', keyboard=keyboard.get_keyboard())

            if msg == "забыть меня":
                del users_db[vk_id]

                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button('Начать', color=VkKeyboardColor.PRIMARY)

                sender(vk_id, 'До встречи!', keyboard=keyboard.get_keyboard())

            users_db.close()
