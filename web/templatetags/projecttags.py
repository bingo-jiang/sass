from django.template import Library
from web import models
from django.shortcuts import render
register=Library()


@register.inclusion_tag('inclusion/all_project_list.html')
def all_project_list(request):
    # 我的项目
    my_project=models.Project.objects.filter(creator=request.current.user)

    # 我参与的项目
    join_project=models.ProjectUser.objects.filter(user=request.current.user)

    return {'my_project':my_project,'join_project':join_project}