"""sass_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
import os
from django.views.static import serve
from web.views import account, homepage, tools, project, user
from web.views.project_manage import wiki, file, issues, settings, statistic, dashborde
from django import conf

urlpatterns = [
    # 账号相关
    url(r'^admin/', admin.site.urls),
    url(r'^test/', tools.test, name='test'),
    url(r'^login/pwd/', account.login, name='login'),
    url(r'^logout/', account.logout, name='logout'),
    url(r'^login/sms/', account.login_sms, name='login_sms'),
    url(r'^register/', account.register, name='register'),
    url(r'^send/sms/', account.send_sms, name='send_sms'),
    url(r'^img_code/', tools.img_code, name='img_code'),
    url(r'^index/', homepage.index, name='index'),
    url(r'^user/center/', user.user_center, name='user_center'),
    url(r'^user/editor/', user.user_editor, name='user_editor'),
    url(r'^user/pwd/alter/$', user.user_alter_pwd, name='user_alter_pwd'),
    url(r'^price/', homepage.price, name='price'),
    url(r'^payment/(?P<policy_id>\d+)/', homepage.payment, name='payment'),
    url(r'^pay/$', homepage.pay, name='pay'),
    url(r'^pay/notify/$', homepage.pay_notify, name='pay_notify'),
    url(r'^favicon.ico$', serve, {'path': 'imgs/favicon.ico','document_root': os.path.join(conf.settings.BASE_DIR, "web/static")}),

    # 项目列表
    url(r'^project/list/', project.project_list, name='project_list'),
    # url(r'^project/manage/(?P<project_id>\d+)/issues/detail/(?P<issues_id>\d+)/$', issues.issues_detail, name='issues_detail'),
    # 项目管理
    url(r'^project/manage/(?P<project_id>\d+)/', include([
        url(r'^dashborde/$', dashborde.dashborde, name='dashborde'),
        url(r'^dashborde/issues/chart/$', dashborde.dashborde_chart, name='dashborde_chart'),
        # 问题操作
        url(r'^issues/$', issues.issues, name='issues'),
        url(r'^issues/delete/$', issues.issues_delete, name='issues_delete'),
        url(r'^issues/detail/(?P<issues_id>\d+)/$', issues.issues_detail, name='issues_detail'),
        url(r'^issues/record/(?P<issues_id>\d+)/$', issues.issues_record, name='issues_record'),
        url(r'^issues/change/(?P<issues_id>\d+)/$', issues.issues_change, name='issues_change'),
        url(r'^issues/invite/$', issues.invite, name='invite'),

        # 统计
        url(r'^statistic/$', statistic.statistic, name='statistic'),
        url(r'^statistic/priority/$', statistic.statistic_priority, name='statistic_priority'),
        url(r'^statistic/progress/$', statistic.statistic_project_progress, name='statistic_project_progress'),
        # 文件操作
        url(r'^file/home/', file.file_home, name='file_home'),
        url(r'^file/delete/', file.file_delete, name='file_delete'),
        url(r'^file/write/', file.file_to_db, name='file_to_db'),
        url(r'^file/download/(?P<file_id>\d+)/', file.file_download, name='file_download'),
        url(r'^test/', file.test, name='test'),  # 测试专用
        # wiki操作
        url(r'^wiki/index/', wiki.wiki_index, name='wiki_index'),
        url(r'^wiki/add/', wiki.wiki_add, name='wiki_add'),
        url(r'^wiki/catalog/', wiki.wiki_catalog, name='wiki_catalog'),
        url(r'^wiki/delete/(?P<textId>\d+)/', wiki.wiki_delete, name='wiki_delete'),
        url(r'^wiki/edit/(?P<textId>\d+)/', wiki.wiki_edit, name='wiki_edit'),
        url(r'^wiki/img/upload/', wiki.wiki_img_upload, name='wiki_img_upload'),
        # settings处理
        url(r'^settings/$', settings.settings, name='settings'),
        url(r'^settings/delete/', settings.settings_delete, name='settings_delete'),
        url(r'^settings/module/$', settings.module, name='module'),
        url(r'^settings/module/add/$', settings.add_module, name='add_module'),
        url(r'^settings/module/delete/$', settings.delete_module, name='delete_module'),
        url(r'^settings/member/$', settings.member, name='member'),
        url(r'^settings/member/delete/$', settings.member_delete, name='member_delete'),
        url(r'^settings/invite_code/$', settings.invite_code, name='invite_code'),
        url(r'^settings/invite_code/delete/$', settings.invite_code_delete, name='invite_code_delete'),
        # cos临时凭证处理
        url(r'^cos/credential/', file.cos_credential, name='cos_credential'),
    ])),
    # 成员加入
    url(r'^issues/invite/join/(?P<code>\w+)/$', issues.invite_join, name='invite_join'),
    # 项目标记
    url(r'^project/star/(?P<project_type>\w+)/(?P<project_id>\d+)/', project.project_star, name='project_star'),
    url(r'^project/unstar/(?P<project_type>\w+)/(?P<project_id>\d+)/', project.project_unstar,
        name='project_unstar'),
]
