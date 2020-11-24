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
