import threading
import time 
import random
import logging

from osChangeWallpaper import setWallpaper
from database import WallpaperDatabase

class ChangeWallpaperThread(threading.Thread):
    def __init__(self,config,setStatus):
        super(ChangeWallpaperThread, self).__init__()
        self.failRetries = config['failRetries']
        self.failWait = config['failWait']
        self.changePeriod = config['changePeriod']
        self.setStatus = setStatus
        self.imageSources = None
        self.stopEvent = threading.Event()
        self.interruptWaitEvent = threading.Event()
        self.db = WallpaperDatabase()
        self.log = logging.getLogger('WallpaperChanger')
    
    def stop(self):
        self.stopEvent.set()
        self.interruptWaitEvent.set()
        self.join()

    def setRefreshTimeout(self,timeout):
        self.changePeriod = timeout

    def setSources(self,imageSources):
        self.imageSources = imageSources

    def changeWallpaper(self):
        self.interruptWaitEvent.set()

    def _changeWallpaper(self):
        self.setStatus({'status':'Changing wallpaper','blockWallpaperChange':True})
        image = None
        retries = 0
        while not image:
            if not self.imageSources or len(self.imageSources)==0:
                self.log.error('changeWallpaper: no image sources found')
                self.setStatus({'status':f'No image sources found'})
                break

            selectedSource = self.imageSources[random.randint(0,len(self.imageSources)-1)]
            self.log.info(f'changeWallpaper: selected source {selectedSource.getName()}')
            try:
                retDict = selectedSource.getImage()
            except:
                retDict = None
            if retDict:
                image = retDict['image']
                metaName = retDict['metaName']
                dup = self.db.checkDuplicate(image)
                if dup:
                    self.setStatus({'status':f'Duplicate - {selectedSource.getTypeName()}:{selectedSource.getName()}:{metaName}'})
                    self.log.info(f'changeWallpaper: duplicate detected {metaName}, {dup}')
                    image = None
            else:
                self.setStatus({'status':f'{selectedSource.getTypeName()}:{selectedSource.getName()}: FAILED, retrying'})
            
            retries +=1
            if retries>self.failRetries:
                self.setStatus({'status':f'{selectedSource.getTypeName()}:{selectedSource.getName()}: FAILED, retries exhausted','blockWallpaperChange':False})
                break
            self.stopEvent.wait(self.failWait)
            if self.stopEvent.is_set():
                break
        
        if image:
            setWallpaper(image)
            self.setStatus({'status':f'{selectedSource.getTypeName()}:{selectedSource.getName()}: {metaName}', 'blockWallpaperChange':False})
            dbEntry={
                'sourceType':selectedSource.getTypeName(),
                'sourceName':selectedSource.getName(),
                'imageName': metaName,
                'imageSource':retDict['imageSource'],
                'image':image
            }
            self.db.addEntry(dbEntry)
            self.setStatus({'updateHistory':True})
            

    def run(self):
        while not self.stopEvent.is_set():
            while not self.imageSources :
                self.log.info('ChangeWallpaperThread: waiting for sources to populate')
                self.stopEvent.wait(1)
                if self.stopEvent.is_set():
                    break
            self._changeWallpaper()
            self.minutesPassed=0
            while self.minutesPassed<self.changePeriod  and not self.interruptWaitEvent.is_set():
                self.interruptWaitEvent.wait(60)
                self.minutesPassed +=1
                # self.setStatus({'status':f'Time since last refresh: {self.minutesPassed} minutes'})
                assert(self.changePeriod >=1)
            self.interruptWaitEvent.clear()
