
from GUI import WallpaperChangerGUI
from osChangeWallpaper import setWallpaper
from redditImageSource import RedditImageSource
import logging
import threading
import time 

class ChangeWallpaperThread(threading.Thread):
    def __init__(self,app):
        super(ChangeWallpaperThread, self).__init__()
        self.app = app
        self.stopEvent = threading.Event()
    
    def stop(self):
        self.stopEvent.set()

    def run(self):
        while not self.stopEvent.is_set():
            image = None
            while not image:
                image = self.app.imageSource.getImage()
                time.sleep(1)
                if image:
                    setWallpaper(image)
            time.sleep(60*30)

class MainApp:
    def __init__(self):
        log = logging.getLogger('WallpaperChanger')
        log.setLevel(logging.INFO)
        fileHandler = logging.FileHandler('log.txt')
        fileHandler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s, %(levelname)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
        fileHandler.setFormatter(formatter)
        log.addHandler(fileHandler)
        log.info(f'MainApp: started')

        redditArgs = {
            'width':1920,
            'height':1080,
            'subreddit':'wallpaper'
        }
        self.imageSource  = RedditImageSource(redditArgs)

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