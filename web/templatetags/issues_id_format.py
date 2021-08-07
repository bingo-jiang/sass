#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.template import Library
from django.urls import reverse
from web import models

register = Library()


@register.simple_tag
def string_just(num):
    if int(num) < 1000:
        num = str(num).rjust(4, "0")
    return "#{}".format(num)