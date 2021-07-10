import threading
import time 
import random
import logging
from osChangeWallpaper import setWallpaper

class ChangeWallpaperThread(threading.Thread):
    def __init__(self,config,setStatus):
        super(ChangeWallpaperThread, self).__init__()
        self.config = config
        self.setStatus = setStatus
        self.stopEvent = threading.Event()
        self.log = logging.getLogger('WallpaperChanger')
    
    def stop(self):
        self.stopEvent.set()

    def resetSources(self,imageSources):
        self.imageSources = imageSources

    def changeWallpaper(self):
        self.setStatus('Changing wallpaper',{'blockChange':True})
        self.minutesPassed=0
        image = None
        retries = 0
        while not image:
            selectedSource = self.imageSources[random.randint(0,len(self.imageSources)-1)]
            self.log.info(f'ChangeWallpaperThread: selected source {selectedSource.getName()}')
            retDict = selectedSource.getImage()
            if retDict:
                image = retDict['image']
                metaName = retDict['metaName']
                setWallpaper(image)
                self.setStatus(f'{selectedSource.getName()}: {metaName}',{'blockChange':False})
            else:
                self.setStatus(f'{selectedSource.getName()}: FAILED, retrying')
                retries +=1
                if retries>self.config['failRetries']:
                    break
                time.sleep(self.config['failWait'])
        if not image:
            self.setStatus(f'{selectedSource.getName()}: FAILED, retries exhausted',{'blockChange':False})
        self.minutesPassed=0

    def run(self):
        while not self.stopEvent.is_set():
            self.changeWallpaper()
            while self.minutesPassed<self.config['changePeriod']:
                time.sleep(60)
                self.minutesPassed +=1
                # self.setStatus(f'Time since last refresh: {self.minutesPassed} minutes')
                assert(self.config['changePeriod']>=1)
