from django.shortcuts import render, redirect
from web.forms.issues_form import InviteModelForm, ModuleModelForm
from web import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from scripts.tencent import cos
import datetime
from django.urls import reverse


def settings(request, project_id):
    if request.method == 'GET':
        invite_form = InviteModelForm()
        module_form = ModuleModelForm()
        project_obj = models.Project.objects.filter(id=project_id).first()
        res = {
            'project_obj': project_obj,
            'invite_form': invite_form,
            'module_form': module_form,
        }
        return render(request, 'settings.html', res)


def settings_delete(request, project_id):
    if request.method == 'GET':
        invite_form = InviteModelForm()
        res = {
            'invite_form': invite_form,
        }
        return render(request, 'settings_delete.html', res)
    else:
        project_name = request.POST.get('project_name')
        if not project_name or project_name != request.current.project.name:
            return render(request, 'settings_delete.html', {'error': '输入为空或非当前项目名，请重新输入'})
        if request.current.user != request.current.project.creator:
            return render(request, 'settings_delete.html', {'error': '非项目创建者，不可删除'})

        # 删除桶
        cos.delete_bucket(request.current.project.bucket, request.current.project.region)
        # 删除数据库数据
        models.Project.objects.filter(id=request.current.project.id).delete()
        return redirect('project_list')


def module(request, project_id):
    if request.method == 'GET':
        invite_form = InviteModelForm()
        module_form = ModuleModelForm()
        module_obj = models.Module.objects.filter(project_id=project_id).all()
        res = {
            'invite_form': invite_form,
            'module_obj': module_obj,
            'module_form': module_form,
        }
        return render(request, 'settings_module.html', res)


def delete_module(request, project_id):
    moduleId = request.GET.get('moduleId')
    if moduleId and moduleId.isdecimal():
        module_delete = models.Module.objects.filter(id=int(moduleId), project_id=project_id)
        if module_delete:
            module_delete.delete()
            return JsonResponse({'status': True})
        else:
            return JsonResponse({'status': False, 'error': '请求数据错误'})
    else:
        return JsonResponse({'status': False, 'error': '请求参数错误'})


@csrf_exempt
def add_module(request, project_id):
    form = ModuleModelForm(data=request.POST)
    moduleId = request.POST.get('moduleId')
    new_title = request.POST.get('moduleTitle')
    # 重命名
    if moduleId and new_title and moduleId.isdecimal():
        module_instance = models.Module.objects.filter(id=moduleId).first()
        if not module_instance:
            return JsonResponse({'status': False, 'error': '没有该模块'})
        if request.current.user != request.current.project.creator:
            form.add_error('title', '只有项目创建者才能修改')
            return JsonResponse({'status': False, 'error': form.errors})
        module_obj = models.Module.objects.filter(project_id=project_id).all()
        for item in module_obj:
            flags = 0
            if new_title == item.title:
                form.add_error('title', '已有该问题模块或名称没有变化')
                flags = 1
                return JsonResponse({'status': False, 'error': form.errors})
            if flags == 1:
                break
        models.Module.objects.filter(id=moduleId).update(title=new_title, project_id=project_id)
        return JsonResponse({'status': True, 'data': '模块修改成功，请继续操作！'})
    # 新建
    else:
        new_title = request.POST.get('title')
        if form.is_valid():
            if request.current.user != request.current.project.creator:
                form.add_error('title', '只有项目创建者才能添加问题模块')
                return JsonResponse({'status': False, 'error': form.errors})
            module_obj = models.Module.objects.filter(project_id=project_id).all()
            for item in module_obj:
                flags = 0
                if new_title == item.title:
                    form.add_error('title', '已有该问题模块')
                    flags = 1
                    return JsonResponse({'status': False, 'error': form.errors})
                if flags == 1:
                    break
            form.instance.project = request.current.project
            form.save()
            return JsonResponse({'status': True, 'data': '模块添加成功，请继续操作！'})
        else:
            return JsonResponse({'status': False, 'error': form.errors})


def member(request, project_id):
    invite_form = InviteModelForm()
    # 1.创建者
    project_creator_obj = models.Project.objects.filter(id=project_id).first()
    # 2.参与者
    member_obj = models.ProjectUser.objects.filter(project_id=project_id).all
    res = {
        'invite_form': invite_form,
        'project_creator_obj': project_creator_obj,
        'member_obj': member_obj,
    }
    return render(request, 'settings_member.html', res)


def member_delete(request, project_id):
    member_id = request.GET.get('memberId')
    member_obj = models.ProjectUser.objects.filter(id=member_id, project_id=project_id).first()
    if not member_obj:
        return JsonResponse({'status': False, 'data': '非项目成员'})
    if request.current.user != member_obj.project.creator:
        return JsonResponse({'status': False, 'data': '非项目创建者，不能剔除成员'})
    member_obj.delete()
    return JsonResponse({'status': True})


def invite_code(request, project_id):
    invite_form = InviteModelForm()
    # 邀请码
    code_valid_list = []
    code_expire_list = []
    code_obj = models.ProjectInvite.objects.filter(project_id=project_id).all()
    # 邀请码是否过期
    current_time = datetime.datetime.now()
    for item in code_obj:
        limit_time = item.create_datetime + datetime.timedelta(minutes=item.period)  # 截止时间
        # 邀请码链接拼接
        url = "{scheme}://{host}{path}".format(
            scheme=request.scheme,
            host=request.get_host(),
            path=reverse('invite_join', kwargs={'code': item.code})
        )
        # 邀请码对象
        data_dict = {'obj': item, 'limit_time': limit_time, 'url': url}
        if current_time >= limit_time:  # 无效邀请码
            code_expire_list.append(data_dict)
        else:  # 有效邀请码
            code_valid_list.append(data_dict)
    res = {
        'invite_form': invite_form,
        'code_valid_list': code_valid_list,
        'code_expire_list': code_expire_list,
    }
    return render(request, 'settings_invite_code.html', res)


def invite_code_delete(request, project_id):
    # 单次删除
    code_id = request.GET.get('codeId')
    operate_type = request.GET.get('operateType')
    #单次删除
    if operate_type == 'one':
        code_obj = models.ProjectInvite.objects.filter(id=code_id, project_id=project_id).first()
        if not code_obj:
            return JsonResponse({'status': False, 'data': '该邀请码不存在!'})
        if request.current.user != code_obj.project.creator:
            return JsonResponse({'status': False, 'data': '非项目创建者，不能进行此操作!'})
        code_obj.delete()
        return JsonResponse({'status': True})

    all_code_obj = models.ProjectInvite.objects.filter(project_id=project_id).all()
    current_time = datetime.datetime.now()

    # 删除全部有效邀请码
    if operate_type == 'all_valid':
        # 邀请码是否过期
        for item in all_code_obj:
            limit_time = item.create_datetime + datetime.timedelta(minutes=item.period)  # 截止时间
            if current_time >= limit_time:  # 无效邀请码
                continue
            else:
                item.delete()
        return JsonResponse({'status': True})

    # 删除全部无效邀请码
    if operate_type == 'all_expire':
        for item in all_code_obj:
            limit_time = item.create_datetime + datetime.timedelta(minutes=item.period)  # 截止时间
            if current_time >= limit_time:  # 无效邀请码
                item.delete()
            else:
                continue
        return JsonResponse({'status': True})
    # 以上请求都出错
    else:
        return JsonResponse({'status': False,'data':'非法请求!'})
