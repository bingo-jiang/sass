import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 基础配置
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_TZ = False  # 影响数据库自动生成的时间字段。True:用UTC时间格式；False:根据TIME_ZONE设置时间格式
DEBUG = True

# 腾讯云相关配置
TENCENT_SMS_APP_ID = 1400505612
TENCENT_SMS_APP_KEY = 'a70aa149199a16f92933446c32d1c08c'
TENCENT_SMS_SIGN = 'Python菜鸟入门'
TENCENT_SMS_TEMPLATES = {
    'login': 920365,
    'register': 920350,
    'reset': 920369,
}
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",  # 安装redis的主机的 IP 和 端口
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 1000,
                "encoding": 'utf-8'
            },
            "PASSWORD": "jjb000522"  # redis密码
        }
    }
}
# 腾讯对象存储
TENCENT_COS_ID = 'AKIDXqgJp5zyaMs7GFtb1A3f6JGdy4zdELuJ'
TENCENT_COS_KEY = 'BCxS8YnwwEH4aqUtbAVgbGepscDvNZUG'
# 支付宝配置
ALI_APP_ID = '2021000117649639'
ALI_GATEWAY = 'https://openapi.alipaydev.com/gateway.do'
ALI_PRI_KEY_PATH = os.path.join(BASE_DIR, 'web/Secret_key/PUBLIC_RSA2_PKCS1.txt')
ALI_PUB_KEY_PATH = os.path.join(BASE_DIR, 'web/Secret_key/Alia_Public.txt')
ALI_NOTIFY_URL = 'http://127.0.0.1:8848/pay/notify/'
ALI_RETURN_URL = 'http://127.0.0.1:8848/pay/notify/'
