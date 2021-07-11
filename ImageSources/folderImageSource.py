import os
import logging
import random

from wx.core import StaticBitmap

class FolderImageSource:
    def __init__(self,argsDict):
        self.path = argsDict['config']
        self.log = logging.getLogger('WallpaperChanger')
        self.imageTypes = ['.jpeg','.jpg','.png','.tiff','.tif','.gif']

    def getName(self):
        return self.path
    
    @staticmethod
    def getTypeName():
        return 'folder'

    def getImage(self):
        if not os.path.isdir(self.path):
            self.log.error(f'FolderImageSource: directory does not exist {self.path}')
            return None
        fileList=os.listdir(self.path)
        fileList = list(filter(lambda x: os.path.isfile(self.path+'/'+x),fileList))
        if len(fileList)==0:
            self.log.error(f'FolderImageSource: no files found in {self.path}')
            return None
        selectedFile = fileList[random.randint(0,len(fileList)-1)]
        selectedFile = self.path+'/'+selectedFile
        _,selectedExtension = os.path.splitext(selectedFile)
        selectedExtension = selectedExtension.lower()
        if not selectedExtension in self.imageTypes:
            self.log.error(f'FolderImageSource: selected file is not an image {selectedFile}')
            return None
        
        self.log.info(f'FolderImageSource: selected file is {selectedFile}')
        retData = {
            'image':selectedFile,
            'metaName':os.path.basename(selectedFile)
        }
        return retData


