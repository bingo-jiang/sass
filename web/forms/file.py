from django import forms
from web import models
from django.core.exceptions import ValidationError
from web.forms.accountforms import BoostrapForm
from scripts.tencent import cos
from qcloud_cos.cos_exception import CosClientError

class FileModelForm(BoostrapForm,forms.ModelForm):
    class Meta:
        model=models.File
        fields = ['filename']
        exclude=[]

    def __init__(self,request,parent_obj,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request=request
        self.parent_obj=parent_obj

    def clean_filename(self):
        filename=self.cleaned_data.get('filename')

        file_obj=models.File.objects.filter(type=2,filename=filename,project=self.request.current.project)
        # 根目录下是否同名
        if not self.parent_obj:
            exists=file_obj.filter(parent__isnull=True).exists()
        # 同一父目录下是否同名
        else:
            exists = file_obj.filter(parent=self.parent_obj).exists()
        if exists:
            raise ValidationError('文件夹已存在')
        return filename

class CosFileModelForm(BoostrapForm,forms.ModelForm):
    etag=forms.CharField(label='ETag')
    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request=request

    class Meta:
        model=models.File
        exclude=['project','type','update_user','update_time']

    def clean_file_path(self):
        file_path=self.cleaned_data.get('file_path')
        return "https://{}".format(file_path)

    # def clean_parent(self):
    #     parent_id = self.cleaned_data.get('parent_id')
    #     print("parent_id:",parent_id)
    #     project = self.request.current.project
    #     update_user = self.request.current.user
    #     parent_obj=models.File.objects.filter(id=parent_id,project=project,update_user=update_user).first()
    #     return parent_obj


    def clean(self):
        etag=self.cleaned_data.get('etag')
        key=self.cleaned_data.get('key')
        if not etag or key:
            return self.cleaned_data
        else:
            #向cos校验etaghe key
            try:
                res=cos.check_file(self.request.current.project.bucket,self.request.current.project.region,key)
            except CosClientError as e:
                self.add_error(key,'文件不存在')
                return self.cleaned_data
            cos_etag=res.get('ETag')
            if etag!=cos_etag:
                self.add_error(etag,'etag校验失败')

            return self.cleaned_data


