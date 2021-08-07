from django import forms
from web import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from scripts.tencent.sms import send_sms_single
import random
from django_redis import get_redis_connection
from scripts import encrypt


# 基类
class BoostrapForm(object):
    boostrap_exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in self.boostrap_exclude:
                continue
            old_class = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = 'form-control {}'.format(old_class)
            field.widget.attrs['placeholder'] = '请输入%s' % (field.label,)
            field.widget.attrs['autocomplete'] = "off"


# 注册
class RegisterModelForm(BoostrapForm, forms.ModelForm):
    mobile_phone = forms.CharField(label='手机号', validators=[RegexValidator(r"^1\d{10}$", '手机号格式错误')])
    emai = forms.CharField(label='邮箱', required=False)
    password = forms.CharField(label='密码', max_length=32, widget=forms.PasswordInput)
    confirm_pwd = forms.CharField(label='确认密码', max_length=32, widget=forms.PasswordInput)
    code = forms.CharField(label='验证码', widget=forms.TextInput)

    class Meta:
        model = models.Userinfo
        fields = ['username', 'emai', 'password', 'confirm_pwd', 'mobile_phone', 'code']

    # def __init__(self,*args,**kwargs):
    #     super().__init__(*args,**kwargs)
    #     for name,field in self.fields.items():
    #         field.widget.attrs['class']='form-control'
    #         field.widget.attrs['placeholder'] = '请输入%s'%(field.label,)
    def clean_username(self):
        username = self.cleaned_data.get('username')
        exits = models.Userinfo.objects.filter(username=username).exists()
        if exits:
            raise ValidationError('用户名已存在')
        return username

    def clean_emai(self):
        emai = self.cleaned_data.get('emai')
        exits = models.Userinfo.objects.filter(username=emai).exists()
        if exits:
            raise ValidationError('邮箱已绑定或注册账号')
        return emai

    def clean_password(self):
        password = self.cleaned_data.get('password')
        # 加密
        password = encrypt.data_encryption(password)
        return password

    def clean_confirm_pwd(self):
        password = self.cleaned_data.get('password')
        confirm_pwd = self.cleaned_data.get('confirm_pwd')
        confirm_pwd = encrypt.data_encryption(confirm_pwd)
        if password != confirm_pwd:
            raise ValidationError('两次密码输入不一致')
        return confirm_pwd

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data.get('mobile_phone')
        exits = models.Userinfo.objects.filter(mobile_phone=mobile_phone).exists()
        if exits:
            raise ValidationError('手机号已绑定或注册账号')
        return mobile_phone

    def clean_code(self):
        code = self.cleaned_data['code']
        mobile_phone = self.cleaned_data.get('mobile_phone')
        conn = get_redis_connection()
        redis_code = conn.get(mobile_phone)
        if not redis_code:
            raise ValidationError('验证码已失效或未发送，请重新获取验证码')

        else:
            redis_str_code = redis_code.decode()
            if code.strip() != redis_str_code:
                raise ValidationError('验证码错误，请重新输入')
            return code


# 发送短信验证码
class SendSmsForm(forms.Form):
    mobile_phone = forms.CharField(label='手机号', validators=[RegexValidator(r"^1\d{10}$", '手机号格式错误')])

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data.get('mobile_phone')
        # mobile_phone = self.request.GET.get('mobile_phone')
        tql = self.request.GET.get('tql')
        template_id = settings.TENCENT_SMS_TEMPLATES.get(tql)
        exits = models.Userinfo.objects.filter(mobile_phone=mobile_phone).exists()
        if not template_id:
            raise ValidationError('短信模板ID错误')
        if tql == 'login':
            if not exits:
                raise ValidationError('手机号不存在')
        else:
            if exits:
                raise ValidationError('手机号已存在')
        # 发短信，存入Redis
        code = random.randrange(100000, 999999)
        sms_result = send_sms_single(mobile_phone, template_id, [code, ])
        # print(sms_result)
        # return sms_result
        if sms_result['result'] != 0:
            raise ValidationError("短信发送失败，{}".format(sms_result['errmsg']))
        else:
            # redis
            conn = get_redis_connection()
            conn.set(mobile_phone, code, ex=60 * 60)
            return mobile_phone


# 短信登录
class LoginSmsForm(BoostrapForm, forms.Form):
    mobile_phone = forms.CharField(label='手机号', validators=[RegexValidator(r"^1\d{10}$", '手机号格式错误')])
    code = forms.CharField(label='验证码', widget=forms.TextInput)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     for name, field in self.fields.items():
    #         field.widget.attrs['class'] = 'form-control'
    #         field.widget.attrs['placeholder'] = '请输入%s' % (field.label,)

    # 数据校验
    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data.get('mobile_phone')
        db_obj = models.Userinfo.objects.filter(mobile_phone=mobile_phone).exists()
        if not db_obj:
            raise ValidationError('手机号不存在')
        return mobile_phone

    def clean_code(self):
        mobile_phone = self.cleaned_data.get('mobile_phone')
        code = self.cleaned_data['code']
        # 手机号不存在，无需判断
        if not mobile_phone:
            return code
        else:
            conn = get_redis_connection()
            redis_code = conn.get(mobile_phone)
            if not redis_code:
                raise ValidationError('验证码已失效或未发送，请重新获取验证码')

            else:
                redis_str_code = redis_code.decode()
                if code.strip() != redis_str_code:
                    raise ValidationError('验证码错误，请重新输入')
                return code


class LoginForm(BoostrapForm, forms.Form):
    username = forms.CharField(label='手机/邮箱/用户名', max_length=32)
    password = forms.CharField(label='密码', max_length=32, widget=forms.PasswordInput(render_value=True))
    code = forms.CharField(label='验证码', max_length=32)

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_code(self):
        code = self.cleaned_data.get('code')
        session_code = self.request.session.get('sass_img_code')
        print(code,session_code)
        if not session_code:
            raise ValidationError('验证码已过期，请重新获取')
        if code.strip().upper() != session_code.strip().upper():
            raise ValidationError('验证码错误，请重新输入')
        return code

    def clean_password(self):
        password = self.cleaned_data.get('password')
        # 加密
        password = encrypt.data_encryption(password)
        return password


class UserModelForm(BoostrapForm, forms.ModelForm):
    birday = forms.DateField(label='出生年月', widget=forms.DateInput())

    class Meta:
        model = models.Userinfo
        fields = ['nickname', 'username', 'mobile_phone', 'birday', 'sex', 'emai', 'adress']
        exclude = ['header_img', 'password', 'register_time']


class PwdAlterModelForm(BoostrapForm, forms.ModelForm):
    old_pwd = forms.CharField(label='旧密码', max_length=32, widget=forms.PasswordInput)
    password = forms.CharField(label='新密码', max_length=32, widget=forms.PasswordInput)
    confirm_pwd = forms.CharField(label='确认新密码', max_length=32, widget=forms.PasswordInput)

    class Meta:
        model = models.Userinfo
        fields = ['old_pwd', 'password', 'confirm_pwd']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_old_pwd(self):
        old_pwd=self.cleaned_data.get('old_pwd')
        if not old_pwd:
            raise ValidationError('输入不能为空')
        old_pwd = encrypt.data_encryption(old_pwd)
        real_old_pwd=self.request.current.user.password
        if old_pwd!=real_old_pwd:
            raise ValidationError('密码输入错误')
        return old_pwd

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise ValidationError('输入不能为空')
        # 加密
        password = encrypt.data_encryption(password)
        return password

    def clean_confirm_pwd(self):
        password = self.cleaned_data.get('password')
        confirm_pwd = self.cleaned_data.get('confirm_pwd')
        if not confirm_pwd:
            raise ValidationError('输入不能为空')
        confirm_pwd = encrypt.data_encryption(confirm_pwd)
        if password != confirm_pwd:
            raise ValidationError('两次密码输入不一致')
        return confirm_pwd
