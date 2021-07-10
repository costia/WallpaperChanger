
from GUI import WallpaperChangerGUI
from osChangeWallpaper import setWallpaper
from redditImageSource import RedditImageSource
import logging
import threading
import time 
import random
import yaml

class ChangeWallpaperThread(threading.Thread):
    def __init__(self,imageSources,config):
        super(ChangeWallpaperThread, self).__init__()
        self.imageSources = imageSources
        self.config = config
        self.stopEvent = threading.Event()
        self.log = logging.getLogger('WallpaperChanger')
    
    def stop(self):
        self.stopEvent.set()

    def run(self):
        while not self.stopEvent.is_set():
            image = None
            retries = 0
            while not image:
                selectedSource = self.imageSources[random.randint(0,len(self.imageSources)-1)]
                self.log.info(f'ChangeWallpaperThread: selected source {selectedSource.getName()}')
                image = selectedSource.getImage()
                if image:
                    setWallpaper(image)
                else:
                    retries +=1
                    if retries>self.config['failRetries']:
                        continue
                    time.sleep(self.config['failWait'])

            time.sleep(self.config['changePeriod'])

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

        with open('config.yaml','rt') as f:
            self.config = yaml.load(f)
        
        self.imageSources  =[]
        for subreddit in self.config['subreddits']:
            redditArgs = {
                'width':self.config['width'],
                'height':self.config['height'],
                'subreddit':subreddit
            }
            self.imageSources.append(RedditImageSource(redditArgs))
        redditArgs = {
            'width':1920,
            'height':1080,
            'subreddit':'wallpapers'
        }
        self.imageSources.append(RedditImageSource(redditArgs))

        self.wallpaperReplaceThread = ChangeWallpaperThread(self.imageSources,self.config)
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
    main()