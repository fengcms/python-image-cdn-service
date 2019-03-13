import os
import re
from sanic.response import file
def hasFile(FilePath):
    return os.path.exists(FilePath)

def isMd5(String):
    res = re.match('[a-fA-F0-9]{32}', String)
    if res == None:
        return False
    else:
        return True
def isImgName(name):
    suffixs = ['jpg', 'png', 'gif']
    arr = name.split('.')
    if len(arr) != 2:
        return False
    if isMd5(arr[0]) != True:
        return False
    if arr[1] not in arr:
        return False
    return True

def checkThumbParams(params):
    methods = ['fill', 'clip', 'zoom']
    arr = params.split('-')
    if len(arr) != 3:
        return False
    if arr[0] not in methods:
        return False
    if not arr[1].isdigit() or not arr[1].isdigit():
        return False
    return True

def mkdir(path):
    # 去除首位空格
    path=path.strip()
    # 去除尾部 \ 符号
    path=path.rstrip("\\")
    if not os.path.exists(path):
        os.makedirs(path)

async def return404():
    return await file('image/404.svg', status=404)

