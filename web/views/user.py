from django.shortcuts import render, HttpResponse, redirect
from web.forms.accountforms import UserModelForm,PwdAlterModelForm
from django.http import JsonResponse
from web import models
from django.db.models import Q
import uuid
import datetime
from django.contrib import messages


def user_center(request):
    user_obj = models.Userinfo.objects.filter(username=request.current.user.username).first()
    # print(user_obj.get_sex_display())
    current_year = int(datetime.datetime.now().strftime('%Y'))
    if user_obj.birday:
        birthday = int(user_obj.birday.strftime('%Y'))
        age = current_year - birthday
    else:
        age = ''
    return render(request, 'user_center.html', {'user_obj': user_obj, 'age': age})


def user_editor(request):
    if request.method == 'GET':
        user_obj = request.current.user
        form = UserModelForm(instance=user_obj)
        return render(request, 'user_editor.html', {'form': form})
    else:
        form = UserModelForm(data=request.POST, instance=request.current.user)
        if form.is_valid():
            form.save()
            return render(request, 'user_editor.html', {'form': form})
        else:
            return render(request, 'user_editor.html', {'form': form})


def user_alter_pwd(request):
    if request.method == 'GET':
        form = PwdAlterModelForm(request=request)
        return render(request, 'user_alter_pwd.html',{'form':form})
    else:
        form=PwdAlterModelForm(request=request,data=request.POST,instance=request.current.user)
        if form.is_valid():
            form.save()
            request.session.flush()
            return redirect('login')
        else:
            return render(request,'user_alter_pwd.html',{'form':form})
