from  PIL import Image
import os
import logging
import ctypes
import time
import threading
import random
from wx.core import INT64_MAX

from resources import Resources

def removeTemp(tempName):
    log = logging.getLogger('WallpaperChanger')
    try:
        time.sleep(2)
        os.remove(tempName)
    except:
        log.error(f'setWallpaper: Failed deleting temp file {tempName}')


def setWallpaper(path):
    log = logging.getLogger('WallpaperChanger')
    if not os.path.isfile(path):
        log.error(f'setWallpaper: file not found {path}')
        return False

    tempDir = Resources['TEMP_DIR']
    tempBmp = tempDir+f'/temp_{str(random.randint(0,INT64_MAX))}.bmp'

    try:
        im = Image.open(path)
    except:
        log.error(f'setWallpaper: file not an image {path}')
        return False
    im.save(tempBmp)
    im.close()

    ret = ctypes.windll.user32.SystemParametersInfoW(20, 0, tempBmp , 0)
    if not ret:
        log.error(f'setWallpaper: OS call failed {path}')
        return False

    deleteThread = threading.Thread(target=removeTemp,args=(tempBmp,))
    deleteThread.start()

    log.info(f'setWallpaper: changed wallpaper to {path}')
    return True