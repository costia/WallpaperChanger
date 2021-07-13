import wx
import wx.adv
import logging
import copy

from resources import Resources
from GUI.common import createMenuItem
from ImageSources import getSourceTypes
from database import WallpaperDatabase


class WallpaperFrame(wx.Frame):
    def __init__(self,wxApp,config):
        super(WallpaperFrame, self).__init__(None, style= wx.CAPTION |	 wx.CLOSE_BOX | wx.MINIMIZE_BOX)
        self.SetTitle(Resources['APP_NAME'])
        self.SetIcon(wx.Icon(wx.Bitmap(Resources['ICON_PATH'])))

        self.db = WallpaperDatabase()
        
        self.windowWidth = 290
        self.panelHeight = 410
        self.windowHeight = self.panelHeight+30
        self.timeSelections = [{'name':'5min','value':5},
                                {'name':'10min','value':10},
                                {'name':'1h','value':60},
                                {'name':'4h','value':60*4},
                                {'name':'12h','value':60*12},
                                {'name':'24h','value':60*24}]
        
        self.minResolutionsSelections=[
            {'name':'720p','value':[1280,720]},
            {'name':'1080p','value':[1920,1080]},
            {'name':'1440p','value':[2560,1440]},
            {'name':'4K','value':[3840,2160]},
        ]

        self.sourceTypes = getSourceTypes()
        self.wallpaperRefreshTimeout = config['changePeriod']
        self.wallpaperMinResolution = config['minResolution']
        self.wxApp = wxApp
        self.log = logging.getLogger('WallpaperChanger')
        self.historyLength = 40

        self.popupmenu = wx.Menu()
        createMenuItem(self.popupmenu, 'Minimize',  lambda x: self.wxApp.toggleShow())
        createMenuItem(self.popupmenu, 'Exit',  lambda x: self.wxApp.notifyMain({'handleExit':True}))
        self.Bind(wx.EVT_CONTEXT_MENU, self._onShowPopup)
        
        self.Bind(wx.EVT_CLOSE, lambda x: self.wxApp.notifyMain({'handleExit':True}))
        self.Bind(wx.EVT_ICONIZE, self._onIconize)

        self.selectMainPanelBtn = wx.Button(self,-1,'Main',pos=(0,0),size=(self.windowWidth/2+5,30))
        self.selectHistoryPanelBtn = wx.Button(self,-1,'History',pos=(self.windowWidth/2+5,0),size=(self.windowWidth/2+10,30))
        
        self._buildMainPanel(40)
        self._buildHistoryPanel(40)

        self.changeNowButton.Bind(wx.EVT_BUTTON, lambda x: self.wxApp.notifyMain({'changeWallpaper':True}))

        self.selectMainPanelBtn.Bind(wx.EVT_BUTTON, self._showMainPanel)
        self.selectHistoryPanelBtn.Bind(wx.EVT_BUTTON, self._showHistoryPanel)

        self.timeSelect.Bind(wx.EVT_COMBOBOX, self._onTimeSelectChange)
        self.sourceAddButton.Bind(wx.EVT_BUTTON, self._addSource)
        self.sourceConfig.Bind(wx.EVT_TEXT_ENTER,self._addSource)
        self.sourceRemovButton.Bind(wx.EVT_BUTTON,self._removeSource)
        self.minResSelect.Bind(wx.EVT_COMBOBOX, self._onResolutionSelectChange)
        self.sourcesListbox.Bind(wx.EVT_LISTBOX,lambda x: self._sourceEditStatusChanged())

        self.baseFont = self.selectMainPanelBtn.GetFont()
        self.selectMainPanelBtn.SetFont(self.selectMainPanelBtn.GetFont().Bold())
        self.SetSize(size = (self.windowWidth+25,self.windowHeight))

    def _onIconize(self,event):
        if event.IsIconized():
            self.wxApp.toggleShow()
    
    def _sourceEditStatusChanged(self):
        if self.sourcesListbox.GetSelection()>=0 and not self.sourcesEditLocked:
            self.sourceRemovButton.Enable()
        else:
            self.sourceRemovButton.Disable()

        if self.sourcesEditLocked:
            self.sourceAddButton.Disable()
        else:
            self.sourceAddButton.Enable()

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
    
    def _updateHistoryList(self):
        names,links = self.db.getLatest(self.historyLength)
        self.historySources = links
        if len(names)>0:
            self.historListbox.SetItems(names)
            self.historListbox.SetSelection(0)

    def _buildHistoryPanel(self,nextY):
        startX = 5
        self.historyPanel = wx.Panel(self)
        self.historyPanel.SetSize(size = (self.windowWidth+25,self.panelHeight))
        self.historyPanel.SetPosition((0,0))

        self.historListbox = wx.ListBox(self.historyPanel,pos=(startX,nextY),size=(self.windowWidth,self.panelHeight-50))
        self._updateHistoryList()

        self.popupmenuHistory = wx.Menu()
        createMenuItem(self.popupmenuHistory, 'Copy selection source',  self._onCopySource)
        self.historListbox.Bind(wx.EVT_CONTEXT_MENU, self._onShowHistoryPopup)

        self.historyPanel.Show(False)

    def _onShowHistoryPopup(self,event):
        self.historyPanel.PopupMenu(self.popupmenuHistory,self.ScreenToClient(event.GetPosition()))

    def _onCopySource(self,event):
        id = self.historListbox.GetSelection()
        source = self.historySources[id]
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(source))
            wx.TheClipboard.Close()

    def _buildMainPanel(self,nextY):
        startX = 5
        self.mainPanel = wx.Panel(self)
        self.mainPanel.SetSize(size = (self.windowWidth+25,self.panelHeight))
        self.mainPanel.SetPosition((0,0))

        self.labelRefresh = wx.StaticText(self.mainPanel,label = "Wallpaper refresh delay:" ,pos=(startX,nextY+2),style = wx.ALIGN_LEFT) 
        textSize = self.labelRefresh.GetSize()[0] +10
        self.timeSelect = wx.ComboBox(self.mainPanel,pos=(startX+textSize,nextY),size=(self.windowWidth-textSize,30),style=wx.CB_DROPDOWN|wx.CB_READONLY,choices=[x['name'] for x in self.timeSelections])
        self.timeSelect.SetSelection(self._getCurrentTimeSelectID())
        nextY += self.timeSelect.GetSize()[1]+3
        self.changeNowButton = wx.Button(self.mainPanel,-1,'Change now',pos=(startX,nextY),size=(self.windowWidth,25))
        nextY += 50

        self.labelSources = wx.StaticText(self.mainPanel,label = "Wallpaper sources:" ,pos=(startX,nextY+2),style = wx.ALIGN_LEFT) 
        nextY += 20
        self.sourcesListbox = wx.ListBox(self.mainPanel,pos=(startX,nextY),size=(self.windowWidth,100))
        nextY += 105
        textSize = self.labelSources.GetSize()[0] +10
        self.sourceTypeSelect= wx.ComboBox(self.mainPanel,pos=(startX,nextY),size=(100,30),style=wx.CB_DROPDOWN|wx.CB_READONLY,
            choices=self.sourceTypes)
        self.sourceTypeSelect.SetSelection(0)
        self.sourceConfig = wx.TextCtrl(self.mainPanel,pos=(startX+100,nextY),size=(self.windowWidth-100,20),style = wx.TE_PROCESS_ENTER)
        nextY += 20
        self.sourceAddButton = wx.Button(self.mainPanel,-1,'Add new source',pos=(startX,nextY),size=(self.windowWidth/2,25))
        self.sourceRemovButton = wx.Button(self.mainPanel,-1,'Remove source',pos=(startX+self.windowWidth/2,nextY),size=(self.windowWidth/2,25))
        nextY += 30
        self.sourceAddButton.Disable()
        self.sourceRemovButton.Disable()
        self.sourcesEditLocked = True
        

        nextY += 20
        self.labelResolution= wx.StaticText(self.mainPanel,label = "Minimal resolution:" ,pos=(startX,nextY+2),style = wx.ALIGN_LEFT) 
        textSize = self.labelResolution.GetSize()[0] +10
        self.minResSelect = wx.ComboBox(self.mainPanel,pos=(startX+textSize,nextY),size=(self.windowWidth-textSize,30),style=wx.CB_DROPDOWN|wx.CB_READONLY,
            choices=[x['name'] for x in self.minResolutionsSelections])
        self.minResSelect.SetSelection(self._getCurrentMinResolutionSelectID())
        nextY += 30

        nextY += 20

        self.labelStatus = wx.TextCtrl(self.mainPanel,pos=(startX,nextY),size=(self.windowWidth,40),style = wx.TE_READONLY| wx.TE_MULTILINE| wx.TE_NO_VSCROLL ) 
        self.labelStatus.SetLabelText('Initializing...')
        self.labelStatus.SetBackgroundColour((173,173,173))
        nextY += 30

    
    def _updateSourcesList(self):
        sourcesListStrings = [ x.getTypeName()+':'+x.getName() for x in self.imageSources]
        self.sourcesListbox.SetItems(sourcesListStrings)

    def _removeSource(self,event):
        selectedSourceID = self.sourcesListbox.GetSelection()
        if selectedSourceID>=0:
            self.wxApp.notifyMain({'removeSource':selectedSourceID})

    def _addSource(self,event):
        sourceType = self.sourceTypeSelect.GetStringSelection()
        sourceConfig = self.sourceConfig.GetValue()
        if sourceConfig:
            sourceDict={
                'type':sourceType,
                'config':sourceConfig
            }
            self.wxApp.notifyMain({'addSource':sourceDict})
    
    def _onTimeSelectChange(self,event):
        selected = self.timeSelect.GetSelection()
        selectedPeriod = self.timeSelections[selected]['value']
        self.wxApp.notifyMain({'setRefreshTimeout':selectedPeriod})
        self.wallpaperRefreshTimeout = selectedPeriod
        self.log.info(f'GUI_WallpaperFrame: wallpaper refresh time changed to {selectedPeriod}')

    def _onResolutionSelectChange(self,event):
        selected = self.minResSelect.GetSelection()
        selectedResolution = self.minResolutionsSelections[selected]['value']
        self.wxApp.notifyMain({'setMinResolution':selectedResolution})
        self.wallpaperMinResolution = selectedResolution
        self.log.info(f'GUI_WallpaperFrame: wallpaper min resolution changed to {str(selectedResolution)}')

    def _onShowPopup(self,event):
        self.PopupMenu(self.popupmenu,self.ScreenToClient(event.GetPosition()))

    def _getCurrentTimeSelectID(self):
        currentSelection=self.wallpaperRefreshTimeout

        selectedItem = -1
        for ind,x in enumerate(self.timeSelections):
            if x['value']==currentSelection:
                selectedItem = ind
                break
        
        if selectedItem<0:
            selectedItem=1
            currentSelection = self.timeSelections[selectedItem]['value']
            # call after will delay execution untill main's ctor is done
            # otherwise change wallpaper instance doesnt exist yet
            wx.CallAfter(self.wxApp.notifyMain,{'setRefreshTimeout':currentSelection})
            self.wallpaperRefreshTimeout = currentSelection

        return selectedItem
    
    def _getCurrentMinResolutionSelectID(self):
        currentSelection=self.wallpaperMinResolution

        selectedItem = -1
        for ind,x in enumerate(self.minResolutionsSelections):
            if x['value'][0]==currentSelection[0] and x['value'][1]==currentSelection[1]:
                selectedItem = ind
                break
        
        if selectedItem<0:
            selectedItem=0
            currentSelection = self.minResolutionsSelections[selectedItem]['value']
            # call after will delay execution untill main's ctor is done
            # otherwise change wallpaper instance doesnt exist yet
            wx.CallAfter(self.wxApp.notifyMain,{'setMinResolution':currentSelection})
            self.wallpaperMinResolution = currentSelection

        return selectedItem

        
    
    #
    # called by App
    #

    def notifyGUI(self,argsDict):
        if 'status' in argsDict:
            self.labelStatus.SetValue(argsDict['status'])
            self.labelStatus.Update()
        if 'blockWallpaperChange' in argsDict:
            if argsDict['blockWallpaperChange']:
                self.changeNowButton.Disable()
            else:
                self.changeNowButton.Enable()
        if 'updateHistory' in argsDict and argsDict['updateHistory']:      
            self._updateHistoryList()
        if 'imageSources' in argsDict:
            self.imageSources = argsDict['imageSources']
            self._updateSourcesList()
        if 'lockSourceEdit' in argsDict:
            if argsDict['lockSourceEdit']:
                self.sourcesEditLocked = True
            else:
                self.sourcesEditLocked = False
            self._sourceEditStatusChanged()
