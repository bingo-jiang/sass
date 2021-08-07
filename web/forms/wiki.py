from django import forms
from web import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django_redis import get_redis_connection
from web.forms import selfwidgets
from web.forms.accountforms import BoostrapForm


class WikiModelForm(BoostrapForm, forms.ModelForm):
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        total_list = [("", "请选择(不选则默认根目录)")]
        data_list = models.Wiki.objects.filter(project=request.current.project).values_list('id', 'title')
        total_list.extend(data_list)
        self.fields['parent'].choices = total_list

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content:
            raise ValidationError('内容不应为空')
        return content

    class Meta:
        model = models.Wiki
        fields = ['title', 'content', 'parent']
        exclude = ['project', 'rank']
