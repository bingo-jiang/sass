from django.shortcuts import render, redirect, HttpResponse
from web.forms.issues_form import IssuesModelForm, IssuesReplyModelForm, InviteModelForm
from django.urls import reverse
from django.utils.safestring import mark_safe
from web import models
from django.http import JsonResponse, FileResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from scripts import pagination
import json
from scripts.encrypt import uid
import datetime
import time


class CheckFilter(object):
    def __init__(self, name, data_list, request):
        self.name = name
        self.data_list = data_list
        self.request = request

    def __iter__(self):
        for item in self.data_list:
            key = str(item[0])
            text = item[1]
            ck = ""
            # 如果当前用户请求的URL中status和当前循环key相等
            value_list = self.request.GET.getlist(self.name)
            if key in value_list:
                ck = 'checked'
                value_list.remove(key)
            else:
                value_list.append(key)

            # 为自己生成URL
            # 在当前URL的基础上去增加一项
            # status=1&age=19
            from django.http import QueryDict
            query_dict = self.request.GET.copy()
            query_dict._mutable = True
            query_dict.setlist(self.name, value_list)
            if 'page' in query_dict:
                query_dict.pop('page')

            param_url = query_dict.urlencode()
            if param_url:
                url = "{}?{}".format(self.request.path_info, param_url)  # status=1&status=2&status=3&xx=1
            else:
                url = self.request.path_info

            tpl = '<a class="cell" href="{url}"><input type="checkbox" {ck} /><label>{text}</label></a>'
            html = tpl.format(url=url, ck=ck, text=text)
            yield mark_safe(html)

    def get_name(self):
        return self.name


class SelectFilter(object):
    def __init__(self, name, data_list, request):
        self.name = name
        self.data_list = data_list
        self.request = request

    def __iter__(self):
        yield mark_safe(
            "<label style='width:96%'><select class='select2' name='select2' multiple='multiple' style='width:96%'>")
        for item in self.data_list:
            key = str(item[0])
            text = item[1]

            selected = ""
            value_list = self.request.GET.getlist(self.name)
            if key in value_list:
                selected = 'selected'
                value_list.remove(key)
            else:
                value_list.append(key)

            query_dict = self.request.GET.copy()
            query_dict._mutable = True
            query_dict.setlist(self.name, value_list)
            if 'page' in query_dict:
                query_dict.pop('page')

            param_url = query_dict.urlencode()
            if param_url:
                url = "{}?{}".format(self.request.path_info, param_url)  # status=1&status=2&status=3&xx=1
            else:
                url = self.request.path_info

            html = "<option value='{url}' {selected} >{text}</option>".format(url=url, selected=selected, text=text)
            yield mark_safe(html)
        yield mark_safe("</select></label>")

    def get_name(self):
        return self.name


def issues(request, project_id):
    if request.method == 'GET':
        # 允许的筛选条件
        allow_filter_name = ['issues_type', 'status', 'priority', 'assign', 'attention']
        condition = {}
        for name in allow_filter_name:
            value_list = request.GET.getlist(name)
            if not value_list:
                continue
            condition['{}__in'.format(name)] = value_list

        # 分页处理
        issues_all_obj = models.Issues.objects.filter(project_id=project_id).filter(**condition)
        pagination_obj = pagination.Pagination(
            current_page=request.GET.get('page'),
            all_count=issues_all_obj.count(),
            base_url=request.path_info,
            query_params=request.GET,
        )
        form = IssuesModelForm(request)
        issues_list = issues_all_obj[pagination_obj.start:pagination_obj.end]

        project_issues_type = models.IssuesType.objects.filter(project_id=project_id).values_list('id', 'title')
        project_total_user = [(request.current.project.creator_id, request.current.project.creator.username,)]
        join_user = models.ProjectUser.objects.filter(project_id=project_id).values_list('user_id', 'user__username')
        project_total_user.extend(join_user)

        invite_form = InviteModelForm()
        res_dict = {
            'form': form,
            'invite_form': invite_form,
            'issues_list': issues_list,
            'page_html': pagination_obj.page_html(),
            'filter_list': [
                {'title': "问题类型", 'filter': CheckFilter('issues_type', project_issues_type, request)},
                {'title': "状态", 'filter': CheckFilter('status', models.Issues.status_choices, request)},
                {'title': "优先级", 'filter': CheckFilter('priority', models.Issues.priority_choices, request)},
                {'title': "指派者", 'filter': SelectFilter('assign', project_total_user, request)},
                {'title': "关注者", 'filter': SelectFilter('attention', project_total_user, request)},
            ],
        }
        return render(request, 'issues.html', res_dict)

    else:
        form = IssuesModelForm(request=request, data=request.POST)
        if form.is_valid():
            form.instance.project = request.current.project
            form.instance.creator = request.current.user
            form.save()
            return JsonResponse({'status': True})
        else:
            return JsonResponse({'status': False, 'error': form.errors})


def select_test(request, project_id):
    return render(request, 'test.html')


def issues_detail(request, project_id, issues_id):
    if request.method == 'GET':
        issues_obj = models.Issues.objects.filter(id=issues_id, project_id=project_id).first()
        form = IssuesModelForm(request, instance=issues_obj)
        resp = {
            'form': form,
            'issues_obj': issues_obj,
            'issues_id': issues_id,
        }
        return render(request, 'issues_detail.html', resp)
    else:
        instance = models.Issues.objects.filter(id=issues_id, project_id=project_id).first()
        form = IssuesModelForm(request, data=request.POST, instance=instance)
        if form.is_valid():
            form.instance.project = request.current.project
            form.instance.creator = request.current.user
            form.save()
            # models.IssuesReply.objects.update(form.cleaned_data)
            url = reverse('issues_detail', kwargs={'project_id': project_id, 'issues_id': issues_id})
            return redirect(url)


@csrf_exempt
def issues_record(request, project_id, issues_id):
    if request.method == 'GET':
        reply_list = models.IssuesReply.objects.filter(issues_id=issues_id, issues__project=request.current.project)
        # 将reply原queryset类型转为json格式
        data_list = []
        for row in reply_list:
            data = {
                'id': row.id,
                'reply_type': row.get_reply_type_display(),
                'content': row.content,
                'creator': row.creator.username,
                'create_datetime': row.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                'parent_id': row.reply_id,
            }
            data_list.append(data)
        return JsonResponse({'status': True, 'data': data_list})
    # POST请求
    else:
        form = IssuesReplyModelForm(data=request.POST)
        print(request.POST)
        if form.is_valid():
            form.instance.creator = request.current.user
            form.instance.issues_id = issues_id
            form.instance.reply_type = 2
            row = form.save()
            info = {
                'id': row.id,
                'reply_type': row.get_reply_type_display(),
                'content': row.content,
                'creator': row.creator.username,
                'create_datetime': row.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                'parent_id': row.reply_id,
            }
            return JsonResponse({'status': True, 'data': info})
        else:
            return JsonResponse({'status': False, 'error': form.errors})


@csrf_exempt
def issues_change(request, project_id, issues_id):
    issues_obj = models.Issues.objects.filter(id=issues_id, project_id=project_id).first()
    post_dict = json.loads(request.body.decode('utf-8'))
    name = post_dict.get('name')
    value = post_dict.get('value')
    field_obj = models.Issues._meta.get_field(name)
    # 数据库更新# 生成更新记录
    # 1.文本
    if name in ['subject', 'desc', 'start_date', 'end_date']:
        if not value:
            if not field_obj.null:
                return JsonResponse({'status': False, 'error': '更改的字段不能为空'})
            else:
                setattr(issues_obj, name, None)
                issues_obj.save()
                change_info = "{}更改为空".format(field_obj.verbose_name)
        else:
            setattr(issues_obj, name, value)
            issues_obj.save()
            change_info = "{}更改为{}".format(field_obj.verbose_name, value)
        row = models.IssuesReply.objects.create(
            reply_type=1,
            issues=issues_obj,
            content=change_info,
            creator=request.current.user,
        )
        info = {
            'id': row.id,
            'reply_type': row.get_reply_type_display(),
            'content': row.content,
            'creator': row.creator.username,
            'create_datetime': row.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'parent_id': row.reply_id,
        }
        return JsonResponse({'status': True, 'data': info})

    # 2.ForeignKey
    if name in ['issues_type', 'module', 'parent', 'assign']:
        if not value:  # 输入值为空
            if not field_obj.null:
                return JsonResponse({'status': False, 'error': '更改的字段不能为空'})
            else:
                setattr(issues_obj, name, None)
                issues_obj.save()
                change_info = "{}更改为空".format(field_obj.verbose_name)
        else:  # 输入值不为空
            if name == 'assign':
                if value == str(request.current.project.creator_id):
                    instance = request.current.project.creator
                else:
                    project_user = models.ProjectUser.objects.filter(project_id=project_id, user_id=value).first()
                    if project_user:
                        instance = project_user.user
                    else:
                        instance = None
                if not instance:
                    return JsonResponse({'status': False, 'error': '输入值不能为空'})

                setattr(issues_obj, name, instance)
                issues_obj.save()
                change_info = "{}更改为{}".format(field_obj.verbose_name, str(instance))
            else:  # 判断用户输入的值是否是自己拥有的
                instance = field_obj.rel.model.objects.filter(id=value, project_id=project_id).first()
                if not instance:
                    return JsonResponse({'status': False, 'error': '更改的字段不存在'})
                setattr(issues_obj, name, instance)
                issues_obj.save()
                change_info = "{}更改为{}".format(field_obj.verbose_name, str(instance))
        row = models.IssuesReply.objects.create(
            reply_type=1,
            issues=issues_obj,
            content=change_info,
            creator=request.current.user,
        )
        info = {
            'id': row.id,
            'reply_type': row.get_reply_type_display(),
            'content': row.content,
            'creator': row.creator.username,
            'create_datetime': row.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'parent_id': row.reply_id,
        }
        return JsonResponse({'status': True, 'data': info})

    # 3.choices字段
    if name in ['status', 'priority', 'mode']:
        selected_text = None
        for key, text in field_obj.choices:
            if str(key) == value:
                selected_text = text
        if not selected_text:
            return JsonResponse({'status': False, 'error': '更改的内容不存在'})
        setattr(issues_obj, name, value)
        issues_obj.save()
        change_info = "{}更改为{}".format(field_obj.verbose_name, selected_text)
        row = models.IssuesReply.objects.create(reply_type=1, issues=issues_obj, content=change_info,
                                                creator=request.current.user)
        info = {
            'id': row.id,
            'reply_type': row.get_reply_type_display(),
            'content': row.content,
            'creator': row.creator.username,
            'create_datetime': row.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'parent_id': row.reply_id,
        }
        return JsonResponse({'status': True, 'data': info})
    # 4.ManyToMany
    if name == 'attention':
        if not isinstance(value, list):
            return JsonResponse({'status': False, 'error': '输入格式错误'})

        else:
            if not value:  # 没有选择关注者
                issues_obj.attention.set(value)
                issues_obj.save()
                change_info = "{}更改为空".format(field_obj.verbose_name)
                row = models.IssuesReply.objects.create(reply_type=1, issues=issues_obj, content=change_info,
                                                        creator=request.current.user)
                info = {
                    'id': row.id,
                    'reply_type': row.get_reply_type_display(),
                    'content': row.content,
                    'creator': row.creator.username,
                    'create_datetime': row.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    'parent_id': row.reply_id,
                }
                return JsonResponse({'status': True, 'data': info})
            else:
                # 判断是否为项目成员的id
                user_id_dict = {str(request.current.project.creator_id): request.current.project.creator.username}
                project_user = models.ProjectUser.objects.filter(project_id=project_id)
                username_list = []
                for item in project_user:
                    user_id_dict[str(item.user_id)] = item.user.username
                for user_id in value:
                    username = user_id_dict.get(str(user_id))
                    if not username:
                        return JsonResponse({'status': False, 'error': '项目成员不存在'})
                    username_list.append(username)
                issues_obj.attention.set(value)
                issues_obj.save()
                change_info = "{}更改为{}".format(field_obj.verbose_name, ','.join(username_list))
                row = models.IssuesReply.objects.create(reply_type=1, issues=issues_obj, content=change_info,
                                                        creator=request.current.user)
                info = {
                    'id': row.id,
                    'reply_type': row.get_reply_type_display(),
                    'content': row.content,
                    'creator': row.creator.username,
                    'create_datetime': row.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    'parent_id': row.reply_id,
                }
                return JsonResponse({'status': True, 'data': info})

    return JsonResponse({'status': False, 'error': '你正在非法访问网站'})


def invite(request, project_id):
    '''成员邀请'''
    form = InviteModelForm(request.POST)
    if form.is_valid():
        '''
        1.创建邀请码
        2.保存邀请码到数据库
        3.限制：创建者才能邀请
        '''
        if request.current.user != request.current.project.creator:
            form.add_error('period', '只有项目创建者才能邀请成员')
            return JsonResponse({'status': False, 'error': form.errors})
        invite_code = uid(request.current.user.mobile_phone)
        form.instance.code = invite_code
        form.instance.project = request.current.project
        form.instance.creator = request.current.user
        form.save()

        # 将邀请码返回前端
        url = "{scheme}://{host}{path}".format(
            scheme=request.scheme,
            host=request.get_host(),
            path=reverse('invite_join', kwargs={'code': invite_code})
        )
        return JsonResponse({'status': True, 'data': url})
    else:
        return JsonResponse({'status': False, 'error': form.errors})


def invite_join(request, code):
    current_time = datetime.datetime.now()
    invite_obj = models.ProjectInvite.objects.filter(code=code).first()
    if not invite_obj:
        return render(request, 'invite_join.html', {'error': '邀请码不存在'})
    if invite_obj.project.creator == request.current.user:
        return render(request, 'invite_join.html', {'error': '您是项目创建者，无需再加入项目'})
    exits = models.ProjectUser.objects.filter(project=invite_obj.project, user=request.current.user).exists()
    if exits:
        return render(request, 'invite_join.html', {'error': '您已加入该项目'})

    # 项目人数限制判断
    # 1.最大成员数(项目创建者所拥有的的权限）
    # max_member = request.current.price_policy.project_member   当前登录用户的权限

    max_transaction = models.Transation.objects.filter(user=invite_obj.project.creator, status=1).order_by(
        '-id').first()
    if max_transaction.price_policy.category == 1:
        max_member = max_transaction.price_policy.project_member
    else:
        if current_time > max_transaction.end_time:
            free_policy = models.PricePolicy.objects.filter(category=1).first()
            max_member = free_policy.project_member
        else:
            max_member = max_transaction.price_policy.project_member
    # 当前成员数(不包含创建者)
    current_member = models.ProjectUser.objects.filter(project=invite_obj.project).count()
    if current_member >= max_member:
        return render(request, 'invite_join.html', {'error': '项目成员数已经达到上限'})
    # 邀请码是否过期

    limit_time = invite_obj.create_datetime + datetime.timedelta(minutes=invite_obj.period)
    if current_time >= limit_time:
        return render(request, 'invite_join.html', {'error': '邀请码已过期'})
    # 邀请码邀请人数限制
    if invite_obj.count:
        if invite_obj.use_count >= invite_obj.count:
            return render(request, 'invite_join.html', {'error': '邀请人数已达上限'})
        invite_obj.use_count += 1
        invite_obj.save()
    models.ProjectUser.objects.create(project=invite_obj.project, user=request.current.user, invitor=invite_obj.creator)
    invite_obj.project.join_count += 1
    invite_obj.project.save()
    return render(request, 'invite_join.html', {'invite_obj': invite_obj})


@csrf_exempt
def issues_delete(request, project_id):
    # 1.是否为项目创建者，不是不能进行删除操作
    # 2.是否是当前项目
    # 3.问题id是否存在
    issues_id_list = dict(request.POST).values()
    project_obj = models.Project.objects.filter(id=project_id).first()
    if request.current.user != project_obj.creator:
        return JsonResponse({'status': False, 'error': '非项目创建者，不能进行此操作'})
    id_list = []
    if not issues_id_list:
        return JsonResponse({'status': False})
    for item in issues_id_list:
        issues_id = int(item[0])
        id_list.append(issues_id)
        issues_obj = models.Issues.objects.filter(id=issues_id).first()
        print(issues_id)
        if not issues_obj:
            return JsonResponse({'status': False, 'error': '不存在此问题ID'})
        if issues_obj.project_id != request.current.project.id:
            return JsonResponse({'status': False, 'error': '非本项目问题，不能进行此操作'})
    models.Issues.objects.filter(id__in=id_list).delete()
    return JsonResponse({'status': True})
