from django.db import models

# Create your models here.
from django.core.validators import RegexValidator


# 用户表
class Userinfo(models.Model):
    '''用户表'''
    alphanumeric = RegexValidator(r'^[a-zA-Z]{1}[0-9a-zA-Z]*$', '账号必须以字母开头，后由数字字母组成')
    sex_choice = {(0, '不填'), (1, '男'), (2, '女'), }
    # 各个字段
    header_img = models.CharField(verbose_name='头像', max_length=128, null=True, default='none')
    nickname = models.CharField(verbose_name='昵称', max_length=16, null=True)
    username = models.CharField(verbose_name='账号', max_length=32, db_index=True, validators=[alphanumeric])
    mobile_phone = models.CharField(verbose_name='手机号', max_length=16)
    sex = models.SmallIntegerField(verbose_name='性别', choices=sex_choice, default=0)
    birday = models.DateField(verbose_name="生日", null=True, blank=True)
    emai = models.EmailField(verbose_name='邮箱', max_length=32, db_index=True, null=True)
    adress = models.CharField(verbose_name='地址', max_length=512, blank=True, null=True)
    password = models.CharField(verbose_name='密码', max_length=32)
    register_time = models.DateTimeField(verbose_name='注册时间', auto_now_add=True)

    def __str__(self):
        return self.username


# 价格策略
class PricePolicy(models.Model):
    '''价格策略/收费策略'''
    category_choice = {
        (1, '免费版'), (2, '收费版'), (3, '其他'),
    }
    category = models.SmallIntegerField(verbose_name='收费类型', default=2, choices=category_choice)

    title = models.CharField(verbose_name='标题', max_length=32)
    price = models.CharField(verbose_name='价格', max_length=32)

    project_num = models.PositiveIntegerField(verbose_name='可创建项目数')
    project_member = models.PositiveIntegerField(verbose_name='项目成员数',help_text='包括项目创建者')
    project_space = models.PositiveIntegerField(verbose_name='单项目空间（G）', help_text='G')
    per_file_size = models.PositiveIntegerField(verbose_name='单文件上传大小（M）', help_text='M')

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)


# 交易记录
class Transation(models.Model):
    '''交易记录'''
    status_choice = {
        (0, '未支付'), (1, '已支付'),
    }
    status = models.SmallIntegerField(verbose_name='状态', choices=status_choice)

    order = models.CharField(verbose_name='订单号', unique=True, max_length=64)

    user = models.ForeignKey(verbose_name='用户', to='Userinfo')
    price_policy = models.ForeignKey(verbose_name='价格策略', to='PricePolicy')

    count = models.IntegerField(verbose_name='数量（年）', help_text='0表示无限期')
    price = models.IntegerField(verbose_name='实际支付价格')

    start_time = models.DateTimeField(null=True, verbose_name='开始时间', blank=True)
    end_time = models.DateTimeField(null=True, verbose_name='结束时间', blank=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)


# 项目
class Project(models.Model):
    '''项目'''
    color_choice = {
        (1, '#F70909'), (2, '#EEEE11'), (3, '#11EE11'), (4, '#113DEE'), (5, '#C211EE'), (6, '#11EEEE'), (7, '#96EE11'),
    }
    name = models.CharField(verbose_name='项目名', unique=True, max_length=64)

    color = models.SmallIntegerField(verbose_name='颜色', choices=color_choice, default=1)

    desc = models.CharField(verbose_name='项目描述', null=True, max_length=512, blank=True)

    use_space = models.BigIntegerField(verbose_name='项目已使用空间', default=0, help_text='单位（字节/b）')

    star = models.BooleanField(verbose_name='星标', default=False)

    join_count = models.SmallIntegerField(verbose_name='参与人数', default=1)
    creator = models.ForeignKey(verbose_name='项目创建者', to='Userinfo')

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    bucket = models.CharField(verbose_name='COS桶', max_length=128)
    region = models.CharField(verbose_name='COS桶区域', max_length=128)


# 项目参与者
class ProjectUser(models.Model):
    '''项目参与者'''
    user = models.ForeignKey(verbose_name='用户', to='Userinfo', related_name='user')
    project = models.ForeignKey(verbose_name='项目', to='Project')
    invitor = models.ForeignKey(verbose_name='邀请人', to='Userinfo', null=True, blank=True, related_name='invitor')

    star = models.BooleanField(verbose_name='星标', default=False)

    create_time = models.DateTimeField(verbose_name='加入时间', auto_now_add=True)


# wiki
class Wiki(models.Model):
    # 关联外表
    project = models.ForeignKey(verbose_name='项目', to='Project')

    title = models.CharField(verbose_name='项目', max_length=128)
    content = models.TextField(verbose_name='内容')
    # 自关联
    parent = models.ForeignKey(verbose_name='所属目录', to='Wiki', null=True, blank=True, related_name='children')
    rank = models.IntegerField(verbose_name='目录级别', default=1)

    def __str__(self):
        return self.title


# 文件信息
class File(models.Model):
    project = models.ForeignKey(verbose_name='项目', to='Project')

    filename = models.CharField(verbose_name='文件名', max_length=64, help_text='文件/文件夹名')
    type_choies = {(1, '文件'), (2, '文件夹')}
    type = models.SmallIntegerField(verbose_name='类型', choices=type_choies)
    key = models.CharField(max_length=128, verbose_name='cos存储关键字', null=True, blank=True)
    file_size = models.BigIntegerField(verbose_name='文件大小', null=True, blank=True, help_text='字节/b')
    file_path = models.CharField(verbose_name='路径', null=True, blank=True, max_length=512)

    parent = models.ForeignKey(verbose_name='上级目录', to='File', related_name='child', null=True, blank=True)
    update_user = models.ForeignKey(verbose_name='更新者', to='Userinfo')
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)


# 问题/疑难解答
class Issues(models.Model):
    """ 问题 """
    project = models.ForeignKey(verbose_name='项目', to='Project')
    issues_type = models.ForeignKey(verbose_name='问题类型', to='IssuesType')
    module = models.ForeignKey(verbose_name='模块', to='Module', null=True, blank=True)

    subject = models.CharField(verbose_name='主题', max_length=80)
    desc = models.TextField(verbose_name='问题描述')
    priority_choices = (
        ("danger", "高"),
        ("warning", "中"),
        ("success", "低"),
    )
    priority = models.CharField(verbose_name='优先级', max_length=12, choices=priority_choices, default='danger')

    # 新建、处理中、已解决、已忽略、待反馈、已关闭、重新打开
    status_choices = (
        (1, '新建'),
        (2, '处理中'),
        (3, '已解决'),
        (4, '已忽略'),
        (5, '待反馈'),
        (6, '已关闭'),
        (7, '重新打开'),
    )
    status = models.SmallIntegerField(verbose_name='状态', choices=status_choices, default=1)

    assign = models.ForeignKey(verbose_name='指派', to='Userinfo', related_name='task', null=True, blank=True)
    attention = models.ManyToManyField(verbose_name='关注者', to='Userinfo', related_name='observe', blank=True)

    start_date = models.DateField(verbose_name='开始时间', null=True, blank=True)
    end_date = models.DateField(verbose_name='结束时间', null=True, blank=True)
    mode_choices = (
        (1, '公开模式'),
        (2, '隐私模式'),
    )
    mode = models.SmallIntegerField(verbose_name='模式', choices=mode_choices, default=1)

    parent = models.ForeignKey(verbose_name='父问题', to='self', related_name='child', null=True, blank=True,
                               on_delete=models.SET_NULL)

    creator = models.ForeignKey(verbose_name='创建者', to='Userinfo', related_name='create_problems')

    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    latest_update_datetime = models.DateTimeField(verbose_name='最后更新时间', auto_now=True)

    def __str__(self):
        return self.subject


# 问题所属板块
class Module(models.Model):
    """ 模块（里程碑）"""
    project = models.ForeignKey(verbose_name='项目', to='Project')
    title = models.CharField(verbose_name='模块名称', max_length=32)

    def __str__(self):
        return self.title


# 问题类型
class IssuesType(models.Model):
    """ 问题类型 例如：任务、功能、Bug """

    PROJECT_INIT_LIST = ["任务", '功能', 'Bug']

    title = models.CharField(verbose_name='类型名称', max_length=32)
    project = models.ForeignKey(verbose_name='项目', to='Project')

    def __str__(self):
        return self.title


# 问题答复
class IssuesReply(models.Model):
    """ 问题回复"""

    reply_type_choices = (
        (1, '修改记录'),
        (2, '评论')
    )
    reply_type = models.IntegerField(verbose_name='类型', choices=reply_type_choices)

    issues = models.ForeignKey(verbose_name='问题', to='Issues')
    content = models.TextField(verbose_name='描述')
    creator = models.ForeignKey(verbose_name='创建者', to='Userinfo', related_name='create_reply')
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    reply = models.ForeignKey(verbose_name='评论', to='self', null=True, blank=True)

#成员邀请
class ProjectInvite(models.Model):
    """ 项目邀请码 """
    project = models.ForeignKey(verbose_name='项目', to='Project')
    code = models.CharField(verbose_name='邀请码', max_length=64, unique=True)
    count = models.PositiveIntegerField(verbose_name='限制数量', null=True, blank=True, help_text='空表示无数量限制')
    use_count = models.PositiveIntegerField(verbose_name='已邀请数量', default=0)
    period_choices = (
        (30, '30分钟'),
        (60, '1小时'),
        (300, '5小时'),
        (1440, '24小时'),
        (1440*7,'7天'),
    )
    period = models.IntegerField(verbose_name='有效期', choices=period_choices, default=1440)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    creator = models.ForeignKey(verbose_name='创建者', to='Userinfo', related_name='create_invite')