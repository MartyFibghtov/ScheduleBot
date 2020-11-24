
# -*- coding: utf-8 -*-

import requests
import pprint
import json


main_url = "https://ruz.hse.ru"
#https://ruz.hse.ru/api/search?term=Денис&type=student
#/api/schedule/student/217275?start=2020.09.28&finish=2020.10.04&lng=1

def get_students_list(student_name):
    params = { 'term': student_name,
               'type': 'student'}
    url = main_url+'/api/search'
    r = requests.get(url, params=params)
    return json.loads(r.text)

def get_student_schedule(student_id, start_date, end_date, lng): # ('254711', '2020.09.28','2020.10.04', 1)
    params = { 'start': start_date,
               'finish': end_date,
               'lng': 1
               }
    url = main_url + '/api/schedule/student/' + student_id
    r = requests.get(url, params=params)
    return json.loads(r.text)
