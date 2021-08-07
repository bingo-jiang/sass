from django.shortcuts import render, redirect, HttpResponse
from web.forms.wiki import WikiModelForm
from django.urls import reverse
from django.contrib import messages
from web import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from scripts.encrypt import uid
from scripts.tencent import cos


def wiki_index(request, project_id):
    textId = request.GET.get('textId')
    if textId:
        if not textId.isdecimal():
            return render(request, 'wiki.html')
        else:
            wiki_text_obj = models.Wiki.objects.filter(project_id=project_id, id=textId).first()
            return render(request, 'wiki.html', {"project_id": project_id, "wiki_text_obj": wiki_text_obj})
    else:
        return render(request, 'wiki.html')


def wiki_add(request, project_id):
    if request.method == 'GET':
        form = WikiModelForm(request)
        return render(request, 'wiki_form.html', {'form': form})
    else:
        form = WikiModelForm(request=request, data=request.POST)
        if form.is_valid():
            form.instance.project = request.current.project
            if form.instance.parent:
                form.instance.rank = form.instance.parent.rank + 1
            form.save()
            url = reverse('wiki_index', kwargs={'project_id': project_id})
            # messages.success(request, 'wiki文档添加成功')
            return redirect(url)
        else:
            # messages.error(request, '未知错误')
            print(form.errors)
            return render(request, 'wiki_form.html', {'form': form})


def wiki_catalog(request, project_id):
    data = models.Wiki.objects.filter(project_id=project_id).all().values('id', 'title', 'parent_id').order_by('rank',
                                                                                                               'id')
    return JsonResponse({'status': True, 'data': list(data)})


def wiki_delete(request, project_id, textId):
    models.Wiki.objects.filter(id=textId, project_id=project_id).delete()
    url = reverse('wiki_index', kwargs={'project_id': project_id})
    return redirect(url)
    # messages.success(request,'删除成功')
    # return JsonResponse({'status': True, 'data': url})


def wiki_edit(request, project_id, textId):
    wiki_text_obj = models.Wiki.objects.filter(id=textId, project_id=project_id).first()
    if not wiki_text_obj:
        url = reverse('wiki_index', kwargs={'project_id': project_id})
        return redirect(url)
    if request.method == 'GET':
        form = WikiModelForm(request, instance=wiki_text_obj)
        return render(request, 'wiki_form.html', {'form': form, 'wiki_text_obj': wiki_text_obj})
    form = WikiModelForm(request, data=request.POST, instance=wiki_text_obj)
    if form.is_valid():
        form.instance.project = request.current.project
        if form.instance.parent:
            form.instance.rank = form.instance.parent.rank + 1
        else:
            form.instance.rank = 1
        form.save()
        url = reverse('wiki_edit', kwargs={'project_id': project_id,'textId':textId})
        # edit_url = "{0}/{1}/".format(url, textId)
        return redirect(url)
    else:
        return render(request, 'wiki_form.html', {'form': form, 'wiki_text_obj': wiki_text_obj})


@csrf_exempt
def wiki_img_upload(request, project_id):
    # 初始化返回结果
    result = {'success': 0, 'message': None, 'url': None}  # Markdown要求的固定的返回结果格式

    img_obj = request.FILES.get('editormd-image-file')  # 获取上传的文件对象

    # 如果文件上传失败
    if not img_obj:
        result['message'] = "文件不存在"
        return JsonResponse(result)

    # 处理文件的名称
    img_type = img_obj.name.rsplit('.')
    img_name = "{}.{}".format(uid(request.current.user.mobile_phone), img_type[-1])

    img_url = cos.upload_file(bucket=request.current.project.bucket, region=request.current.project.region, file_object=img_obj,
                              key=img_name)
    # print(img_url)
    result['success'] = 1
    result['url'] = img_url
    return JsonResponse(result)
