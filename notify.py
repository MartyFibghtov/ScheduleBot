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
import schedule as sc
import time

from datetime import date, timedelta



import shelve

FILENAME = "users"


def job():
    print("time")
    users_db = shelve.open(FILENAME)
    for vk_id in users_db.keys():
        print(vk_id)
        print(users_db[vk_id].get('student_id'))
        if users_db[vk_id].get('student_id') != None:
            today = date.today()
            formated_today = today.strftime("%Y.%m.%d")
            student_id = users_db[vk_id]['student_id']
            schedule = ruz.get_student_schedule(student_id, formated_today, formated_today, "1")
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button('Расписание', color=VkKeyboardColor.PRIMARY)
            keyboard.add_line()
            keyboard.add_button('Навигация', color=VkKeyboardColor.POSITIVE)
            keyboard.add_line()
            keyboard.add_button('Забыть меня', color=VkKeyboardColor.NEGATIVE)

            sender(vk_id, format_schedule_one_day(schedule), keyboard=keyboard.get_keyboard())





def format_schedule_one_day(schedule):
    if len(schedule) == 0:
        return "Сегодня нет пар, отдыхаем!"
    res = schedule[0]['date']+"\n\n"

    for lesson in schedule:
        res += """Пары на сегодня:
        %s
        %s - %s
        %s
        %s""" % (lesson['discipline'], lesson['beginLesson'], lesson['endLesson'], lesson['auditorium'], lesson['lecturer'])
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

users_db = shelve.open(FILENAME)





sc.every().day.at("12:43").do(job)


while True:
    sc.run_pending()
    time.sleep(1)
