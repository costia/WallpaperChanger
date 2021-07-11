import wx
from GUI.taskBarIcon import TaskBarIcon
from GUI.wallpaperFrame import WallpaperFrame

class WallpaperChangerGUI(wx.App):
    def __init__(self,mainApp,sourceTypes):
        super(WallpaperChangerGUI, self).__init__()
        self.mainApp = mainApp
        self.sourceTypes = sourceTypes
        self.taskbar = TaskBarIcon(self)
        self.frame = WallpaperFrame(self,mainApp.config,sourceTypes)
        self.frame.Show(True)
    
    def handleExit(self):
        self.mainApp.handleExit()
    
    def exitGUI(self):
        self.taskbar.RemoveIcon()
        self.taskbar.Destroy()
        self.frame.Destroy()
        wx.CallAfter(self.Destroy)
    
    def configChanged(self):
        self.mainApp.configChanged()

    def setStatus(self,text,statusDict):
        self.frame.setStatus(text,statusDict)
        self.taskbar.setStatus(text,statusDict)
    
    def changeWallpaper(self):
        self.mainApp.changeWallpaper()
    
    def resetSources(self):
        self.mainApp.resetSources()
    
    def toggleShow(self):
        if self.frame.IsShown():
            self.frame.Show(False)
        else:
            self.frame.Show(True)
            if self.frame.IsIconized():
                self.frame.Iconize(False)
