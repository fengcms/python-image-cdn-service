#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os, sys
import shutil
import hashlib
import json
from PIL import Image, ImageDraw, ImageFont, ImageOps
import imageio
from io import BytesIO
from core.tool import ok, fail, bytes2hex, getSuffix, isDictStr, isNum,\
        checkSuffix, hasFile, isColor, findTtfPath
from core.gif import hackGif
from config import STATIC_DIR

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
    mParam = {'type': mType, 'location': ['right', 'bottom']}

    # 如果参数中包含水印位置参数，则重设水印位置参数
    if 'location' in mark:
        mLoca = mark['location']
        if not isinstance(mLoca, list):
            return fail('mark location must be array', 412)
        if len(mLoca) != 2:
            return fail('mark location array length must be 2', 412)
        if not mLoca[0] in ['left', 'right', 'center']:
            return fail('mark location[0] value must in "left", "right", "center"', 412)
        if not mLoca[1] in ['top', 'bottom', 'center']:
            return fail('mark location[1] value must in "top", "bottom", "center"', 412)
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

# 制作文字水印图片
def makeTextImg(param):
    # 利用 getbox 方法计算出文字水印所需要的尺寸大小
    def calcImgWidth(param, text):
        im = Image.new('RGB', (1000, param['size'] + 10), (0, 0, 0))
        imDraw = ImageDraw.Draw(im)
        imFont = ImageFont.truetype(param['ttf'], param['size'])
        imDraw.text((5, 5), text, fill="#FFFFFF", font=imFont)
        return im.getbbox()[2] + 5

    # 处理文字，防止中文乱码
    text = u'{0}'.format(param['text'])
    mW = calcImgWidth(param, text)
    mH = param['size'] + 10
    blank = Image.new('RGBA', (mW, mH), (255, 255, 255, 0))
    draw = ImageDraw.Draw(blank)
    font = ImageFont.truetype(param['ttf'], param['size'])
    draw.text((5, 5), text, fill=param['color'], font=font)
    return blank

# 叠加水印函数
def addMark(sImg, mark, mW, mH, mLocaX, mLocaY):
    sW, sH = sImg.size
    if sW >= (mW + 20) and sH >= (mH + 20):
        layer = Image.new('RGBA', sImg.size, (0,0,0,0))
        mX = 10
        mY = 10
        if mLocaX == 'center':
            mX = int((sW - mW) / 2)
        if mLocaX == 'right':
            mX = sW - mW - 10
        if mLocaY == 'center':
            mY = int((sH - mH) / 2)
        if mLocaY == 'bottom':
            mY = sH - mH - 10
        layer.paste(mark, (mX, mY))
        oImg = Image.composite(layer, sImg, layer)
        return oImg
    else:
        return sImg

# 添加水印参数
def makeMark(sImg, mParam):
    mType = mParam['type']
    mLocaX = mParam['location'][0]
    mLocaY = mParam['location'][1]
    if mType == 'img':
        mW = mParam['imgSize'][0]
        mH = mParam['imgSize'][1]
        mark = Image.open(mParam['imgPath']).resize((mW, mH), Image.ANTIALIAS)
        return addMark(sImg, mark, mW, mH, mLocaX, mLocaY)
    else:
        mark = makeTextImg(mParam)
        mW, mH = mark.size
        return addMark(sImg, mark, mW, mH, mLocaX, mLocaY)

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
            oImg = sImg
            # 处理缩放图片
            if 'zoom' in params:
                zoom = params['zoom']
                if not isNum(zoom):
                    return fail('zoom value must be Positive integer', 412)
                # 如果原图尺寸小于缩放尺寸，则直接保存
                if sw <= zoom and sh <= zoom:
                    saveImage(savePath, image)
                else:
                    oImg = zoomImg(sImg, sw, sh, zoom)
            # 处理水印参数
            mParam = calcMarkParams(params)
            if not isinstance(mParam, dict) and mParam != False:
                return mParam
            if isinstance(mParam, dict):
                oImg = makeMark(oImg, mParam)
            # 保存图片
            oImg.save(savePath, checkSuffix(imageSuffix))
            oImg.close()

        # 处理 gif 图片
        else:
            oImg = sImg
            # 将 gif 拆解为一组照片
            tempGIf = hackGif(sImg, savePath)
            tempImgPath = tempGIf[0]
            tempDirPath = tempGIf[1]
            gifDur = tempGIf[2] / 1000
            tempImg = []
            # 压缩每一张照片
            for i in tempImgPath:
                tmp = Image.open(i)
                if 'zoom' in params:
                    zoom = params['zoom']
                    if not isNum(zoom):
                        return fail('zoom value must be Positive integer', 412)
                    # 如果原图尺寸小于缩放尺寸，则直接保存
                    if sw > zoom and sh > zoom:
                        tmp = zoomImg(tmp, sw, sh, zoom)
                # 处理水印参数
                mParam = calcMarkParams(params)
                if not isinstance(mParam, dict) and mParam != False:
                    return mParam
                if isinstance(mParam, dict):
                    tmp = makeMark(tmp, mParam)
                tmp.save(i, 'PNG')
                tempImg.append(imageio.imread(i))
            # 将拆解出来的图片重新组装为gif图片
            imageio.mimsave(savePath, tempImg, 'GIF', duration = gifDur)
            # 删除临时文件夹
            # shutil.rmtree(tempDirPath)
            # saveImage(savePath, image)

    else:
        saveImage(savePath, image)

    # 给客户端返回结果
    return ok({"path": resPath})

