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
    
    def toggleShow(self):
        if self.frame.IsShown():
            self.frame.Show(False)
        else:
            self.frame.Show(True)
            if self.frame.IsIconized():
                self.frame.Iconize(False)

    #
    # called from main
    #

    def exitGUI(self):
        self.taskbar.RemoveIcon()
        self.taskbar.Destroy()
        self.frame.Destroy()
        wx.CallAfter(self.Destroy)

    def setStatus(self,statusDict):
        self.frame.setStatus(statusDict)
        self.taskbar.setStatus(statusDict)
    
    #
    # main app callbacks
    #

    def configChanged(self):
        self.mainApp.configChanged()

    def handleExit(self):
        self.mainApp.handleExit()

    def changeWallpaper(self):
        self.mainApp.changeWallpaper()
    
    def resetSources(self):
        self.mainApp.resetSources()
    
    