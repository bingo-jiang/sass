import time


# 性能提升
# 1.及时使用break跳出不必要的循环
# 2.优化相关的变量,如i
def num_select():
    start = time.time()
    for i in range(2, 100000):
        flags = True
        for j in range(2, int(pow(i, 0.5))):
            if i % j == 0:
                flags = False
                break
        if flags:
            print(i)
    print('用时：', time.time() - start)
def store():
    a=123
    b=a
    a+=1
    print(a,b)

def string_just(num):
    if int(num) < 1000:
        num = str(num).rjust(4, "0")
    return "#{}".format(num)
if __name__ == '__main__':
    a=1
    l=['a','b',a]
    print(id(a))
    print(id(l),id(l[0]))
    a=12
    print(id(a))
    print(id(l),id(l[0]))