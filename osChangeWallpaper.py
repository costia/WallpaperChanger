from  PIL import Image
import os
import logging
import ctypes

def setWallpaper(path):
    log = logging.getLogger('WallpaperChanger')
    if not os.path.isfile(path):
        log.error(f'setWallpaper: file not found {path}')
        return False

    tempDir = os.path.abspath('./temp')
    if not os.path.isdir(tempDir):
        os.mkdir(tempDir)
    try:
        im = Image.open(path)
    except:
        log.error(f'setWallpaper: file not an image {path}')
        return False
    im.save(tempDir+'/temp.bmp')

    ret = ctypes.windll.user32.SystemParametersInfoW(20, 0, tempDir+'/temp.bmp' , 0)
    if not ret:
        log.error(f'setWallpaper: OS call failed {path}')
        return False

    log.info(f'setWallpaper: changed wallpaper to {path}')
    return True