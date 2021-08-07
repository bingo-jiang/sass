from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from web import models
from django_redis import get_redis_connection
import datetime
import json
from scripts import encrypt
from scripts import alipay
from django.conf import settings
from django.contrib import messages


def index(request):
    if request.method == 'GET':
        return render(request, 'index.html')


def price(request):
    policy_list = models.PricePolicy.objects.filter(category=2)
    per_file_size_list = []
    for i in policy_list:
        per_list = [i.title, int(i.per_file_size) * 1024 * 1024]
        per_file_size_list.append(per_list)
    result = {
        'policy_list': policy_list,
        'per_file_size_list': per_file_size_list,
    }
    return render(request, 'price.html', result)


def payment(request, policy_id):
    # 套餐id
    policy_obj = models.PricePolicy.objects.filter(id=policy_id, category=2).first()

    if not policy_obj:
        print(1)
        return redirect('price')
    # 购买数量
    number = request.GET.get('number', '')
    if not number or not number.isdecimal():
        print(2)
        return redirect('price')
    number = int(number)
    if number < 1:
        print(3)
        return redirect('price')
    # 计算原价
    origin_price = number * int(policy_obj.price)
    # 之前购买过套餐，现在升级套餐
    discount = 0
    transact_obj = None
    print(request.current.user.username)
    if request.current.price_policy.category == 2:
        transact_obj = models.Transation.objects.filter(user=request.current.user, status=1).order_by('-id').first()
        total_time = transact_obj.end_time - transact_obj.start_time
        discount_time = transact_obj.end_time - datetime.datetime.now()
        discount = (int(transact_obj.price_policy.price) / total_time.days) * (discount_time.days)
        if discount >= origin_price:
            return redirect('price')
    res = {
        'policy_id': policy_obj.id,
        'number': number,
        'origin_price': origin_price,
        'discount': round(discount, 2),
        'real_price': int(origin_price) - round(discount, 2),
    }
    conn = get_redis_connection()
    key = "payment_{}".format(request.current.user.mobile_phone)
    conn.set(key, json.dumps(res), ex=60 * 15)

    res['policy_obj'] = policy_obj
    res['transaction'] = transact_obj

    return render(request, 'payment.html', res)


def pay(request):
    conn = get_redis_connection()
    key = "payment_{}".format(request.current.user.mobile_phone)
    order = conn.get(key)
    if not order:
        redirect('price')
    order_context = json.loads(order.decode('utf-8'))

    order_id = str(encrypt.uid(request.current.user.mobile_phone))
    total_price = order_context['real_price']
    # 保存到数据库（未支付状态）
    tran_obj = models.Transation.objects.create(
        status=0,  # 0表示未支付
        order=order_id,
        user=request.current.user,
        price_policy_id=order_context['policy_id'],
        count=order_context['number'],
        price=total_price,
    )
    # 跳转到支付宝进行支付
    ali_pay = alipay.AliPay(
        appid=settings.ALI_APP_ID,
        app_notify_url=settings.ALI_NOTIFY_URL,
        return_url=settings.ALI_RETURN_URL,
        app_private_key_path=settings.ALI_PRI_KEY_PATH,
        alipay_public_key_path=settings.ALI_PUB_KEY_PATH
    )
    query_params = ali_pay.direct_pay(
        subject="用户升级权限，{}套餐支付".format(tran_obj.price_policy.title),  # 商品简单描述
        out_trade_no=order_id,  # 商户订单号
        total_amount=total_price
    )
    pay_url = "{}?{}".format(settings.ALI_GATEWAY, query_params)
    return redirect(pay_url)


def pay_notify(request):
    """ 支付成功之后触发的URL """
    ali_pay = alipay.AliPay(
        appid=settings.ALI_APP_ID,
        app_notify_url=settings.ALI_NOTIFY_URL,
        return_url=settings.ALI_RETURN_URL,
        app_private_key_path=settings.ALI_PRI_KEY_PATH,
        alipay_public_key_path=settings.ALI_PUB_KEY_PATH
    )

    if request.method == 'GET':
        # 只做跳转，判断是否支付成功了，不做订单的状态更新。
        # 支付吧会讲订单号返回：获取订单ID，然后根据订单ID做状态更新 + 认证。
        # 支付宝公钥对支付给我返回的数据request.GET 进行检查，通过则表示这是支付宝返还的接口。
        params = request.GET.dict()
        sign = params.pop('sign', None)
        status = ali_pay.verify(params, sign)

        if status:
            current_datetime = datetime.datetime.now()
            out_trade_no = params['out_trade_no']
            _object = models.Transation.objects.filter(order=out_trade_no).first()
            _object.status = 1
            _object.start_time = current_datetime
            _object.end_time = current_datetime + datetime.timedelta(days=365 * _object.count)
            _object.save()
            messages.success(request,'支付完成')
            return redirect('index')
        return HttpResponse('支付失败')
    else:
        from urllib.parse import parse_qs
        body_str = request.body.decode('utf-8')
        post_data = parse_qs(body_str)
        post_dict = {}
        for k, v in post_data.items():
            post_dict[k] = v[0]

        sign = post_dict.pop('sign', None)
        status = ali_pay.verify(post_dict, sign)
        if status:
            #数据库交易信息更新
            current_datetime = datetime.datetime.now()
            out_trade_no = post_dict['out_trade_no']
            _object = models.Transation.objects.filter(order=out_trade_no).first()
            _object.status = 1
            _object.start_datetime = current_datetime
            _object.end_datetime = current_datetime + datetime.timedelta(days=365 * _object.count)
            _object.save()
            return HttpResponse('success')
        return HttpResponse('error')
