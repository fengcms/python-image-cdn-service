# Python 图片上传、图片获取以及自动生成缩略图模块说明

## 为什么有这个项目？

**上传部分**

在一般的web项目当中，图片上传到服务器之后，回基于上传时间来给一个独立的命名。这样做的优点是非常便于文件的管理，但是缺点也很明显，就是当同一张图片上传到服务器之后，会生成多张图片，造成硬盘空间资源的浪费。

如果要避免这个问题，绝大多数的解决方案是采用数据库维护不同图片的数据，来达到问题的解决。但是这样会使问题更加复杂化，本来只是为了上传个图片而已，结果还整上一个庞大的管理系统来管理。

所以，在这个项目中，我用了一种非常暴力的手段来解决这个问题，就是直接读取上传图片的文件的MD5哈希值，并用此为文件名存储。这样，当一个重复的图片上传到服务器上之后，会自动的覆盖到原先的存储路径上，避免了存储空间的浪费。

用这个暴力的方法，所造成的后遗症有两个，一个是并没有解决带宽浪费的问题。因为重复图片上传到服务器这一步并没有省略，所以自然这个重复的图片还是必须传输一遍。

这个相对来说还是比较好解决的，只需要客户端在上传图片的时候，先把图片的md5值传过来，检查一下就可以了。不过如果每次上传图片都需要这么做，算下来还是复杂了。因为一般图片都不是特别大，因此我个人觉得没有必要这么做。如果你是用来做其它的大文件的存储，可以考虑我上面说的这个思路，自行完善这部分功能。

还有一个后遗症就是，可能会出现两张不同的图片，他们的MD5值是一样的，这会导致后面的这张图片覆盖了原来的这张图片。我个人的观点是，这个几率是非常非常低的，2e128分之一的几率我感觉在一个中小型的项目上没有必要考虑这个问题。

**获取图片部分**

一般来说，在服务器上的图片都是静态资源的方式进行存储，其URL相对于互联网用户来说是公开的。当然，这样做并没有什么太大的问题。我这边设计的是，图片无论存储在服务器的哪个目录，通过程序来进行读取之后返回给客户端。

这样访客看到的路径其实和服务器的真实路径是不一致的。缺点比较明显，就是多了一层计算，稍微增加了服务器的运算压力。那么这么做的好处是什么呢？其实对于读取原图来说，并没有啥好处。重点是，我增加了一个可以随意生成缩略图的功能。

在普通的web项目当中，一般前端在读取后端返回的图片路径的时候，都是直接读取的。假设首页需要10个产品图片。可能网站管理员上传的都是500\*400的图片，如果直接读取原图的话，对于带宽的要求还是比较高的。比较浪费流量。

因此，有很多项目都会设定缩略图以供用户访问，减轻服务器的带宽压力。我这边也是这个思路，不过为了前端方便，我这边不会限制缩略图的尺寸或者方法。可以所以生成任意尺寸的缩略图。

生成缩略图的方法一般情况有这样几种——拉伸、裁剪、填白缩小。拉伸比较好理解，就是不顾原图的比例，直接拉伸后输出。这样的结果就是缩略图变形得比较厉害。裁剪是保持图片的尺寸不变形，然后根据所需要的缩略图的尺寸大小进行最大范围内的裁剪（居中原则，没有更高级的算法）进行输出。这样的结果是图片不会变形，但是图片会有部分信息被裁剪掉。还有一个就是填白缩放，就是根据缩略图的尺寸创建一个空白的图形，然后将原图等比例缩小到这个缩略图能够容纳的最大尺寸，合并后进行输出。这样的结果是图片不会变形，信息不会丢失，但是如果原图比例和缩略图尺寸比例严重不匹配的话，会造成大面积留白。

每一种生成缩略图的方式都有其不同的应用场景，因此，我这个系统是全面支持者三种不同的缩略图模式的。

本系统支持 jpg png gif svg 等图片格式的缩略图处理。没看错，gif 动图也是完美支持的。不过需要注意的是，如果 gif 动图的尺寸比较大，帧率比较多，会比较严重的消耗服务器资源。

## 项目依赖

本程序基于 python3.7 开发，依赖以下模块：

```
os, sys, io, re, shutil, hashlib, PIL(pillow), imageio, sanic
```

## 项目文件说明

```
├── README.md ············· 说明文件
├── config.py ············· 配置文件
├── core
│   ├── app.py ············ 主程序
│   ├── gif.py ············ GIF 图片拆解
│   ├── thumb.py ·········· 缩略图处理
│   ├── tool.py ··········· 攻击类函数
│   └── upload.py ········· 上传函数
├── image ················· 系统图片文件夹
│   └── 404.svg
├── run.py ················ 程序启动文件
├── temp ·················· 临时文件夹（用于gif图片拆解时临时存放文件）
└── upload ················ 用户文件存储文件夹（只是演示，并不限制存储位置）
```


## 配置文件说明

```
# 用户图片上传存储位置（服务器绝对路径）
STATIC_DIR = '/Users/fungleo/Sites/YuanMu/CDN-Server/upload'
# 项目运行端口设置
PORT = 9000
# 项目运行IP设置，默认为外网可访问
# 只运行于本机可设置为 127.0.0.1
HOST = '0.0.0.0' 
```

## 项目启动

进入项目根目录，运行下面的命令启动：

```
python3 run.py
```

## 如何使用

### 上传图片

#### 普通上传
```
curl http://localhost:9000/upload -F "file=@__YOUR__IMAGE__PATH__"
```

文件上传没有做权限管理，这部分不打算做，我的考虑是，这个项目应该作为微服务启动，权限管理是业务程序的事情。

不过添加水印功能需要完善，这部分功能随后完成。

图片上传成功后，会返回一个包含 md5 组织的文件名的 json 数据，格式如下：

```json
{
  "data": {
    "path": "9194e7ed62ba83c3d181b2f70590ab12.jpg"
  },
  "status": 0
}
```
获取图片只需要根据这个文件名加上不同的参数就可以获取了。

#### 限制最大尺寸上传以及上传图片自动添加水印

在上传图片的时候，采用的是 `form-data` 方式的 POST 提交，因此，想要传输参数的话，是不能直接传输 `json` 格式的数据的。因此，我用一个 `data` 字段，传输一个参数json字符串过去即可。
```
curl http://localhost:9000/upload -F "file=@__YOUR__IMAGE__PATH__" -F 'data={"zoom":200,"mark":{"type":"text","text":"hi,水印","color":"#00F","size":25,"ttf":"Heiti","location":["center","center"]}}'
```

命令行下的提交是如上这样的。参数说明如下：

```json
{
  // 最长边尺寸，只能是正整数
  // 例如设置为400则800*600的图片会压缩为400*300
  // 而600*800的图片会压缩为300*400
  // 如果图片尺寸小于设置数字，则会原图直接保存
  "zoom": 300,
  // 图片水印参数
  "mark": {
    // 类型 可以为 text 或者 img，必填
    "type": "img",
    // 水印图片的 md5 文件名，将水印图片无参数上传就可以得到，必填
    "imgName": "c84739f4dd318edee5b5655bc3091708.png",
    // 水印尺寸，选填。如不填写，则自动读取水印图片的默认尺寸
    "imgSize": [150, 40],
    // 水印位置，第一个参数为X轴，支持 left center right 等参数
    // 第二个参数为Y轴位置，支持 top center bottom 等参数
    // 选填。默认为右下角。
    "location": ["right", "bottom"]
  },
  // 文字水印参数
  "mark": {
    "type": "text",
    // 水印文字，必填。
    "text": "这是一个水印文字",
    // 水印颜色，选填。默认白色。
    "color": "#FFFFFF",
    // 水印文字大小，选填。默认20，最小18。
    "size": 18,
    // 水印字体，需要添加其他字体请将字体文件放到 fonts 文件夹中
    "ttf": "PingFang",
    "location": ["right", "bottom"]
  }
}
```
图片水印参数和文字水印参数不能同时使用。

### 获取图片

**原图获取**

```
http://localhost:9000/proto/9194e7ed62ba83c3d181b2f70590ab12.jpg
```

原图的获取，只需要用 `proto` 前缀就可以获取了。

**缩略图获取**

缩略图的获取，是使用 `thumb` 前缀，外加参数的方式来进行获取，如下示例：

```
http://localhost:9000/thumb/fill-200-200/9194e7ed62ba83c3d181b2f70590ab12.jpg
```

支持三种缩略图的生成方式：

| 缩略图生成方式 | 参数 | 
| --- | --- |
| 拉伸 | fill |
| 裁切 | clip |
| 填白缩放 | zoom |

确定缩略图生成方式之后，就是规定缩略图的宽高了，只要指定像素尺寸即可。

```
方法-宽度-高度
```
参数之间采用英文中划线间隔，然后就可以请求到不同尺寸以及不同规格的缩略图了。

## License

[MIT](http://opensource.org/licenses/MIT)
Copyright &copy; 2019-present FungLeo
