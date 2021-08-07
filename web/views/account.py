'''
与账号相关的功能都在此文件中书写:登录、注册、注销
'''
from django.shortcuts import render, HttpResponse, redirect
from web.forms.accountforms import RegisterModelForm, SendSmsForm, LoginSmsForm, LoginForm, UserModelForm
from django.http import JsonResponse
from web import models
from django.db.models import Q
import uuid
import datetime
from django.contrib import messages


def register(request):
    if request.method == 'GET':
        form = RegisterModelForm()
        return render(request, 'register.html', {'form': form})
    else:
        form = RegisterModelForm(data=request.POST)
        if form.is_valid():
            # 往用户表插入注册信息
            resp = form.save()
            policy_obj = models.PricePolicy.objects.filter(category=1, title='免费版', price=0).first()
            # print(policy_obj.id)
            # 往交易记录插入初始权限信息
            tran = models.Transation.objects.create(
                status=1,  # 1表示已支付
                order=str(uuid.uuid4()),
                user=resp,
                price_policy=policy_obj,
                count=0,
                price=0,
                start_time=datetime.datetime.now(),
            )
            # print(tran)
            messages.success(request, '注册成功')
            # return redirect('/login/',{'messages':messages})
            return JsonResponse({'status': True, 'data': '/login/pwd/'})
        else:
            return JsonResponse({'status': False, 'error': form.errors})


def send_sms(request):
    form = SendSmsForm(request, data=request.GET)
    if form.is_valid():
        return JsonResponse({'status': True})
    else:
        return JsonResponse({'status': False, 'error': form.errors})


def login(request):
    if request.method == 'GET':
        status = request.session.get("user_id")
        if status:
            messages.info(request, '已登录')
            return redirect('index')
        form = LoginForm(request)
        return render(request, 'login.html', {'form': form})
    else:
        # password=request.POST.get('password')
        # print(password)
        # passwd=encrypt.md5(password)
        # print(passwd)
        # return HttpResponse({password:passwd})
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            db_obj = models.Userinfo.objects.filter(
                Q(username=username) | Q(mobile_phone=username) | Q(emai=username)).filter(password=password).first()
            if db_obj:
                request.session['user_id'] = db_obj.id
                request.session.set_expiry(43200)
                id = request.session.get('user_id', 0)
                return redirect('/index/')
            else:
                form.add_error('username', '用户名或密码错误')
                return render(request, 'login.html', {'form': form})
        else:
            return render(request, 'login.html', {'form': form})


def login_sms(request):
    if request.method == 'GET':
        status = request.session.get("user_id")
        if status:
            # messages.info(request, '已登录')
            return redirect('index')
        form = LoginSmsForm()
        return render(request, 'login_sms.html', {'form': form})

    else:
        form = LoginSmsForm(data=request.POST)
        if form.is_valid():
            mobile_phone = form.cleaned_data.get('mobile_phone')
            db_obj = models.Userinfo.objects.filter(mobile_phone=mobile_phone).first()
            request.session['user_id'] = db_obj.id
            request.session.set_expiry(60 * 60 * 24)
            return JsonResponse({'status': True, 'data': '/index/'})
        else:
            return JsonResponse({'status': False, 'error': form.errors})


def logout(request):
    request.session.flush()
    return redirect('login')


