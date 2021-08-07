from scripts.pic_code import check_code
from django.shortcuts import HttpResponse
from django.http import JsonResponse
from io import BytesIO
import os
from django.conf import settings
def img_code(request):
    img, code = check_code()
    # print(code)
    # 设置session
    request.session['sass_img_code']=code
    request.session.set_expiry(300)
    # 存入内存中
    stream=BytesIO()
    img.save(stream,'png')
    res=stream.getvalue()
    #return HttpResponse(stream.getvalue())
    return HttpResponse(res,content_type="image/png")


def test(request):
    path=os.path.join(settings.BASE_DIR,'scripts/font_file')
    return HttpResponse(path)
