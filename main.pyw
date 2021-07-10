import logging
import yaml
import shutil
from win32api import GetSystemMetrics

from resources import Resources
from GUI import WallpaperChangerGUI
from redditImageSource import RedditImageSource
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
        
        self.imageSources  =[]
        for subreddit in self.config['subreddits']:
            redditArgs = {
                'width':self.width,
                'height':self.height,
                'subreddit':subreddit,
                'aspecRatioMargin':self.config['aspecRatioMargin']
            }
            self.imageSources.append(RedditImageSource(redditArgs))

        self.wallpaperReplaceThread = ChangeWallpaperThread(self.imageSources,self.config)
        self.wallpaperReplaceThread.start()
        
        self.GUI = WallpaperChangerGUI(self)
        self.GUI.MainLoop()
        pass

    
    def handleExit(self):
        self.wallpaperReplaceThread.stop()

        configPath=Resources['CONFIG_YAML']
        shutil.copyfile(configPath,configPath+'.bak')
        with open(configPath,'wt') as f:
            yaml.dump(self.config,f,Dumper=yaml.SafeDumper,sort_keys=False)
        self.log.info(f'MainApp: saved config {configPath}')
        
        self.GUI.exitGUI()

def main():
    app = MainApp()
    pass



if __name__ == '__main__':
    main()