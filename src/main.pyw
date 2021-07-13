import logging
import yaml
import shutil
import copy
import threading
import wx

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

        for param in Resources:
            self.log.info(f'MainApp: {param}:{Resources[param]}')

        with open(Resources['CONFIG_YAML'],'rt') as f:
            self.config = yaml.load(f,Loader=yaml.SafeLoader)

        configPath=Resources['CONFIG_YAML']
        shutil.copyfile(configPath,configPath+'.bak')
        
        self.GUI = WallpaperChangerGUI(self)

        self.wallpaperReplaceThread = ChangeWallpaperThread(self.config,self.notifyGUI)        
        self.wallpaperReplaceThread.start()

        self._resetSources()
        self.GUI.MainLoop()
        pass

    def notifyGUI(self,argsDict):
        wx.CallAfter(self.GUI.notifyGUI,argsDict)

    def _removeSource(self,index):
        self.log.info(f'MainApp: removed source index {index}')
        self.notifyGUI({'lockSourceEdit':True})
        newSourceList=copy.copy(self.imageSources)
        removedSource = newSourceList[index]
        del newSourceList[index]
        newList = copy.deepcopy(self.config['sources'])
        del newList[index]

        self.config['sources']=newList
        self.imageSources = newSourceList
        self._saveConfig()
        self.wallpaperReplaceThread.notifyChangeThread({'setSources':self.imageSources})
        self.notifyGUI({'imageSources':self.imageSources,'lockSourceEdit':False})
        self.log.info(f'MainApp: removed source {removedSource.getTypeName()}:{removedSource.getName()}')
        
    def _addSource(self,sourceDict):
        configString = str(sourceDict['config'])
        sourceType = sourceDict['type']
        self.log.info(f'MainApp: adding source {sourceType}:{configString}')
        self.notifyGUI({'lockSourceEdit':True})
        addThread = threading.Thread(target = self._addSource_thread,args=(sourceDict,))
        addThread.start()
    
    def _addSource_thread(self,sourceDict):
        newSources = copy.copy(self.imageSources)
        redditArgs = copy.deepcopy(sourceDict)
        sourceInstance = ImageSource(redditArgs)
        if sourceInstance:
            newSources.append(sourceInstance)
            self.config['sources'].append(sourceDict)
            self.imageSources = newSources
            self._saveConfig()
            self.wallpaperReplaceThread.notifyChangeThread({'setSources':self.imageSources})
            self.notifyGUI({'imageSources':self.imageSources,'lockSourceEdit':False})
        self.log.info('MainApp: addSources thread done')

    def _resetSources(self):
        self.log.info('MainApp: started resetSources thread')
        self.notifyGUI({'lockSourceEdit':True})
        resetThread = threading.Thread(target = self._resetSources_thread)
        resetThread.start()
    
    def _resetSources_thread(self):
        newSources = []
        for source in self.config['sources']:
            redditArgs = copy.deepcopy(source)
            sourceInstance = ImageSource(redditArgs)
            if sourceInstance:
                newSources.append(sourceInstance)
        self.imageSources = newSources
        self.wallpaperReplaceThread.notifyChangeThread({'setSources':self.imageSources})
        self.notifyGUI({'imageSources':self.imageSources,'lockSourceEdit':False})
        self.log.info('MainApp: resetSources thread done')
    
    def _setRefreshTimeout(self,timeout):
        self.config['changePeriod']=timeout
        self.wallpaperReplaceThread.notifyChangeThread({'setRefreshTimeout':timeout})
        self._saveConfig()

    def _saveConfig(self):
        configPath=Resources['CONFIG_YAML']
        with open(configPath,'wt') as f:
            yaml.dump(self.config,f,Dumper=yaml.SafeDumper,sort_keys=False)
        self.log.info(f'MainApp: saved config {configPath}')

    def _handleExit(self):
        self.log.info(f'MainApp: closing')
        self.notifyGUI({'status':'Closing...'})
        self._saveConfig()
        self.wallpaperReplaceThread.notifyChangeThread({'stop':True})
        self.notifyGUI({'exitGUI':True})
    
    def notifyMain(self,argsDict):
        if 'handleExit' in argsDict and argsDict['handleExit']:
            self._handleExit()
        if 'changeWallpaper' in argsDict and argsDict['changeWallpaper']:
            self.wallpaperReplaceThread.notifyChangeThread({'changeWallpaper':True})     
        if 'removeSource' in argsDict:
            self._removeSource(argsDict['removeSource'])
        if 'addSource' in argsDict:
            self._addSource(argsDict['addSource'])
        if 'setRefreshTimeout' in argsDict:
            self._setRefreshTimeout(argsDict['setRefreshTimeout'])
            

def main():
    app = MainApp()
    pass



if __name__ == '__main__':
    main()