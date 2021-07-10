import logging
import yaml
import shutil
from win32api import GetSystemMetrics

from resources import Resources
from GUI import WallpaperChangerGUI
from redditImageSource import RedditImageSource
from folderImageSource import FolderImageSource
from changeWallpaperThread import ChangeWallpaperThread

class MainApp:
    def __init__(self):
        self.log = logging.getLogger('WallpaperChanger')
        self.log.setLevel(logging.INFO)
        fileHandler = logging.FileHandler(Resources['LOG_FILE'],encoding='utf-8')
        fileHandler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s, %(levelname)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
        fileHandler.setFormatter(formatter)
        self.log.addHandler(fileHandler)
        self.log.info(f'MainApp: started')

        self.width = GetSystemMetrics(0)
        self.height = GetSystemMetrics(1)

        for param in Resources:
            self.log.info(f'MainApp: {param}:{Resources[param]}')

        with open(Resources['CONFIG_YAML'],'rt') as f:
            self.config = yaml.load(f,Loader=yaml.SafeLoader)
        
        self.sourceMapping ={
            'subreddit':RedditImageSource,
            'folder':FolderImageSource
        }

        
        
        sourceTypes=[x for x in self.sourceMapping]
        self.GUI = WallpaperChangerGUI(self,sourceTypes)

        self.wallpaperReplaceThread = ChangeWallpaperThread(self.config,self.setStatus)
        self.resetSources()
        
        self.wallpaperReplaceThread.start()
        self.GUI.MainLoop()
        pass

    def setStatus(self,text,statusDict={}):
        self.GUI.setStatus(text,statusDict)
    
    def resetSources(self):
        newSources = []
        for source in self.config['sources']:
            sourceType = source['type']
            if not sourceType in self.sourceMapping:
                self.log.error(f'MainApp: unknow source type {sourceType}')
                continue
            instanceType = self.sourceMapping[sourceType]
            redditArgs = {
                'width':self.width,
                'height':self.height,
                'config':source['config'],
                'aspecRatioMargin':self.config['aspecRatioMargin']
            }

            newSources.append(instanceType(redditArgs))
        self.imageSources = newSources
        self.wallpaperReplaceThread.resetSources(self.imageSources)
        
    def configChanged(self):
        self.saveConfig()

    def changeWallpaper(self):
        self.wallpaperReplaceThread.changeWallpaper()

    def saveConfig(self):
        configPath=Resources['CONFIG_YAML']
        shutil.copyfile(configPath,configPath+'.bak')
        with open(configPath,'wt') as f:
            yaml.dump(self.config,f,Dumper=yaml.SafeDumper,sort_keys=False)
        self.log.info(f'MainApp: saved config {configPath}')

    def handleExit(self):
        self.wallpaperReplaceThread.stop()
        self.saveConfig()
        self.GUI.exitGUI()

def main():
    app = MainApp()
    pass



if __name__ == '__main__':
    main()