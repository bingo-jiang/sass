from django.shortcuts import render, HttpResponse, redirect
from web.forms.project_forms import ProjectForm
from django.http import JsonResponse
from django.contrib import messages
from web import models
from scripts.tencent import cos
import time
import datetime
from pypinyin import lazy_pinyin, Style


def project_list(request):
    if request.method == 'GET':
        # 展示项目
        '''
        1.从数据库获取创建的项目和参与的项目
        2.提取星标和未星标的项目
        '''
        project_dict = {'star_my': [], 'my': [], 'star_join': [], 'join': [], }
        my_project_list = models.Project.objects.filter(creator=request.current.user)
        join_project_list = models.ProjectUser.objects.filter(user=request.current.user)
        for row in my_project_list:
            if row.star:
                project_dict['star_my'].append(row)
            else:
                project_dict['my'].append(row)
        for item in join_project_list:
            if item.star:
                project_dict['star_join'].append(item)
            else:
                project_dict['join'].append(item)
        form = ProjectForm(request=request)
        return render(request, 'project_list.html', {'form': form, 'project_dict': project_dict})
    else:
        form = ProjectForm(data=request.POST, request=request)
        if form.is_valid():
            project_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            # 1.为项目创建cos桶
            # name_data = form.cleaned_data.get('name')
            # 2.中文转拼音
            # name_str_list = lazy_pinyin(name_data, style=Style.NORMAL)
            # name = ''
            # for i in name_str_list:
            #     name += i + '-'
            # 3.正式创建桶
            COS_APPID = "1305557388"
            bucket = "{}-{}-{}-{}".format(project_time, request.current.user.mobile_phone, str(int(time.time())), COS_APPID)
            region = "ap-guangzhou"
            cos.create_bucket(bucket=bucket, region=region)
            # 4.创建项目
            form.instance.bucket = bucket
            form.instance.region = region
            form.instance.creator = request.current.user# 验证通过后，还应检测当前用户是否有权限创建项目
            instance=form.save()
            #5.为项目初始化问题类型
            issues_type_obj_list=[]
            for item in models.IssuesType.PROJECT_INIT_LIST:
                issues_type_obj_list.append(models.IssuesType(project=instance,title=item))
            models.IssuesType.objects.bulk_create(issues_type_obj_list)#批量增加数据

            # messages.success(request, '项目创建成功')
            return JsonResponse({'status': True, 'data': '/project/list/'})
        else:
            return JsonResponse({'status': False, 'error': form.errors})


# 添加项目标记
def project_star(request, project_type, project_id):
    if project_type == 'my':
        models.Project.objects.filter(id=project_id, creator=request.current.user).update(star=True)
        return redirect('project_list')
    elif project_type == 'join':
        models.ProjectUser.objects.filter(project_id=project_id, user=request.current.user).update(star=True)
        return redirect('project_list')
    else:
        messages.error(request, '标记错误')
        return render(request, 'project_list.html')


# 移除项目标记
def project_unstar(request, project_type, project_id):
    if project_type == 'my':
        models.Project.objects.filter(id=project_id, creator=request.current.user).update(star=False)
        return redirect('project_list')
    elif project_type == 'join':
        models.ProjectUser.objects.filter(project_id=project_id, user=request.current.user).update(star=False)
        return redirect('project_list')
    else:
        messages.error(request, '标记错误')
        return render(request, 'project_list.html')
