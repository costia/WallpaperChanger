import wx
import wx.adv
from resources import Resources



def createMenuItem(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.Append(item)
    return item


class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self,wxApp):
        super(TaskBarIcon, self).__init__()
        self.wxApp = wxApp
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        
        icon = wx.Icon(wx.Bitmap(Resources['ICON_PATH']))
        self.SetIcon(icon, Resources['TRAY_TOOLTIP'])
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, lambda x: self.wxApp.toggleShow())

    def CreatePopupMenu(self):
        menu = wx.Menu()
        createMenuItem(menu, 'Exit',  lambda x: self.wxApp.handleExit())
        return menu


class WallpaperFrame(wx.Frame):
    def __init__(self,wxApp,config):
        super(WallpaperFrame, self).__init__(None, style= wx.CAPTION |	 wx.CLOSE_BOX | wx.MINIMIZE_BOX)
        self.config = config
        self.wxApp = wxApp
        self.popupmenu = wx.Menu()
        createMenuItem(self.popupmenu, 'Minimize',  lambda x: self.wxApp.toggleShow())
        createMenuItem(self.popupmenu, 'Exit',  lambda x: self.wxApp.handleExit())
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)
        
        self.Bind(wx.EVT_CLOSE, lambda x: self.wxApp.handleExit())
        self.Bind(wx.EVT_ICONIZE, lambda x: self.wxApp.toggleShow())
        
    def OnShowPopup(self,event):
        self.PopupMenu(self.popupmenu,self.ScreenToClient(event.GetPosition()))

class WallpaperChangerGUI(wx.App):
    def __init__(self,mainApp):
        super(WallpaperChangerGUI, self).__init__()
        self.mainApp = mainApp
        self.taskbar = TaskBarIcon(self)
        self.frame = WallpaperFrame(self,mainApp.config)
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


