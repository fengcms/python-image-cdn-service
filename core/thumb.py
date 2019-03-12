# import os
# import re

from PIL import Image
from sanic.response import file

def fillJpg(imgPath, thumbPath, width, height):
    image = Image.open(imgPath)
    thumb = image.resize((width, height), Image.ANTIALIAS)
    thumb.save(thumbPath, 'jpeg')

def clipJpg(imgPath, thumbPath, ow, oh):
    image = Image.open(imgPath)
    sw, sh = image.size
    # 长条图的裁剪
    if sw/ow < sh/oh:
        th = int(ow/sw*sh)
        tmpImg = image.resize((ow, th), Image.ANTIALIAS)
        cy = int((th - oh)/2)
        outImg = tmpImg.crop((0, cy, ow, cy+oh))
    # 宽条图的裁剪
    else:
        tw = int(oh/sh*sw)
        tmpImg = image.resize((tw, oh), Image.ANTIALIAS)
        cx = int((tw - ow)/2)
        outImg = tmpImg.crop((cx, 0, cx+ow, oh))
    # 保存图片
    outImg.save(thumbPath, 'jpeg')

def zoomJpg(imgPath, thumbPath, ow, oh):
    image = Image.open(imgPath)
    sw, sh = image.size
    outImg = Image.new('RGB',(ow, oh), '#FFFFFF')
    # 长条图的缩小
    if sw/ow < sh/oh:
        tw = int(oh/sh*sw)
        tmpImg = image.resize((tw, oh), Image.ANTIALIAS)
        cx = int((ow - tw) / 2)
        outImg.paste(tmpImg, (cx, 0))
    # 宽条图的缩小
    else:
        th = int(ow/sw*sh)
        tmpImg = image.resize((ow, th), Image.ANTIALIAS)
        cy = int((oh - th) / 2)
        outImg.paste(tmpImg, (0, cy))
    # 保存图片
    outImg.save(thumbPath, 'jpeg')

async def markThumb(suffix, imgPath, thumbPath, params):
    arr = params.split('-')
    method = arr[0]
    width = int(arr[1])
    height = int(arr[2])
    if method == 'fill':
        if suffix != 'gif':
            fillJpg(imgPath, thumbPath, width, height)
            return await file(thumbPath, status=200)
    if method == 'clip':
        if suffix != 'gif':
            clipJpg(imgPath, thumbPath, width, height)
            return await file(thumbPath, status=200)
    if method == 'zoom':
        if suffix != 'gif':
            zoomJpg(imgPath, thumbPath, width, height)
            return await file(thumbPath, status=200)
