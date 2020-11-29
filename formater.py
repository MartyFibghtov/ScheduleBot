def format_shedule(schedule):

    res = ""

    for lesson in schedule:
        res += """%s
        %s
        %s - %s
        %s""" % (lesson['date'],  lesson['discipline'], lesson['beginLesson'], lesson['endLesson'], lesson['lecturer'])
        if lesson['url1'] != None:
            res += "\nURL:" + lesson['url1']

        res += "-------------"

    return res


def format_schedule_one_day(schedule):
    UTC_PLUS = 3
    if len(schedule) == 0:
        return "В этот день нет пар, отдыхаем!"

    res = schedule[0]['date_start'].split("T")[0]+"\n\n"
    res += """Пары на сегодня:"""

    for lesson in schedule:
        time_start = str(int(lesson['date_start'].split("T")[1].split(":")[0])+UTC_PLUS) + ":" + lesson['date_start'].split("T")[1].split(":")[1]

        time_end = str(int(lesson['date_end'].split("T")[1].split(":")[0])+UTC_PLUS) + ":" + lesson['date_end'].split("T")[1].split(":")[1]
        res += """
        %s
        %s - %s
        %s
        %s""" % (lesson['discipline'], time_start, time_end, lesson['auditorium'], lesson['lecturer'])

        if lesson['stream_links'] != None:
            res += "\nURL:" + lesson['stream_links'][0]['link']

        res += "\n--------------\n"

    return res


def format_students_list(students_list):
    res = ""
    for i in range(len(students_list)):
        res += "%s. %s - %s \n" % (str(i+1), students_list[i]['label'], students_list[i]['description'])

    return res
