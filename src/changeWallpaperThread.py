import threading
import time 
import random
import logging

from osChangeWallpaper import setWallpaper
from database import WallpaperDatabase

class ChangeWallpaperThread(threading.Thread):
    def __init__(self,config,setStatus):
        super(ChangeWallpaperThread, self).__init__()
        self.config = config
        self.setStatus = setStatus
        self.stopEvent = threading.Event()
        self.db = WallpaperDatabase()
        self.log = logging.getLogger('WallpaperChanger')
    
    def stop(self):
        self.stopEvent.set()

    def resetSources(self,imageSources):
        self.imageSources = imageSources

    def changeWallpaper(self):
        self.setStatus({'status':'Changing wallpaper','blockChange':True})
        self.minutesPassed=0
        image = None
        retries = 0
        while not image:
            if len(self.imageSources)==0:
                self.log.error('changeWallpaper: no image sources found')
                self.setStatus({'status':f'No image sources found'})
                break

            selectedSource = self.imageSources[random.randint(0,len(self.imageSources)-1)]
            self.log.info(f'changeWallpaper: selected source {selectedSource.getName()}')
            retDict = selectedSource.getImage()
            if retDict:
                image = retDict['image']
                metaName = retDict['metaName']
                dup = self.db.checkDuplicate(image)
                if dup:
                    self.setStatus({'status':f'Duplicate - {selectedSource.getName()}:{metaName}'})
                    self.log.info(f'changeWallpaper: duplicate detected {metaName}, {dup}')
                    image = None
            else:
                self.setStatus({'status':f'{selectedSource.getName()}: FAILED, retrying'})
            
            retries +=1
            if retries>self.config['failRetries']:
                self.setStatus({'status':f'{selectedSource.getName()}: FAILED, retries exhausted','blockChange':False})
                break
            time.sleep(self.config['failWait'])
        
        if image:
            setWallpaper(image)
            self.setStatus({'status':f'{selectedSource.getName()}: {metaName}', 'blockChange':False})
            dbEntry={
                'sourceType':selectedSource.getTypeName(),
                'sourceName':selectedSource.getName(),
                'imageName': metaName,
                'imageSource':retDict['imageSource'],
                'image':image
            }
            self.db.addEntry(dbEntry)
            self.setStatus({'updateHistory':True})
                
        self.minutesPassed=0

    def run(self):
        while not self.stopEvent.is_set():
            self.changeWallpaper()
            while self.minutesPassed<self.config['changePeriod']:
                time.sleep(60)
                self.minutesPassed +=1
                # self.setStatus({'status':f'Time since last refresh: {self.minutesPassed} minutes'})
                assert(self.config['changePeriod']>=1)
