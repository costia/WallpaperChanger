import threading
import time 
import random
import logging

from osChangeWallpaper import setWallpaper
from database import WallpaperDatabase

class ChangeWallpaperThread(threading.Thread):
    def __init__(self,config,notifyGUI):
        super(ChangeWallpaperThread, self).__init__()
        self.failRetries = config['failRetries']
        self.failWait = config['failWait']
        self.changePeriod = config['changePeriod']
        self.notifyGUI = notifyGUI
        self.imageSources = None
        self.stopEvent = threading.Event()
        self.interruptWaitEvent = threading.Event()
        self.db = WallpaperDatabase()
        self.log = logging.getLogger('WallpaperChanger')

    def notifyChangeThread(self,argsDict):
        if 'stop' in argsDict and argsDict['stop']:
            self._stopChangeThread()
        if 'setSources' in argsDict:
            self.imageSources = argsDict['setSources']
        if 'setRefreshTimeout' in argsDict:
            self.changePeriod = argsDict['setRefreshTimeout']
        if 'changeWallpaper' in argsDict and argsDict['changeWallpaper']:
            self.interruptWaitEvent.set()
    
    def _stopChangeThread(self):
        self.stopEvent.set()
        self.interruptWaitEvent.set()
        self.join()
    
    def _changeWallpaper(self):
        self.notifyGUI({'status':'Changing wallpaper','blockWallpaperChange':True})
        image = None
        retries = 0
        while not image:
            if not self.imageSources or len(self.imageSources)==0:
                self.log.error('changeWallpaper: no image sources found')
                self.notifyGUI({'status':f'No image sources found'})
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
                    self.notifyGUI({'status':f'Duplicate - {selectedSource.getTypeName()}:{selectedSource.getName()}:{metaName}'})
                    self.log.info(f'changeWallpaper: duplicate detected {metaName}, {dup}')
                    image = None
            else:
                self.notifyGUI({'status':f'{selectedSource.getTypeName()}:{selectedSource.getName()}: FAILED, retrying {retries}'})
            
            retries +=1
            if retries>self.failRetries:
                self.notifyGUI({'status':f'{selectedSource.getTypeName()}:{selectedSource.getName()}: FAILED, retries exhausted'})
                break
            self.stopEvent.wait(self.failWait)
            if self.stopEvent.is_set():
                break
        
        if image:
            setWallpaper(image)
            self.notifyGUI({'status':f'{selectedSource.getTypeName()}:{selectedSource.getName()}: {metaName}'})
            dbEntry={
                'sourceType':selectedSource.getTypeName(),
                'sourceName':selectedSource.getName(),
                'imageName': metaName,
                'imageSource':retDict['imageSource'],
                'image':image
            }
            self.db.addEntry(dbEntry)
            self.notifyGUI({'updateHistory':True})
        
        self.notifyGUI({'blockWallpaperChange':False})
            

    def run(self):
        while (self.imageSources is None) and (not self.stopEvent.is_set()):
                self.log.info('ChangeWallpaperThread: waiting for sources to populate')
                self.stopEvent.wait(0.05)
        while not self.stopEvent.is_set():
            self._changeWallpaper()
            self.minutesPassed=0
            while self.minutesPassed<self.changePeriod  and not self.interruptWaitEvent.is_set():
                self.interruptWaitEvent.wait(60)
                self.minutesPassed +=1
                # self.notifyGUI({'status':f'Time since last refresh: {self.minutesPassed} minutes'})
                assert(self.changePeriod >=1)
            self.interruptWaitEvent.clear()
