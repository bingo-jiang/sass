import random
from PIL import Image, ImageFont, ImageDraw, ImageFilter


# def check_code(width=120, height=30, char_length=4, font_file='./scripts/font_file/Monaco.ttf', font_size=32):
#     code = []
#     img = Image.new(mode='RGB', size=(width, height), color=(255, 255, 255))
#     draw = ImageDraw.Draw(img, mode='RGB')
#
#     def rndChar():
#         """
#         生成随机字母
#         :return:
#         """
#         return chr(random.randint(65, 90))
#
#     def rndColor():
#         """
#         生成随机颜色
#         :return:
#         """
#         # return (random.randint(0, 255), random.randint(10, 255), random.randint(64, 255))
#         return ('#00CCFF')
#
#     def rndColor1():
#         return ('#00FFFF')
#
#     # 写文字
#     font = ImageFont.truetype(font_file, font_size)
#     for i in range(char_length):
#         char = rndChar()
#         code.append(char)
#         h = random.randint(0, 4)
#         draw.text([i * width / char_length, h], char, font=font, fill=rndColor())
#
#     # 写干扰点
#     for i in range(40):
#         draw.point([random.randint(0, width), random.randint(0, height)], fill=rndColor())
#
#     # 写干扰圆圈
#     for i in range(40):
#         draw.point([random.randint(0, width), random.randint(0, height)], fill=rndColor())
#         x = random.randint(0, width)
#         y = random.randint(0, height)
#         draw.arc((x, y, x + 4, y + 4), 0, 90, fill=rndColor1())
#
#     # 画干扰线
#     for i in range(0,10):
#         x1 = random.randint(0, width)
#         y1 = random.randint(0, height)
#         x2 = random.randint(0, width)
#         y2 = random.randint(0, height)
#         # draw.line((x1, y1), fill=rndColor())
#         draw.line((x1, y1, x2, y2), fill=rndColor1())
#
#     img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
#     return img, ''.join(code)

def check_code(width=120, height=34, char_length=4,font_file='./scripts/font_file/Monaco.ttf',font_size=36):
    def random_char():
        """
        生成随机字符
        """
        random_upper = chr(random.randint(65, 90))
        random_lower = chr(random.randint(97, 122))
        random_int = str(random.randint(0, 9))
        char_chose = random.choice([random_upper, random_lower, random_int])
        return char_chose

    def random_color0():
        """
        生成随机颜色
        :return:
        """
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        # return ('#00CCFF')

    def random_color1():
        return ('#00FFFF')

    code = []
    img = Image.new(mode='RGB', size=(width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img, mode='RGB')
    # 写文字
    font = ImageFont.truetype(font=font_file,size=font_size)
    for i in range(char_length):
        char = random_char()
        code.append(char)
        h = random.randint(0, 4)
        draw.text([i * width / char_length, h], char, font=font, fill=random_color0())

    # 写干扰点
    for i in range(40):
        draw.point([random.randint(0, width), random.randint(0, height)], fill=random_color0())

    # 写干扰圆圈
    for i in range(40):
        draw.point([random.randint(0, width), random.randint(0, height)], fill=random_color0())
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.arc((x, y, x + 4, y + 4), 0, 90, fill=random_color1())

    # 画干扰线
    for i in range(0, 10):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        # draw.line((x1, y1), fill=random_color1())
        draw.line((x1, y1, x2, y2), fill=random_color1())

    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    return img, ''.join(code)


if __name__ == '__main__':
    # 1. 直接打开
    #     img,code = check_code()
    #     img.show()
    #
    #     # 2. 写入文件
    img, code = check_code()
    with open('../web/static/imgs/code.png', 'wb') as f:
        img.save(f, format='png')

    #     # 3. 写入内存(Python3)
    #     # from io import BytesIO
    #     # stream = BytesIO()
    #     # img.save(stream, 'png')
    #     # stream.getvalue()
    #
    #     # 4. 写入内存（Python2）
    #     # import StringIO
    #     # stream = StringIO.StringIO()
    #     # img.save(stream, 'png')
    #     # stream.getvalue()
