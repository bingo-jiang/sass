from django.shortcuts import render, redirect, HttpResponse
from django.db.models import Count
from web.forms.issues_form import IssuesModelForm, IssuesReplyModelForm, InviteModelForm
from django.urls import reverse
from django.utils.safestring import mark_safe
from web import models
from django.http import JsonResponse, FileResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from scripts import pagination
import time
import datetime
import collections


def dashborde(request, project_id):
    # 数据处理
    status_dict = collections.OrderedDict()
    for key, text in models.Issues.status_choices:
        status_dict[key] = {'key': key, 'text': text, 'count': 0}
    issues_data = models.Issues.objects.filter(project_id=project_id).values('status').annotate(ct=Count('id'))
    for item in issues_data:
        status_dict[item['status']]['count'] = item['ct']

    # 项目成员
    project_user = models.ProjectUser.objects.filter(project_id=project_id).values_list('user_id', 'user__username')

    # 动态,已经指派的前十个任务
    recent_issues = models.Issues.objects.filter(project_id=project_id, assign__isnull=False).order_by(
        '-latest_update_datetime')[0:10]
    response = {
        'status_dict': status_dict,
        'project_user': project_user,
        'recent_issues': recent_issues,
    }
    return render(request, 'dashborde.html', response)


def dashborde_chart(request, project_id):
    today=datetime.datetime.now().date()
    data_dict = collections.OrderedDict()
    for i in range(0,30):
        date=today-datetime.timedelta(days=i)
        data_dict[date.strftime('%Y-%m-%d')]=[time.mktime(date.timetuple())*1000,0]
    #查数据，分组,extra()用于高级SQL语句查询
    obj=models.Issues.objects.filter(project_id=project_id,create_datetime__gte=today-datetime.timedelta(days=30)).extra(
        select={'ctime':"strftime('%%Y-%%m-%%d',web_issues.create_datetime)"}
    ).values('ctime').annotate(ct=Count('id'))
    for item in obj:
        data_dict[item['ctime']][1]=item['ct']
    return JsonResponse({'status': True, 'data': list(data_dict.values())})
