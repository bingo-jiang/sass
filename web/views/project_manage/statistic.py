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


def statistic(request, project_id):
    return render(request, 'statistic.html')


def statistic_priority(request, project_id):
    start = request.GET.get('start')
    end = request.GET.get('end')
    priority_dict = collections.OrderedDict()
    for key, text in models.Issues.priority_choices:
        priority_dict[key] = {'name': text, 'y': 0}
    issues_obj = models.Issues.objects.filter(project_id=project_id, create_datetime__gte=start,
                                              create_datetime__lte=end).values('priority').annotate(ct=Count('id'))
    for item in issues_obj:
        priority_dict[item['priority']]['y'] = int(item['ct'])
    return JsonResponse({'status': True, 'data': list(priority_dict.values())})


def statistic_project_progress(request, project_id):
    """ 项目成员每个人被分配的任务数量（问题类型的配比）"""
    start = request.GET.get('start')
    end = request.GET.get('end')
    # 1. 所有项目成员 及 未指派
    all_user_dict = collections.OrderedDict()

    all_user_dict[request.current.project.creator.id] = {
        'name': request.current.project.creator.username,
        'status': {item[0]: 0 for item in models.Issues.status_choices}
    }
    all_user_dict[None] = {
        'name': '未指派',
        'status': {item[0]: 0 for item in models.Issues.status_choices}
    }
    user_list = models.ProjectUser.objects.filter(project_id=project_id)
    for item in user_list:
        all_user_dict[item.user_id] = {
            'name': item.user.username,
            'status': {item[0]: 0 for item in models.Issues.status_choices}
        }

    # 2. 去数据库获取相关的所有问题
    issues = models.Issues.objects.filter(project_id=project_id, create_datetime__gte=start, create_datetime__lt=end)
    for item in issues:
        if not item.assign:
            all_user_dict[None]['status'][item.status] += 1
        else:
            all_user_dict[item.assign_id]['status'][item.status] += 1

    # 3.获取所有的成员
    categories = [data['name'] for data in all_user_dict.values()]

    # 4.构造字典
    """
    data_result_dict = {
        1:{name:新建,data:[1，2，3，4]},
        2:{name:处理中,data:[3，4，5]},
        3:{name:已解决,data:[]},
        4:{name:已忽略,data:[]},
        5:{name:待反馈,data:[]},
        6:{name:已关闭,data:[]},
        7:{name:重新打开,data:[]},
    }
    """
    data_result_dict = collections.OrderedDict()
    for item in models.Issues.status_choices:
        data_result_dict[item[0]] = {'name': item[1], "data": []}

    for key, text in models.Issues.status_choices:
        # key=1,text='新建'
        for row in all_user_dict.values():
            count = row['status'][key]
            data_result_dict[key]['data'].append(count)

    context = {
        'status': True,
        'data': {
            'categories': categories,
            'series': list(data_result_dict.values())
        }
    }
    return JsonResponse(context)
