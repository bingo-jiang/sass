from django.template import Library
import datetime

register = Library()


@register.simple_tag
def compute(birthday):
    if birthday:
        current_year = int(datetime.datetime.now().strftime('%Y'))
        birth_year = int(birthday.strftime('%Y'))
        age = current_year - birth_year
        return '{}岁'.format(int(age))
    else:
        return '#岁(未填写)'
