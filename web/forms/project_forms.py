from django import forms
from web import models
from django.core.exceptions import ValidationError
from web.forms import selfwidgets
from web.forms.accountforms import BoostrapForm

class ProjectForm(BoostrapForm,forms.ModelForm):
    boostrap_exclude=["color"]
    name=forms.CharField(label='项目名称',widget=forms.TextInput(attrs={'autocomplete':'off'}))
    # color = forms.CharField(label='颜色', widget=forms.Select())
    desc=forms.CharField(label='项目描述',widget=forms.Textarea(),required=False)
    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request=request

    class Meta:
        model=models.Project
        fields=['name','color','desc']
        widgets={
            'color':selfwidgets.ColorRadioSelect(attrs={'class':'color-radio'})
        }

    def clean_name(self):
        name=self.cleaned_data.get('name')
        # 1.判断当前用户是否已经创建过此项目
        obj=models.Project.objects.filter(name=name,creator=self.request.current.user).first()
        if obj:
            raise ValidationError('项目名已存在')
        # 2.判断当前用户的额度是否已经用完
        project_num=self.request.current.price_policy.project_num#额度
        project_count=models.Project.objects.filter(creator=self.request.current.user).count()
        if project_count>=project_num:
            raise ValidationError('项目额度已用完，请升级权限或删除已有项目')
        else:
            return name

