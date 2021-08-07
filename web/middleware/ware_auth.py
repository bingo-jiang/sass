from django.utils.deprecation import MiddlewareMixin
from web import models
from django.contrib import messages
from django.shortcuts import render, redirect
from django.conf import settings
import datetime


class Current(object):
    def __init__(self):
        self.user = None
        self.price_policy = None
        self.project = None


class MiddleWare(MiddlewareMixin):
    def process_request(self, request):
        # 用户所有信息封装到current中
        request.current = Current()

        user_id = request.session.get('user_id', 0)
        user_obj = models.Userinfo.objects.filter(id=user_id).first()
        request.current.user = user_obj
        if request.current.user:
            # 登录后访问后台获取用户的使用额度,在Transation表中
            use_space = models.Transation.objects.filter(user=user_obj, status=1).last()
            if use_space:
                # 检测非免费版是否已过期
                if use_space.end_time and use_space.end_time < datetime.datetime.now():  # 过期
                    policy_obj = models.Transation.objects.filter(user=user_obj, status=1, price_policy__category=1).first()
                    request.current.price_policy = policy_obj.price_policy
                else:
                    request.current.price_policy = use_space.price_policy
        # 添加白名单，即不用登录也可访问的页面
        '''
        1.获取访问的url
        2.检测url是否在白名单中
        '''
        url = request.path_info

        if url == '/':
            return redirect('/index/')
        if url.split('/')[1] == 'static' and url.split('/')[2] == 'imgs':
            return
        # 在白名单中，返回空，不做其余处理
        if url in settings.WHITE_REGES_URL_LIST:
            return
        # 不在名单中，返回登录页面
        if not url in settings.WHITE_REGES_URL_LIST:
            if not request.current.user:
                # messages.info(request, '还未登录或登录认证已过期，请重新登录！')
                return redirect('/login/pwd/')
            else:
                return

        # # 登录后访问后台获取用户的使用额度,在Transation表中
        # print(user_obj)
        # use_space = models.Transation.objects.filter(user=user_obj, status=1).last()
        # print(use_space.id)
        # # 检测非免费版是否已过期
        # if use_space.end_time and use_space.end_time < datetime.datetime.now():  # 过期
        #     print('price_policy', 1)
        #     policy_obj = models.Transation.objects.filter(user=user_obj, status=1, price_policy__category=1).first()
        #     request.current.price_policy = policy_obj.price_policy
        # else:
        #     print('price_policy', 2)
        #     request.current.price_policy = use_space.price_policy

    def process_view(self, request, view, args, kwargs):
        # 判断url是否以manage开头
        if not request.path_info.startswith('/project/manage/'):
            return
        current_user = request.current.user
        project_id = kwargs.get('project_id')
        wiki_id = kwargs.get('textId')
        '''判断是否是当前用户创建的项目、参与的项目'''
        # 是否是我创建的
        project_obj = models.Project.objects.filter(creator=current_user, id=project_id).first()
        # 是否是我参与的项目
        project_user_obj = models.ProjectUser.objects.filter(user=request.current.user, project_id=project_id).first()
        if project_obj:
            request.current.project = project_obj
            return
        elif project_user_obj:
            # 是我参与的项目
            request.current.project = project_user_obj.project
            return
        else:
            return redirect('project_list')
