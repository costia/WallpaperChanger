import wx
import wx.adv
import logging
from resources import Resources
from GUI.common import createMenuItem
from ImageSources import getSourceTypes

class WallpaperFrame(wx.Frame):
    def __init__(self,wxApp,config):
        super(WallpaperFrame, self).__init__(None, style= wx.CAPTION |	 wx.CLOSE_BOX | wx.MINIMIZE_BOX)
        self.SetTitle(Resources['APP_NAME'])
        self.SetIcon(wx.Icon(wx.Bitmap(Resources['ICON_PATH'])))
        
        self.windowWidth = 300
        self.windowHeight = 490+30
        self.panelHeight = 490
        self.timeSelections = {'5min':5,'10min':10,'30min':30,'1h':60,'4h':60*4,'12h':60*12,'24h':60*24}

        self.sourceTypes = getSourceTypes()
        self.config = config
        self.wxApp = wxApp
        self.log = logging.getLogger('WallpaperChanger')

        

        self.popupmenu = wx.Menu()
        createMenuItem(self.popupmenu, 'Minimize',  lambda x: self.wxApp.toggleShow())
        createMenuItem(self.popupmenu, 'Exit',  lambda x: self.wxApp.handleExit())
        self.Bind(wx.EVT_CONTEXT_MENU, self._onShowPopup)
        
        self.Bind(wx.EVT_CLOSE, lambda x: self.wxApp.handleExit())
        self.Bind(wx.EVT_ICONIZE, lambda x: self.wxApp.toggleShow())

        self.selectMainPanelBtn = wx.Button(self,-1,'Main',pos=(0,0),size=(self.windowWidth/2+5,30))
        self.selectHistoryPanelBtn = wx.Button(self,-1,'History',pos=(self.windowWidth/2+5,0),size=(self.windowWidth/2+10,30))
        
        self._buildMainPanel(40)
        self._buildHistoryPanel(40)

        self.changeNowButton.Bind(wx.EVT_BUTTON, lambda x: self.wxApp.changeWallpaper())

        self.selectMainPanelBtn.Bind(wx.EVT_BUTTON, self._showMainPanel)
        self.selectHistoryPanelBtn.Bind(wx.EVT_BUTTON, self._showHistoryPanel)

        self.timeSelect.Bind(wx.EVT_COMBOBOX, self._onTimeSelectChange)
        self.minimizeButton.Bind(wx.EVT_BUTTON, lambda x: self.wxApp.toggleShow())
        self.sourceAddButton.Bind(wx.EVT_BUTTON, self._addSource)
        self.sourceConfig.Bind(wx.EVT_TEXT_ENTER,self._addSource)
        self.sourceRemovButton.Bind(wx.EVT_BUTTON,self._removeSource)

        self.baseFont = self.selectMainPanelBtn.GetFont()
        self.selectMainPanelBtn.SetFont(self.selectMainPanelBtn.GetFont().Bold())
        self.SetSize(size = (self.windowWidth+25,self.windowHeight))

    def _showHistoryPanel(self,event):
        self.historyPanel.Show(True)
        self.mainPanel.Show(False)
        self.selectMainPanelBtn.SetFont(self.baseFont)
        self.selectHistoryPanelBtn.SetFont(self.baseFont.Bold())
    
    def _showMainPanel(self,event):
        self.historyPanel.Show(False)
        self.mainPanel.Show(True)
        self.selectMainPanelBtn.SetFont(self.baseFont.Bold())
        self.selectHistoryPanelBtn.SetFont(self.baseFont)
    

    def _buildHistoryPanel(self,nextY):
        startX = 5
        self.historyPanel = wx.Panel(self)
        self.historyPanel.SetSize(size = (self.windowWidth+25,self.panelHeight))
        self.historyPanel.SetPosition((0,0))

        self.historListbox = wx.ListBox(self.historyPanel,pos=(startX,nextY),size=(self.windowWidth,self.windowHeight-40),style=wx.CB_READONLY)


        self.historyPanel.Show(False)

    def _buildMainPanel(self,nextY):
        startX = 5
        self.mainPanel = wx.Panel(self)
        self.mainPanel.SetSize(size = (self.windowWidth+25,self.panelHeight))
        self.mainPanel.SetPosition((0,0))

        self.labelRefresh = wx.StaticText(self.mainPanel,label = "Wallpaper refresh delay:" ,pos=(startX,nextY),style = wx.ALIGN_LEFT) 
        nextY += 20

        self.timeSelect = wx.ComboBox(self.mainPanel,pos=(startX,nextY),size=(self.windowWidth,30),style=wx.CB_DROPDOWN|wx.CB_READONLY,choices=[x for x in self.timeSelections])
        self.timeSelect.SetSelection(self._getCurrentTimeSelectID())
        nextY += 30
        self.changeNowButton = wx.Button(self.mainPanel,-1,'Change now',pos=(startX,nextY),size=(self.windowWidth,20))
        nextY += 30

        nextY += 20
        self.labelSources = wx.StaticText(self.mainPanel,label = "Wallpaper sources:" ,pos=(startX,nextY),style = wx.ALIGN_LEFT) 
        nextY += 20
        self.sourceTypeSelect= wx.ComboBox(self.mainPanel,pos=(startX,nextY),size=(self.windowWidth,30),style=wx.CB_DROPDOWN|wx.CB_READONLY,choices=self.sourceTypes)
        self.sourceTypeSelect.SetSelection(0)
        nextY += 25
        self.sourceConfig = wx.TextCtrl(self.mainPanel,pos=(startX,nextY),size=(self.windowWidth,20),style = wx.TE_PROCESS_ENTER)
        nextY += 20
        self.sourceAddButton = wx.Button(self.mainPanel,-1,'Add new source',pos=(startX,nextY),size=(self.windowWidth,20))
        nextY += 30

        self.sourcesListbox = wx.ListBox(self.mainPanel,pos=(startX,nextY),size=(self.windowWidth,100),style=wx.CB_DROPDOWN|wx.CB_READONLY)
        self._updateSourcesList()
        nextY += 100
        self.sourceRemovButton = wx.Button(self.mainPanel,-1,'Remove source',pos=(startX,nextY),size=(self.windowWidth,20))
        nextY += 30

        nextY += 20
        self.minimizeButton = wx.Button(self.mainPanel,-1,'Minimize to tray',pos=(startX,nextY),size=(self.windowWidth,30))
        nextY += 50

        self.labelStatus = wx.TextCtrl(self.mainPanel,pos=(startX,nextY),size=(self.windowWidth,40),style = wx.TE_READONLY| wx.TE_MULTILINE| wx.TE_NO_VSCROLL ) 
        self.labelStatus.SetLabelText('Status')
        self.labelStatus.SetBackgroundColour((173,173,173))
        nextY += 30

    
    def _updateSourcesList(self):
        sourcesListStrings = [ x['type']+':'+str(x['config']) for x in self.config['sources']]
        self.sourcesListbox.SetItems(sourcesListStrings)
        self.sourcesListbox.SetSelection(0)

    def _removeSource(self,event):
        selectedSource = self.sourcesListbox.GetStringSelection()
        splitLocation = selectedSource.find(':')
        sourceType = selectedSource[0:splitLocation]
        sourceConfig = selectedSource[splitLocation+1:]
        newList=[]
        itemRemoved=False
        for src in self.config['sources']:
            if src['type']==sourceType and str(src['config'])==sourceConfig:
                itemRemoved = True
            else:
                newList.append(src)
        
        if itemRemoved:
            self.config['sources']=newList
            self._updateSourcesList()

            self.configChanged()
            self.resetSources()


    def _addSource(self,event):
        sourceType = self.sourceTypeSelect.GetStringSelection()
        sourceConfig = self.sourceConfig.GetValue()
        if sourceConfig:
            sourceDict={
                'type':sourceType,
                'config':sourceConfig
            }
            self.config['sources'].append(sourceDict)
            self._updateSourcesList()
            
            self.configChanged()
            self.resetSources()
    
    def _onTimeSelectChange(self,event):
        selected = self.timeSelect.GetValue()
        selectedPeriod = self.timeSelections[selected]
        self.config['changePeriod'] = selectedPeriod
        self.configChanged()
        self.log.info(f'GUI_WallpaperFrame: wallpaper refresh time changed to {selectedPeriod}')

    def _onShowPopup(self,event):
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
    
    
    #
    # called by App
    #

    def setStatus(self,text,statusDict):
        self.labelStatus.SetValue(text)
        self.labelStatus.Update()
        if 'blockChange' in statusDict:
            if statusDict['blockChange']:
                self.changeNowButton.Disable()
            else:
                self.changeNowButton.Enable()

    #
    # App callbacks
    #

    def resetSources(self):
        self.wxApp.resetSources()

    def configChanged(self):
        self.wxApp.configChanged()