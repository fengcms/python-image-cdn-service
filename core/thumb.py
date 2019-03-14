import os
import shutil

from PIL import Image
import imageio
from sanic.response import file
from core.gif import hackGif
from core.tool import checkSuffix

# 拉伸处理图片函数
def fillImg(suffix, imgPath, thumbPath, ow, oh):
    image = Image.open(imgPath)
    thumb = image.resize((ow, oh), Image.ANTIALIAS)
    thumb.save(thumbPath, checkSuffix(suffix))

# 裁剪处理图片函数
def clipImg(suffix, imgPath, thumbPath, ow, oh):
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
    outImg.save(thumbPath, checkSuffix(suffix))

# 缩放处理图片函数
def zoomImg(suffix, imgPath, thumbPath, ow, oh):
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
    outImg.save(thumbPath, checkSuffix(suffix))

async def markThumb(suffix, imgPath, thumbPath, params):
    arr = params.split('-')
    method = arr[0]
    ow = int(arr[1])
    oh = int(arr[2])
    if suffix != 'gif':
        if method == 'fill':
            fillImg(suffix, imgPath, thumbPath, ow, oh)
        if method == 'clip':
            clipImg(suffix, imgPath, thumbPath, ow, oh)
        if method == 'zoom':
            zoomImg(suffix, imgPath, thumbPath, ow, oh)
    else:
        # 将 gif 拆解为一组照片
        tempGIf = hackGif(imgPath)
        tempImgPath = tempGIf[0]
        tempDirPath = tempGIf[1]
        gifDur = tempGIf[2] / 1000
        tempImg = []
        # 压缩每一张照片
        for i in tempImgPath:
            if method == 'fill':
                fillImg('gif', i, i, ow, oh)
            if method == 'clip':
                clipImg('gif', i, i, ow, oh)
            if method == 'zoom':
                zoomImg('gif', i, i, ow, oh)
            tempImg.append(imageio.imread(i))
        # 将拆解出来的图片重新组装为gif图片
        imageio.mimsave(thumbPath, tempImg, 'GIF', duration = gifDur)
        # 删除临时文件夹
        shutil.rmtree(tempDirPath)

    return await file(thumbPath, status=200)
