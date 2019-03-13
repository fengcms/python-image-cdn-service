#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# from sanic.response import json, text, file
import os, sys
import hashlib
from PIL import Image
from io import BytesIO
from core.tool import ok, fail, bytes2hex, getSuffix
from config import STATIC_DIR

# 存储图片文件函数
def saveImage(savePath, image):
    tempFile = open(savePath, 'wb')
    tempFile.write(image)
    tempFile.close()

# 上传文件接口
async def upimg(request):
    
    # 判断参数是否正确
    if not request.files and not request.files.get('file'):
        return fail('request args is error', 412)
    image = request.files.get('file').body

    # 判断文件是否支持
    imageSuffix = getSuffix(bytes2hex(image))
    if imageSuffix == 'error':
        return fail('image type is error', 415)
    
    # 组织图片存储路径
    m1 = hashlib.md5()
    m1.update(image)
    md5Name = m1.hexdigest()

    saveDir = STATIC_DIR + '/' + md5Name[0:2] + '/'
    savePath = saveDir + md5Name[2:] + '.' + imageSuffix
    resPath = md5Name + '.' + imageSuffix
    if imageSuffix == 'svg':
        resPath += '?sanitize=true'

    # 如果文件夹不存在，就创建文件夹
    if not os.path.exists(saveDir):
        os.makedirs(saveDir)

    # 水印功能回头开发，代码先行封闭
    # # 如果是 jpg 图片，则添加水印
    # if imageSuffix == 'jpg':
    #     bImg = BytesIO(image)
    #     img = Image.open(bImg)
    #     imgW, imgH = img.size

    #     if imgW >= 300 and imgH >= 100:
    #         mark = Image.open("mark.png")
    #         layer = Image.new('RGBA', img.size, (0,0,0,0))
    #         layer.paste(mark, (imgW - 180, imgH - 60))
    #         out = Image.composite(layer, img, layer)
    #         out.save(savePath, 'JPEG', quality = 100)
    #     else:
    #         saveImage(savePath, image)

    # # 否则直接将文件写入到硬盘
    # else:
    #     saveImage(savePath, image)

    saveImage(savePath, image)
    # 给客户端返回结果
    return ok({"path": resPath})

