from django import forms
from web import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django_redis import get_redis_connection
from web.forms import selfwidgets
from web.forms.accountforms import BoostrapForm


class IssuesModelForm(BoostrapForm, forms.ModelForm):
    class Meta:
        model = models.Issues
        exclude = ['project', 'creator', 'create_datetime', 'latest_update_datetime']
        widgets = {
            'mode': forms.Select(attrs={'class': 'selectpicker show-tick'}),
            'priority': forms.Select(attrs={'class': 'selectpicker show-tick'}),
            'assign': forms.Select(attrs={'class': 'selectpicker show-tick', 'data-live-search': 'true'}),
            'issues_type': forms.Select(attrs={'class': 'selectpicker show-tick', 'data-live-search': 'true'}),
            'module': forms.Select(attrs={'class': 'selectpicker show-tick', }),
            'status': forms.Select(attrs={'class': 'selectpicker show-tick', }),
            'attention': forms.SelectMultiple(attrs={'class': 'selectpicker show-tick', 'data-actions-box': 'true'}),
            'parent': forms.Select(attrs={'class': 'selectpicker show-tick', 'data-live-search': 'true'}),
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

        # 数据初始化
        # 获取当前项目的所有问题类型
        issues_type = models.IssuesType.objects.filter(project=self.request.current.project).values_list('id', 'title')
        self.fields['issues_type'].choices = issues_type

        # 获取当前项目的所有模块
        module_list = [('', '忽略，不选'), ]
        module = models.Module.objects.filter(project=self.request.current.project).values_list('id', 'title')
        module_list.extend(module)
        self.fields['module'].choices = module_list

        # 指派给的用户
        # (1)找到项目的创建者和参与者
        total_user_list = [(self.request.current.project.creator_id, self.request.current.project.creator.username), ]
        project_user = models.ProjectUser.objects.filter(project=self.request.current.project).values_list('user_id',
                                                                                                           'user__username')
        total_user_list.extend(project_user)
        self.fields['assign'].choices = [('', '忽略，不选')] + total_user_list
        self.fields['attention'].choices = total_user_list

        # 当前项目已创建的所有问题
        question_list = [('', '忽略，不选')]
        question_obj = models.Issues.objects.filter(project=self.request.current.project).values_list('id', 'subject')
        question_list.extend(question_obj)
        self.fields['parent'].choices = question_list


class IssuesReplyModelForm(BoostrapForm, forms.ModelForm):
    class Meta:
        model = models.IssuesReply
        fields = ['content', 'reply']

    def clean_reply(self):
        reply_id = self.cleaned_data.get('reply')
        # reply=models.IssuesReply.objects.filter(id=reply_id).first()
        return reply_id


class InviteModelForm(BoostrapForm, forms.ModelForm):
    class Meta:
        model = models.ProjectInvite
        fields = ['period', 'count']


class ModuleModelForm(BoostrapForm, forms.ModelForm):
    class Meta:
        model = models.Module
        fields = ['title']
