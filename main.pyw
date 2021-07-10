
from GUI import WallpaperChangerGUI
from osChangeWallpaper import setWallpaper
from redditImageSource import RedditImageSource
import logging
import threading
import time 
import random

class ChangeWallpaperThread(threading.Thread):
    def __init__(self,app):
        super(ChangeWallpaperThread, self).__init__()
        self.app = app
        self.stopEvent = threading.Event()
        self.log = logging.getLogger('WallpaperChanger')
    
    def stop(self):
        self.stopEvent.set()

    def run(self):
        while not self.stopEvent.is_set():
            image = None
            while not image:
                selectedSource = self.app.imageSources[random.randint(0,len(self.app.imageSources)-1)]
                self.log.info(f'ChangeWallpaperThread: selected source {selectedSource.getName()}')
                image = selectedSource.getImage()
                time.sleep(1)
                if image:
                    setWallpaper(image)
            time.sleep(60*30)

class MainApp:
    def __init__(self):
        log = logging.getLogger('WallpaperChanger')
        log.setLevel(logging.INFO)
        fileHandler = logging.FileHandler('log.txt',encoding='utf-8')
        fileHandler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s, %(levelname)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
        fileHandler.setFormatter(formatter)
        log.addHandler(fileHandler)
        log.info(f'MainApp: started')

        
        self.imageSources  =[]
        redditArgs = {
            'width':1920,
            'height':1080,
            'subreddit':'wallpaper'
        }
        self.imageSources.append(RedditImageSource(redditArgs))
        redditArgs = {
            'width':1920,
            'height':1080,
            'subreddit':'wallpapers'
        }
        self.imageSources.append(RedditImageSource(redditArgs))

        self.wallpaperReplaceThread = ChangeWallpaperThread(self)
        self.wallpaperReplaceThread.start()
        
        self.GUI = WallpaperChangerGUI(self)
        self.GUI.MainLoop()
        pass

    
    def handleExit(self):
        self.wallpaperReplaceThread.stop()
        self.GUI.exitGUI()

def main():
    app = MainApp()
    pass



if __name__ == '__main__':
    # ret = ctypes.windll.user32.SystemParametersInfoW(20, 0, 'C:\\Users\\Costia\\Documents\\cofeePy\\1.bmp' , 0)

    main()