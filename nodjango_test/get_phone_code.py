import redis
import datetime
# 直接连接redis
conn = redis.Redis(host='106.55.134.35', port=6379, password='jjb000522', encoding='utf-8')
#conn = redis.Redis(host='127.0.0.1', port=6379,password='jjb000522', encoding='utf-8')
# 设置键值：******="123456" 且超时时间为60*30秒（值写入到redis时会自动转字符串）
conn.set('code', 123456, ex=60*30)       #123456为验证码
# 根据键获取值：如果存在获取值（获取到的是字节类型）；不存在则返回None
value = conn.get('code')
print(value)
