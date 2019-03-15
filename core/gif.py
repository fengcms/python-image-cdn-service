#-*- coding: UTF-8 -*-  
import os
from PIL import Image
from core.tool import mkdir
 
def analyseGif(im):
#    im = Image.open(path)
    results = {
        'size': im.size,
        'mode': 'full',
    }
    try:
        while True:
            if im.tile:
                tile = im.tile[0]
                update_region = tile[1]
                update_region_dimensions = update_region[2:]
                if update_region_dimensions != im.size:
                    results['mode'] = 'partial'
                    break
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    return results
 
 
def hackGif(im, path):
    mode = analyseGif(im)['mode']
    #im = Image.open(path)
    i = 0
    p = im.getpalette()
    last_frame = im.convert('RGBA')
    
    res = []
    tempDir = 'temp/' + ''.join(os.path.basename(path).split('.')[:-1])
    try:
        while True:
            if not im.getpalette():
                im.putpalette(p)
            
            new_frame = Image.new('RGBA', im.size)
            
            if mode == 'partial':
                new_frame.paste(last_frame)
            
            new_frame.paste(im, (0,0), im.convert('RGBA'))
            mkdir(tempDir)
            savePath = tempDir + '/' + str(i) + '.png'
            new_frame.save(savePath, 'PNG')
            res.append(savePath)
 
            i += 1
            last_frame = new_frame
            im.seek(im.tell() + 1)

    except EOFError:
        pass
    return (res, tempDir, im.info['duration'])
