import threading
from win32api import GetSystemMetrics
import random
import logging
from PIL import Image
import os

from osChangeWallpaper import setWallpaper
from database import WallpaperDatabase
from resources import Resources

class ChangeWallpaperThread(threading.Thread):
    def __init__(self,config,notifyGUI):
        super(ChangeWallpaperThread, self).__init__()
        self.failRetries = config['failRetries']
        self.failWait = config['failWait']
        self.changePeriod = config['changePeriod']
        self.minResolution = config['minResolution']
        self.aspectRatioMargin = config['aspectRatioMargin']
        self.duplicateTimeout = config['duplicateTimeout']
        self.notifyGUI = notifyGUI
        self.imageSources = None
        self.stopEvent = threading.Event()
        self.interruptWaitEvent = threading.Event()
        self.db = WallpaperDatabase()
        self.log = logging.getLogger('WallpaperChanger')
        self.tempDir = os.path.abspath(Resources['TEMP_DIR'])

        screenWitdh = GetSystemMetrics(0)
        screenHeight = GetSystemMetrics(1)
        self.requiredAR = screenWitdh/screenHeight

        self.failedSourceID = None

    def notifyChangeThread(self,argsDict):
        if 'stop' in argsDict and argsDict['stop']:
            self._stopChangeThread()
        if 'setSources' in argsDict:
            self.failedSourceID = None
            self.imageSources = argsDict['setSources']
        if 'setRefreshTimeout' in argsDict:
            self.changePeriod = argsDict['setRefreshTimeout']
        if 'changeWallpaper' in argsDict and argsDict['changeWallpaper']:
            self.interruptWaitEvent.set()
        if 'setMinResolution' in argsDict:
            self.minResolution = argsDict['setMinResolution']
    
    def _stopChangeThread(self):
        self.stopEvent.set()
        self.interruptWaitEvent.set()
        self.join()
    
    def _getImage(self):        
        retDict = None
        retries = 0

        selectedSourceID = None
        retrysourceID = self.failedSourceID
        self.failedSourceID = None

        while (not retDict) and (retries<=self.failRetries) and (not self.stopEvent.is_set()):
            # safer for multithreading
            # GUI/main thread can replace self.imageSources at any time
            imageSources = self.imageSources
            if not imageSources or len(imageSources)==0:
                self.log.error('changeWallpaper: no image sources found')
                self.notifyGUI({'status':f'No image sources found'})
                return None

            # not None = failed in previous iteration
            if selectedSourceID:
                self.failedSourceID = selectedSourceID

            # retry queued from previous _getImage call
            if retrysourceID:
                selectedSourceID = retrysourceID % len(imageSources)
                selectedSource = imageSources[selectedSourceID]
                self.log.info(f'changeWallpaper: retrying previously failed {selectedSource.getTypeName()}:{selectedSource.getName()}')
                retrysourceID = None
            else:  
                selectedSourceID = random.randint(0,len(imageSources)-1)
                selectedSource = imageSources[selectedSourceID]
                self.log.info(f'changeWallpaper: selected random source {selectedSource.getTypeName()}:{selectedSource.getName()}')
            
            try:
                retDict = selectedSource.getImage()
            except:
                retDict = None
            
            if not retDict:
                retries +=1
                self.notifyGUI({'status':f'{selectedSource.getTypeName()}:{selectedSource.getName()}: FAILED, retrying {retries}'})
                self.log.error(f'changeWallpaper: {selectedSource.getTypeName()}:{selectedSource.getName()} failed to get image')
                self.stopEvent.wait(self.failWait)
                continue
            
            metaName = retDict['metaName']
            image = retDict['image']

            try:
                im = Image.open(image)
                imWidth = im.size[0]
                imHeight = im.size[1]
                currentAR = imWidth/imHeight
                aspectRatioDiff =abs(currentAR-self.requiredAR)/self.requiredAR
                if aspectRatioDiff>self.aspectRatioMargin:
                    self.notifyGUI({'status':f'Bad aspect ratio {currentAR} {selectedSource.getTypeName()}:{selectedSource.getName()}:{metaName}'})
                    self.log.error(f'changeWallpaper: {selectedSource.getTypeName()}:{selectedSource.getName()} incompatible aspect ratio AR={currentAR} {metaName}')
                    retDict = None
                    continue

                if imWidth<self.minResolution[0] or imHeight<self.minResolution[1]:
                    self.notifyGUI({'status':f'Small image - {selectedSource.getTypeName()}:{selectedSource.getName()}:{metaName}'})
                    self.log.error(f'changeWallpaper: {selectedSource.getTypeName()}:{selectedSource.getName()} small image {imWidth}x{imHeight} {metaName}')
                    retDict = None
                    continue
            except:
                self.notifyGUI({'status':f'failed to open image {selectedSource.getTypeName()}:{selectedSource.getName()}:{metaName}'})
                self.log.error(f'changeWallpaper: {selectedSource.getTypeName()}:{selectedSource.getName()} failed to open image {image}')
                retDict = None
                continue

            dup = self.db.checkDuplicate(retDict['image'],self.duplicateTimeout)
            if dup:
                imageSource = retDict['imageSource']
                self.notifyGUI({'status':f'Duplicate - {selectedSource.getTypeName()}:{selectedSource.getName()}:{metaName}'})
                self.log.info(f'changeWallpaper: duplicate detected {imageSource}, {dup}')
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
            image = os.path.abspath(image)
            assert(image.startswith(self.tempDir))
            if image.startswith(self.tempDir):
                os.remove(image)
        
        self.notifyGUI({'blockWallpaperChange':False})
            

    def run(self):
        while (self.imageSources is None) and (not self.stopEvent.is_set()):
                self.log.info('ChangeWallpaperThread: waiting for sources to populate')
                self.stopEvent.wait(0.01)
        while not self.stopEvent.is_set():
            self._changeWallpaper()
            self.minutesPassed=0
            while self.minutesPassed<self.changePeriod  and not self.interruptWaitEvent.is_set():
                self.interruptWaitEvent.wait(60)
                self.minutesPassed +=1
                # self.notifyGUI({'status':f'Time since last refresh: {self.minutesPassed} minutes'})
                assert(self.changePeriod >=1)
            self.interruptWaitEvent.clear()
