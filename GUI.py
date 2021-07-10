import wx
import wx.adv
import sys

TRAY_TOOLTIP = 'Wallpaper changer'
ICON_PATH = 'resources/icon.png'

def createMenuItem(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.Append(item)
    return item


class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self,app):
        super(TaskBarIcon, self).__init__()
        self.app = app
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        if hasattr(sys,'_MEIPASS'):
            iconPath = sys._MEIPASS+'/'+ICON_PATH
        else:
            iconPath = ICON_PATH
        icon = wx.Icon(wx.Bitmap(iconPath))
        self.SetIcon(icon, TRAY_TOOLTIP)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, lambda x: self.app.toggleShow())

    def CreatePopupMenu(self):
        menu = wx.Menu()
        createMenuItem(menu, 'Exit',  lambda x: self.app.handleExit())
        return menu


class WallpaperFrame(wx.Frame):
    def __init__(self,app):
        super(WallpaperFrame, self).__init__(None, style= wx.CAPTION |	 wx.CLOSE_BOX | wx.MINIMIZE_BOX)
        self.app = app
        self.popupmenu = wx.Menu()
        createMenuItem(self.popupmenu, 'Minimize',  lambda x: self.app.toggleShow())
        createMenuItem(self.popupmenu, 'Exit',  lambda x: self.app.handleExit())
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)
        
        self.Bind(wx.EVT_CLOSE, lambda x: self.app.handleExit())
        self.Bind(wx.EVT_ICONIZE, lambda x: self.app.toggleShow())
        
    
    def OnShowPopup(self,event):
        self.PopupMenu(self.popupmenu,self.ScreenToClient(event.GetPosition()))

class WallpaperChangerGUI(wx.App):
    def __init__(self,mainApp):
        super(WallpaperChangerGUI, self).__init__()
        self.mainApp = mainApp
        self.taskbar = TaskBarIcon(self)
        self.frame = WallpaperFrame(self)
        self.frame.Show(True)
    
    def handleExit(self):
        self.mainApp.handleExit()
    
    def exitGUI(self):
        self.taskbar.RemoveIcon()
        self.taskbar.Destroy()
        self.frame.Destroy()
        wx.CallAfter(self.Destroy)
    
    def toggleShow(self):
        if self.frame.IsShown():
            self.frame.Show(False)
        else:
            self.frame.Show(True)
            if self.frame.IsIconized():
                self.frame.Iconize(False)


