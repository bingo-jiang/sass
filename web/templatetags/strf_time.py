from django.template import Library

register = Library()


@register.simple_tag
def trans_time(time):
    return time.strftime("%Y-%m-%d %H:%M:%S")


@register.simple_tag
def minute_to_hour(minute):
    minute = int(minute)
    if minute>60:
        hour = minute / 60
        remainder = minute % 60
        if remainder == 0:
            return "{}小时".format(int(hour))
        else:
            return "{}小时".format(hour)
    else:
        return "{}分钟".format(minute)

@register.simple_tag
def datetime_format(time):
    return time.strftime("%Y-%m-%d %H:%M")
