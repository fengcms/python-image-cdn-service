import os
import re
from sanic.response import file, json

# 成功以及失败的返回脚本
def ok(data):
    return json({"data": data, "status": 0})
def fail(data, httpCode=500):
    return json({"data": data, "status": httpCode}, httpCode)

# 默认404处理方法
async def return404():
    return await file('image/404.svg', status=404)

# 字节码转16进制字符串
def bytes2hex(bytes):
    hexstr = u""
    try:
        for i in range(10):
            t = u"%x" % bytes[i]
            if len(t) % 2:
                hexstr += u"0"
            hexstr += t
        return hexstr.lower()

    except Exception as e:
        return hexstr.lower()

# 根据16进制字符串获取文件后缀
def getSuffix(hexStr):
    SUPPORT_TYPE = {
            'ffd8ffe':'jpg',
            '3c73766720786d6c6e73':'svg',
            '89504e470d0a1a0a0000':'png',
            '474946383961':'gif',
        }
    for i in SUPPORT_TYPE:
        if i in hexStr:
            return SUPPORT_TYPE[i]
    return 'error'

# 检查文件是否存在
def hasFile(FilePath):
    return os.path.exists(FilePath)

# 检查字符串是否属于MD5值
def isMd5(String):
    res = re.match('[a-fA-F0-9]{32}', String)
    if res == None:
        return False
    else:
        return True
# 检查图片文件名是否符合规定
def isImgName(name):
    suffixs = ['jpg', 'png', 'gif', 'svg']
    arr = name.split('.')
    if len(arr) != 2:
        return False
    if isMd5(arr[0]) != True:
        return False
    if arr[1] not in arr:
        return False
    return True

# 检查缩略图参数是否符合规定
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

# 创建文件夹
def mkdir(path):
    # 去除首位空格
    path=path.strip()
    # 去除尾部 \ 符号
    path=path.rstrip("\\")
    if not os.path.exists(path):
        os.makedirs(path)


