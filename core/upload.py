#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# from sanic.response import json, text, file
import os, sys
import hashlib
import json
from PIL import Image
from io import BytesIO
from core.tool import ok, fail, bytes2hex, getSuffix, isDictStr, isNum,\
        checkSuffix, hasFile, isColor, findTtfPath
from config import STATIC_DIR

# 检查缩小参数
def checkZoomParams(zoom):
    if not isNum(zoom):
        return fail('zoom value must be Positive integer', 412)

# 缩小处理函数
def zoomImg(sImg, sw, sh, zoom):
    ow = zoom
    oh = int(zoom * sh / sw)
    if sw < sh:
        ow = int(zoom * sw / sh)
        oh = zoom
    return sImg.resize((ow, oh), Image.ANTIALIAS)

# 处理水印参数
def calcMarkParams(params):
    if not 'mark' in params:
        return False
    # 确定是否包含水印参数以及水印的类型
    mark = params['mark']
    if not 'type' in mark:
        return fail('mark must has type field', 412)
    mType = mark['type']
    if not mark['type'] in ['img', 'text']:
        return fail('mark type must be "img" or "text"', 412)

    # 默认水印位置为图片右下角
    mParam = {'location': ['right', 'bottom']}

    # 如果参数中包含水印位置参数，则重设水印位置参数
    if 'location' in mark:
        mLoca = mark['location']
        if not isinstance(mLoca, list):
            return fail('mark location must be array', 412)
        if len(mLoca) != 2:
            return fail('mark location array length must be 2', 412)
        for i in mLoca:
            if not i in ['left', 'top', 'right', 'bottom', 'center']:
                return fail('mark location value must in "left", "top", "right", "bottom", "center"', 412)
        mParam['location'] = mLoca

    # 图片水印参数处理
    if mType == 'img':
        # 图片水印必须包含水印图片名称
        if not 'imgName' in mark:
            return fail('image mark must has "imgName" field', 412)
        # 根据水印图片名称组织水印图片路径并判断水印是否存在
        mImgName = mark['imgName']
        markPath = STATIC_DIR + '/' + mImgName[0:2] + '/' + mImgName[2:]
        if not hasFile(markPath):
            return fail('image mark was not found', 412)
        mParam['imgPath'] = markPath
        # 读取水印图片并获取其宽高设为默认水印大小
        mImg = Image.open(markPath)
        mW, mH = mImg.size
        mParam['imgSize'] = [mW, mH]
        # 若果包含水印大小参数则重设水印大小
        if 'imgSize' in mark:
            imgSize = mark['imgSize']
            if not isinstance(imgSize, list):
                return fail('mark imgSize must be array', 412)
            if len(imgSize) != 2:
                return fail('mark imgSize array length must be 2', 412)
            for i in imgSize:
                if not isNum(i):
                    return fail('mark imgSize array value must be Positive integer', 412)
            mParam['imgSize'] = imgSize
    # 文字水印参数处理
    if mType == 'text':
        # 文字水印必须包含文字信息
        if not 'text' in mark:
            return fail('Text mark must has text field', 412)
        mText = mark['text']
        if not isinstance(mText, str):
            return fail('Text mark text field must be String', 412)
        if len(mText) > 20:
            return fail('Text mark text field max length is 20', 412)
        mParam['text'] = mText
        # 处理颜色参数，默认为白色
        mParam['color'] = '#FFFFFF' 
        if 'color' in mark:
            if not isColor(mark['color']):
                return fail('mark color value must be a color String', 412)
            mParam['color'] = mark['color'] 
        # 处理文字大小参数，默认为20，最小值为18
        mParam['size'] = 20
        if 'size' in mark:
            mSize = mark['size']
            if not isNum(mark['size']):
                return fail('mark font size value must be Positive integer', 412)
            if mSize > 18:
                mParam['size'] = mSize
            else:
                mParam['size'] = 18
        # 处理文字字体参数
        if 'ttf' in mark:
            mTtf = mark['ttf']
            if not isinstance(mTtf, str):
                return fail('Text mark ttf field must be String', 412)
            mParam['ttf'] = findTtfPath(mTtf)
    return mParam

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

    # 如果文件夹不存在，就创建文件夹
    if not os.path.exists(saveDir):
        os.makedirs(saveDir)

    # 上传文件附带参数处理
    if 'data' in request.form and imageSuffix != 'svg':
        # 检查参数是否是 json 
        params_text = request.form['data'][0]
        if not isDictStr(params_text):
            return fail('form data must be Json String', 412)
        params = json.loads(params_text)
        
        # 读取原图信息
        sImg = Image.open(BytesIO(image))
        sw, sh = sImg.size

        # PNG 和 JPG 图片的处理
        if imageSuffix != 'gif':
            oImg = None
            # 处理缩放图片
            if 'zoom' in params:
                zoom = params['zoom']
                checkZoomParams(zoom)
                # 如果原图尺寸小于缩放尺寸，则直接保存
                if sw <= zoom and sh <= zoom:
                    saveImage(savePath, image)
                else:
                    oImg = zoomImg(sImg, sw, sh, zoom)
            # 处理水印参数
            mParam = calcMarkParams(params)
            print(mParam)


            # 保存图片
            oImg.save(savePath, checkSuffix(imageSuffix))
        else:
            saveImage(savePath, image)


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
        # saveImage(savePath, image)
    else:
        saveImage(savePath, image)

    # 给客户端返回结果
    return ok({"path": resPath})

