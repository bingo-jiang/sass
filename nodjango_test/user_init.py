import django
import os
import sys

# 创建与Django相匹配的环境
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'sass_project.settings')
django.setup()
# 正式操作
from web import models  # 操作所用库，不能放到上面的环境库中
import uuid
import datetime


def run():
    user_info_obj = models.Userinfo.objects.filter(id=1).first()
    policy_obj = models.PricePolicy.objects.filter(category=2, title='收费版', price=299).first()
    user_id = 2
    models.Transation.objects.create(
        status=2,
        order=str(uuid.uuid4()),
        user=user_info_obj,
        project_policy=policy_obj,
        count=0,
        price=0,
        start_time=datetime.datetime.now(),
    )
    user_obj = models.Userinfo.objects.filter(id=user_id).first()
    exisis = models.Transation.objects.filter(user=user_obj).last()
    print(exisis.id)


def init_user_project():
    issues_type_obj_list = []
    instance = models.Project.objects.filter(id=4).first()
    for item in models.IssuesType.PROJECT_INIT_LIST:
        issues_type_obj_list.append(models.IssuesType(project=instance, title=item))
    models.IssuesType.objects.bulk_create(issues_type_obj_list)  # 批量增加数据


if __name__ == '__main__':
    init_user_project()
