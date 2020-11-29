
# -*- coding: utf-8 -*-

import requests
import pprint
import json
from datetime import date, timedelta


main_url = "https://ruz.hse.ru"
#https://ruz.hse.ru/api/search?term=Денис&type=student
#/api/schedule/student/217275?start=2020.09.28&finish=2020.10.04&lng=1

def get_students_list(student_name):
    params = { 'term': student_name,
               'type': 'student'}
    url = main_url+'/api/search'
    r = requests.get(url, params=params)
    return json.loads(r.text)
"""
def get_student_schedule(student_id, start_date, end_date, lng): # ('254711', '2020.09.28','2020.10.04', 1)
    params = { 'start': start_date,
               'finish': end_date,
               'lng': 1
               }
    url = main_url + '/api/schedule/student/' + student_id
    r = requests.get(url, params=params)
    return json.loads(r.text)
"""

def get_student_schedule(email, start_date, end_date, lng): # ('254711', '2020.09.28','2020.10.04', 1)
    params = { 'start': start_date,
               'end': end_date,
               'email': email
               }
    headers = {"Accept-Language": "ru-RU, ru;q=0.9"}
    url = 'https://api.hseapp.ru/v3/ruz/lessons'
    r = requests.get(url, params=params, headers=headers)
    return json.loads(r.text)

"""
https://api.hseapp.ru/v3/ruz/lessons?end=2020-11-12&start=2020-11-12&email=atnurmatov@edu.hse.ru
"""


def email_is_valid(email):
    """
    Определяет, существует ли такой EMAIL,
    отправляя запрос на получение его расписания
    """
    try:
        email = email.strip()
        test_date = date.today()
        test_date_f= test_date.strftime("%Y.%m.%d")
        resp = get_student_schedule(email, test_date_f, test_date_f, 1)
        resp['error']
        return False
    except Exception as e:
        return True
