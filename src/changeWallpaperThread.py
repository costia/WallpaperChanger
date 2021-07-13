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
    
    def _getImage(self):
        if not self.imageSources or len(self.imageSources)==0:
            self.log.error('changeWallpaper: no image sources found')
            self.notifyGUI({'status':f'No image sources found'})
            return None
        
        retDict = None
        retries = 0
        while (not retDict) and (retries<=self.failRetries) and (not self.stopEvent.is_set()):
            selectedSource = self.imageSources[random.randint(0,len(self.imageSources)-1)]
            self.log.info(f'changeWallpaper: selected source {selectedSource.getName()}')
            try:
                retDict = selectedSource.getImage()
            except:
                retDict = None
            
            if not retDict:
                retries +=1
                self.notifyGUI({'status':f'{selectedSource.getTypeName()}:{selectedSource.getName()}: FAILED, retrying {retries}'})
                self.stopEvent.wait(self.failWait)
                continue

            dup = self.db.checkDuplicate(retDict['image'])
            if dup:
                metaName = retDict['metaName']
                self.notifyGUI({'status':f'Duplicate - {selectedSource.getTypeName()}:{selectedSource.getName()}:{metaName}'})
                self.log.info(f'changeWallpaper: duplicate detected {metaName}, {dup}')
                retDict = None
                continue

            retDict['selectedSourceType'] = selectedSource.getTypeName()
            retDict['selectedSourceName'] = selectedSource.getName()

        if not retDict:
            self.notifyGUI({'status':f'{selectedSource.getTypeName()}:{selectedSource.getName()}: FAILED'})

        return retDict

    def _changeWallpaper(self):
        self.notifyGUI({'status':'Changing wallpaper','blockWallpaperChange':True})
        
        imageDict = self._getImage()
        
        if imageDict:
            selectedSourceType = imageDict['selectedSourceType']
            selectedSourceName = imageDict['selectedSourceName']
            metaName = imageDict['metaName']
            image = imageDict['image']
            imageSource = imageDict['imageSource']

            ret = setWallpaper(image)
            if ret:
                self.notifyGUI({'status':f'{selectedSourceType}:{selectedSourceName}: {metaName}'})
            else:
                self.notifyGUI({'status':f'Failed applying {selectedSourceType}:{selectedSourceName}: {metaName}'})
                self.log.error(f'ChangeWallpaperThread: Failed applying {selectedSourceType}:{selectedSourceName}: {image}')
            
            dbEntry={
                'sourceType':selectedSourceType,
                'sourceName':selectedSourceName,
                'imageName': metaName,
                'imageSource':imageSource,
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
