from django.template import Library
from web import models
from django.shortcuts import render
from django.urls import reverse

register = Library()


@register.simple_tag
def space_trans(size):
    if size >= 1024 * 1024 * 1024:
        return "%.2f GB" % (size / (1024 * 1024 * 1024))
    elif size >= 1024 * 1024:
        return "%.2f MB" % (size / (1024 * 1024))
    elif size >= 1024:
        return "%.2f KB" % (size / (1024))
    else:
        return "%d KB" % (size)
