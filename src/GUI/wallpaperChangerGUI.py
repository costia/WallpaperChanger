import wx
from GUI.taskBarIcon import TaskBarIcon
from GUI.wallpaperFrame import WallpaperFrame

class WallpaperChangerGUI(wx.App):
    def __init__(self,mainApp):
        super(WallpaperChangerGUI, self).__init__()
        self.mainApp = mainApp
        self.taskbar = TaskBarIcon(self)
        self.frame = WallpaperFrame(self,mainApp.config)
        self.frame.Show(True)
    
    def _exitGUI(self):
        self.taskbar.RemoveIcon()
        self.taskbar.Destroy()
        self.frame.Destroy()
        wx.CallAfter(self.Destroy)

    #
    # called from frame or taskbar icon
    #
    def toggleShow(self):
        if self.frame.IsShown():
            self.frame.Show(False)
        else:
            self.frame.Show(True)
            if self.frame.IsIconized():
                self.frame.Iconize(False)
            self.frame.Raise()

    #
    # called from main
    #
    def notifyGUI(self,statusDict):
        if 'exitGUI' in statusDict and statusDict['exitGUI']:
            self._exitGUI()
        else:
            self.frame.notifyGUI(statusDict)
            self.taskbar.notifyGUI(statusDict)
    
    #
    # main app callbacks
    #

    def handleExit(self):
        self.mainApp.handleExit()

    def changeWallpaper(self):
        self.mainApp.changeWallpaper()
    
    def removeSource(self,index):
        self.mainApp.removeSource(index)

    def addSource(self,sourceDict):
        self.mainApp.addSource(sourceDict)
    
    def setRefreshTimeout(self,timeout):
        self.mainApp.setRefreshTimeout(timeout)
    
    
    