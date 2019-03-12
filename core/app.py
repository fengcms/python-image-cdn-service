import os
from sanic import Sanic
from sanic.response import file, text
from sanic.exceptions import NotFound
from config import STATIC_DIR
from core.tool import hasFile, isImgName, checkThumbParams, return404
from core.thumb import markThumb

app = Sanic(__name__)

@app.middleware('request')
async def CheckRequest(request):
    way = list(filter(None, request.path.split('/')))[0]
    
    ways = ['proto', 'thumb']
    # 检查请求方法
    if request.method != 'GET' and way in ways:
        return text('', status=405)

@app.route("/upload")
async def upload(request):
    return text('x')

@app.route("/proto/<name>")
async def Proto(request, name):

    imgPath = STATIC_DIR + '/' + name[0:2] + '/' + name[2:]

    if not isImgName(name) or not hasFile(imgPath):
        return await return404()

    return await file(imgPath)

@app.route("/thumb/<params>/<name>")
async def Thumb(request, params, name):
    # 检查缩略图参数
    if not checkThumbParams(params):
        return text('', status=400)

    # 检查原图是否存在
    imgPath = STATIC_DIR + '/' + name[0:2] + '/' + name[2:]
    if not isImgName(name) or not hasFile(imgPath):
        return await return404()

    # 组织缩略图路径
    tmp = name.split('.')
    thumbPath = STATIC_DIR + '/' + name[0:2] + '/' + \
            tmp[0][2:] + '-' + params + '.' + tmp[1]

    # 缩略图存在则直接返回
    if hasFile(thumbPath):
        return await file(thumbPath)
    # 缩略图不存在则生成缩略图并返回
    else:
        return await markThumb(tmp[1], imgPath, thumbPath, params)


    return text('ok')





@app.exception(NotFound)
async def ignore_404s(request, exception):
    return text('403', status=403)

