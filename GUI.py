import wx
import wx.adv
from resources import Resources
import logging


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
        self.SetIcon(icon, Resources['APP_NAME'])
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, lambda x: self.wxApp.toggleShow())

    def CreatePopupMenu(self):
        menu = wx.Menu()
        createMenuItem(menu, 'Change now',  lambda x: self.wxApp.changeWallpaper())
        createMenuItem(menu, 'Exit',  lambda x: self.wxApp.handleExit())
        return menu


class WallpaperFrame(wx.Frame):
    def __init__(self,wxApp,config,sourceTypes):
        windowWidth = 300
        startX = 5

        super(WallpaperFrame, self).__init__(None, style= wx.CAPTION |	 wx.CLOSE_BOX | wx.MINIMIZE_BOX)
        self.SetTitle(Resources['APP_NAME'])
        self.SetIcon(wx.Icon(wx.Bitmap(Resources['ICON_PATH'])))
        
        self.sourceTypes = sourceTypes
        self.config = config
        self.wxApp = wxApp
        self.log = logging.getLogger('WallpaperChanger')

        self.popupmenu = wx.Menu()
        createMenuItem(self.popupmenu, 'Minimize',  lambda x: self.wxApp.toggleShow())
        createMenuItem(self.popupmenu, 'Exit',  lambda x: self.wxApp.handleExit())
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)
        
        self.Bind(wx.EVT_CLOSE, lambda x: self.wxApp.handleExit())
        self.Bind(wx.EVT_ICONIZE, lambda x: self.wxApp.toggleShow())

        self.timeSelections = {'5min':5,'10min':10,'30min':30,'1h':60,'4h':60*4,'12h':60*12,'24h':60*24}
        
        nextY = 10
        
        self.labelRefresh = wx.StaticText(self,label = "Wallpaper refresh delay:" ,pos=(startX,nextY),style = wx.ALIGN_LEFT) 
        nextY += 20

        self.timeSelect = wx.ComboBox(self,pos=(startX,nextY),size=(windowWidth,30),style=wx.CB_DROPDOWN|wx.CB_READONLY,choices=[x for x in self.timeSelections])
        self.timeSelect.SetSelection(self._getCurrentTimeSelectID())
        self.timeSelect.Bind(wx.EVT_COMBOBOX, self.onTimeSelectChange)
        nextY += 30
        self.changeNowButton = wx.Button(self,-1,'Change now',pos=(startX,nextY),size=(windowWidth,20))
        self.changeNowButton.Bind(wx.EVT_BUTTON, lambda x: self.wxApp.changeWallpaper())
        nextY += 30

        nextY += 20
        self.labelSources = wx.StaticText(self,label = "Wallpaper sources:" ,pos=(startX,nextY),style = wx.ALIGN_LEFT) 
        nextY += 20
        self.sourceTypeSelect= wx.ComboBox(self,pos=(startX,nextY),size=(windowWidth,30),style=wx.CB_DROPDOWN|wx.CB_READONLY,choices=self.sourceTypes)
        self.sourceTypeSelect.SetSelection(0)
        nextY += 25
        self.sourceConfig = wx.TextCtrl(self,pos=(startX,nextY),size=(windowWidth,20))
        nextY += 20
        self.sourceAddButton = wx.Button(self,-1,'Add new source',pos=(startX,nextY),size=(windowWidth,20))
        nextY += 30

        sourcesListStrings = [ x['type']+':'+x['config'] for x in self.config['sources']]
        self.sourcesListbox = wx.ListBox(self,pos=(startX,nextY),size=(windowWidth,100),style=wx.CB_DROPDOWN|wx.CB_READONLY,choices=sourcesListStrings)
        self.sourcesListbox.SetSelection(0)
        nextY += 100
        self.sourceRemovButton = wx.Button(self,-1,'Remove source',pos=(startX,nextY),size=(windowWidth,20))
        nextY += 30

        nextY += 20
        self.minimizeButton = wx.Button(self,-1,'Minimize to tray',pos=(startX,nextY),size=(windowWidth,30))
        self.minimizeButton.Bind(wx.EVT_BUTTON, lambda x: self.wxApp.toggleShow())
        nextY += 50

        self.labelStatus = wx.TextCtrl(self,pos=(startX,nextY),size=(windowWidth,40),style = wx.TE_READONLY| wx.TE_MULTILINE| wx.TE_NO_VSCROLL ) 
        self.labelStatus.SetLabelText('Status')
        self.labelStatus.SetBackgroundColour((173,173,173))
        nextY += 30

        self.sourceAddButton.Disable()
        self.sourceRemovButton.Disable()
        self.SetSize(size = (windowWidth+25,nextY+50))
        
    def setStatus(self,text,statusDict):
        self.labelStatus.SetValue(text)
        self.labelStatus.Update()
        if 'blockChange' in statusDict:
            if statusDict['blockChange']:
                self.changeNowButton.Disable()
            else:
                self.changeNowButton.Enable()
    
    def onTimeSelectChange(self,event):
        selected = self.timeSelect.GetValue()
        selectedPeriod = self.timeSelections[selected]
        self.config['changePeriod'] = selectedPeriod
        self.log.info(f'GUI_WallpaperFrame: wallpaper refresh time changed to {selectedPeriod}')
        
    def OnShowPopup(self,event):
        self.PopupMenu(self.popupmenu,self.ScreenToClient(event.GetPosition()))

    def _getCurrentTimeSelectID(self):
        currentSelection=self.config['changePeriod']
        timesInMinutes = [self.timeSelections[x] for x in self.timeSelections]
        if currentSelection>timesInMinutes[-1]:
            currentSelection=timesInMinutes[-1]
        else:
            ind = 0
            while timesInMinutes[ind]<currentSelection:
                ind +=1
            currentSelection = timesInMinutes[ind]
        self.config['changePeriod'] = currentSelection
        selectedItem = 0
        for x in self.timeSelections:
            if self.timeSelections[x]==currentSelection:
                break
            selectedItem +=1
        return selectedItem

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
    
    def setStatus(self,text,statusDict):
        self.frame.setStatus(text,statusDict)
    
    def changeWallpaper(self):
        self.mainApp.changeWallpaper()
    
    def toggleShow(self):
        if self.frame.IsShown():
            self.frame.Show(False)
        else:
            self.frame.Show(True)
            if self.frame.IsIconized():
                self.frame.Iconize(False)


