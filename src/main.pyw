import logging
import yaml
import shutil
from win32api import GetSystemMetrics
import copy

from resources import Resources
from GUI.wallpaperChangerGUI import WallpaperChangerGUI
from ImageSources import ImageSource, registerAllTypes
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

        registerAllTypes()

        self.width = GetSystemMetrics(0)
        self.height = GetSystemMetrics(1)

        for param in Resources:
            self.log.info(f'MainApp: {param}:{Resources[param]}')

        with open(Resources['CONFIG_YAML'],'rt') as f:
            self.config = yaml.load(f,Loader=yaml.SafeLoader)

        configPath=Resources['CONFIG_YAML']
        shutil.copyfile(configPath,configPath+'.bak')
        
        self.GUI = WallpaperChangerGUI(self)

        self.wallpaperReplaceThread = ChangeWallpaperThread(self.config,self.setStatus)
        self.resetSources()
        
        self.wallpaperReplaceThread.start()
        self.GUI.MainLoop()
        pass

    def setStatus(self,statusDict={}):
        self.GUI.setStatus(statusDict)
    
    def resetSources(self):
        newSources = []
        for source in self.config['sources']:
            redditArgs = {
                'type':source['type'],
                'config':source['config'],
                'width':self.width,
                'height':self.height,
                'aspectRatioMargin':self.config['aspectRatioMargin']
            }
            redditArgs = copy.deepcopy(redditArgs)
            sourceInstance = ImageSource(redditArgs)
            if sourceInstance:
                newSources.append(sourceInstance)
        self.imageSources = newSources
        self.wallpaperReplaceThread.setSources(self.imageSources)
        self.GUI.setStatus({'imageSources':self.imageSources})
        
    def configChanged(self):
        self.saveConfig()

    def changeWallpaper(self):
        self.wallpaperReplaceThread.changeWallpaper()

    def saveConfig(self):
        configPath=Resources['CONFIG_YAML']
        with open(configPath,'wt') as f:
            yaml.dump(self.config,f,Dumper=yaml.SafeDumper,sort_keys=False)
        self.log.info(f'MainApp: saved config {configPath}')

    def handleExit(self):
        self.log.info(f'MainApp: closing')
        self.setStatus({'status':'Closing...'})
        self.saveConfig()
        self.wallpaperReplaceThread.stop()
        self.GUI.exitGUI()

def main():
    app = MainApp()
    pass



if __name__ == '__main__':
    main()