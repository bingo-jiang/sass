from django.shortcuts import render, redirect, HttpResponse
from web.forms.file import FileModelForm, CosFileModelForm
from django.urls import reverse
from django.utils import encoding
from web import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from scripts.tencent import cos
import requests

import json


def test(request, project_id):
    return render(request, 'test.html')


def file_home(request, project_id):
    parent_obj = None
    folder = request.GET.get('folder', '')

    if folder and folder.isdecimal():
        parent_obj = models.File.objects.filter(id=int(folder), type=2, project=request.current.project).first()
        print('folder:',folder,'parent_obj:',parent_obj.filename)
    # get请求
    if request.method == 'GET':
        # 已访问的文件目录
        folder_list = []
        parent = parent_obj
        while parent:
            folder_list.insert(0, {'id': parent.id, 'filename': parent.filename})
            parent = parent.parent

        file_obj = models.File.objects.filter(project=request.current.project)
        if parent_obj:
            file = file_obj.filter(parent=parent_obj).order_by('-type')
            # print('have parent',file)
            # for i in file:
            #     print(i.filename,i.parent_id)
        else:
            file = file_obj.filter(parent__isnull=True).order_by('-type')
            # print('no parent', file)
            # for i in file:
            #     print(i.filename,i.parent_id)
        form = FileModelForm(request=request, parent_obj=parent_obj)
        return_text = {
            'form': form,
            'project_id': project_id,
            'file': file,
            'folder_list': folder_list,
            'parent_obj': parent_obj,
        }

        return render(request, 'file_home.html', return_text)
    fileId = request.POST.get('fileId')
    # 重命名
    if fileId and fileId.isdecimal():
        edit_obj = models.File.objects.filter(id=int(fileId), type=2, project=request.current.project).first()
        form = FileModelForm(request=request, parent_obj=parent_obj, data=request.POST, instance=edit_obj)
    else:
        # 新建文件夹
        form = FileModelForm(request=request, parent_obj=parent_obj, data=request.POST)

    if form.is_valid():
        # print('folder_id:', folder, 'parent_obj:', parent_obj)
        form.instance.project = request.current.project
        form.instance.update_user = request.current.user
        form.instance.type = 2
        form.instance.parent = parent_obj
        form.save()
        return JsonResponse({'status': True})
    else:
        return JsonResponse({'status': False, 'error': form.errors})


def file_delete(request, project_id):
    file_id = request.GET.get('fileId')
    file_delete_obj = models.File.objects.filter(id=file_id, project=request.current.project).first()
    if file_delete_obj:
        if file_delete_obj.type == 1:  # 文件
            request.current.project.use_space -= file_delete_obj.file_size
            request.current.project.save()
            # 从cos删除文件
            try:
                cos.delete_file(request.current.project.bucket, request.current.project.region, file_delete_obj.key)
            except Exception as e:
                pass
            finally:
                # 从数据库中删除文件
                file_delete_obj.delete()
                return JsonResponse({'status': True})

        else:  # 文件夹
            total_size = 0
            folder_list = [file_delete_obj, ]
            cos_file_key = []
            for folder in folder_list:
                child_list = models.File.objects.filter(project=request.current.project, parent=folder).order_by(
                    '-type')
                for child in child_list:
                    if child.type == 2:
                        folder_list.append(child)
                    else:
                        # 文件大小
                        total_size += child.file_size
                        # 从cos删除文件
                        # cos.delete_file(request.current.project.bucket, request.current.project.region, child.key)#逐一删除效率慢
                        cos_file_key.append({'Key': child.key})  # 固定字典格式
            # cos批量删除文件
            try:
                cos.delete_file_list(request.current.project.bucket, request.current.project.region, cos_file_key)
            except Exception as e:
                pass
            finally:
                # 归还存储容量
                if total_size:
                    request.current.project.use_space -= total_size
                    request.current.project.save()
                # 删除数据库中的文件夹
                file_delete_obj.delete()
                return JsonResponse({'status': True})
    else:
        return JsonResponse({'status': False})


@csrf_exempt
def cos_credential(request, project_id):
    '''获取cos临时凭证'''
    per_file_limit = request.current.price_policy.per_file_size * 1024 * 1024
    # 获取前端ajax发送的数据
    total_size = 0
    file_list = json.loads(request.body.decode('utf-8'))
    # 单文件限制判断
    for item in file_list:
        if per_file_limit < item['size']:
            msg = '每个文件上传的大小最大为{}M，{}文件超出限制'.format(request.current.price_policy.per_file_size, item['name'])
            return JsonResponse({'status': False, 'error': msg})
        total_size += item['size']

    # 总容量判断
    limit_space = request.current.price_policy.project_space * 1024 * 1024 * 1024  # 用户拥有的容量
    use_space = request.current.project.use_space  # 项目已用的容量
    if use_space + total_size > limit_space:
        return JsonResponse({'status': False, 'error': '容量已超出项目拥有的空间，请升级权限'})
    data_dict = cos.credential(request.current.project.bucket, request.current.project.region)
    return JsonResponse({'status': True, 'data': data_dict})


@csrf_exempt
def file_to_db(request, project_id):
    # 为了验证数据的合法性，写一个ModelForm进行校验
    form = CosFileModelForm(request=request, data=request.POST)
    parent_id = request.POST.get('parent_id','')
    parent_obj=None
    if parent_id and parent_id.isdecimal():
        parent_id=int(parent_id)
        parent_obj = models.File.objects.filter\
            (id=parent_id, project=request.current.project).first()
        print(parent_obj)
    if form.is_valid():
        # 校验通过，写入数据库
        data_dict = form.cleaned_data

        data_dict.pop('etag')
        data_dict.pop('parent')
        data_dict.update({
            'project': request.current.project,
            'type': 1, 'update_user': request.current.user,
            'parent': parent_obj,
        })
        instance = models.File.objects.create(**data_dict)

        # 更新项目已使用空间
        request.current.project.use_space += data_dict.get('file_size')
        request.current.project.save()
        result = {
            'file_id': instance.id,
            'file_name': instance.filename,
            'file_size': instance.file_size,
            'update_user': instance.update_user.username,
            'update_time': instance.update_time.strftime('%Y-%m-%d %H:%M:%S'),
            'download_url': reverse('file_download', kwargs={'project_id': project_id, 'file_id': instance.id})
            # 'type':instance.get_type_display()#展示文件类型的文字描述
        }
        return JsonResponse({'status': True, 'response': result})
    return JsonResponse({'status': False, 'error': '文件校验失败'})


def file_download(request, project_id, file_id):
    '''文件下载'''
    # 1.找到文件，读取内容
    # 2.返回响应头

    file_obj = models.File.objects.filter(id=file_id, project_id=project_id).first()
    res = requests.get(file_obj.file_path)
    data = res.content
    response = HttpResponse(data, content_type="application/octet-stream")
    response['Content-Disposition'] = 'attachment;filename={}'.format(encoding.escape_uri_path(file_obj.filename))
    return response
