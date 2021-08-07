'''文件说明：非运行时脚本，即不启动Django也能操作数据库等'''
# 环境需要的库
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


def run():
    models.PricePolicy.objects.create(
        category=2,
        title='SSVIP',
        price=999,
        project_num=999,
        project_member=999,
        project_space=9999,
        per_file_size=1024*99,
    )

if __name__ == '__main__':
    run()
