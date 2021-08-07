# -*- coding=utf-8
# appid 已在配置中移除,请在参数 Bucket 中带上 appid。Bucket 由 BucketName-APPID 组成
# 1. 设置用户配置, 包括 secretId，secretKey 以及 Region
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import logging

# 日志打印
# logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# 关键参数
secret_id = 'AKIDXqgJp5zyaMs7GFtb1A3f6JGdy4zdELuJ'  # 替换为用户的 secretId
secret_key = 'BCxS8YnwwEH4aqUtbAVgbGepscDvNZUG'  # 替换为用户的 secretKey
region = 'ap-guangzhou'  # 替换为用户的 Region

# 代理
# proxies = {
#    'http': '127.0.0.1:80', # 替换为用户的 HTTP代理地址
#    'https': '127.0.0.1:443' # 替换为用户的 HTTPS代理地址
# }

# endpoint = 'cos.accelerate.myqcloud.com' # 替换为用户的 endpoint

# 默认参数
token = None  # 使用临时密钥需要传入 Token，默认为空，可不填
scheme = 'https'  # 指定使用 http/https 协议来访问 COS，默认为 https，可不填

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
# 2. 获取客户端对象
client = CosS3Client(config)

# 上传文件
response = client.upload_file(
    # 设置参数
   Bucket='sass-1305557388',
   LocalFilePath='01.gif',
   Key='01.gif',

   # 默认参数
   PartSize=1,
   MAXThread=10,
   EnableMD5=False
)

print(response['ETag'])


