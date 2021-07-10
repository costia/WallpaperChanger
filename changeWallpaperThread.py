import threading
import time 
import random
import logging
from osChangeWallpaper import setWallpaper

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
            
            minutesPassed=0
            while minutesPassed<self.config['changePeriod']:
                time.sleep(60)
                minutesPassed +=1
                assert(self.config['changePeriod']>=1)
