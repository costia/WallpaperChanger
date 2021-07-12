import wx
import wx.adv
from resources import Resources
from GUI.common import createMenuItem

class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self,wxApp):
        super(TaskBarIcon, self).__init__()
        self.wxApp = wxApp
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        
        self.icon = wx.Icon(wx.Bitmap(Resources['ICON_PATH']))
        self.SetIcon(self.icon, Resources['APP_NAME'])
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, lambda x: self.wxApp.toggleShow())
    
    # called by wx
    def CreatePopupMenu(self):
        menu = wx.Menu()
        createMenuItem(menu, 'Change now',  lambda x: self.wxApp.changeWallpaper())
        createMenuItem(menu, 'Exit',  lambda x: self.wxApp.handleExit())
        return menu
    
    #
    # called by App
    #
    def notifyGUI(self,statusDict):
        if 'status' in statusDict:
            self.SetIcon(self.icon, statusDict['status'])