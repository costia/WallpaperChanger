import wx
import wx.adv
import logging
import copy

from resources import Resources
from GUI.common import createMenuItem
from ImageSources import getSourceTypes
from database import WallpaperDatabase


class MainPanel(wx.Panel):
    def __init__(self,frame,config,windowWidth):
        super(MainPanel, self).__init__(frame)
        self.windowWidth = windowWidth

        self.sourceTypes = getSourceTypes()
        self.wallpaperRefreshTimeout = config['changePeriod']
        self.wallpaperMinResolution = config['minResolution']
        self.log = logging.getLogger('WallpaperChanger')
        self.parentFrame = frame

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

        startX = 5
        nextY = 5

        self.labelRefresh = wx.StaticText(self,label = "Wallpaper refresh delay:" ,pos=(startX,nextY+2),style = wx.ALIGN_LEFT) 
        textSize = self.labelRefresh.GetSize()[0] +10
        self.timeSelect = wx.ComboBox(self,pos=(startX+textSize,nextY),size=(self.windowWidth-textSize,30),style=wx.CB_DROPDOWN|wx.CB_READONLY,choices=[x['name'] for x in self.timeSelections])
        self.timeSelect.SetSelection(self._getCurrentTimeSelectID())
        nextY += self.timeSelect.GetSize()[1]+3
        self.changeNowButton = wx.Button(self,-1,'Change now',pos=(startX,nextY),size=(self.windowWidth,25))
        nextY += 50

        self.labelSources = wx.StaticText(self,label = "Wallpaper sources:" ,pos=(startX,nextY+2),style = wx.ALIGN_LEFT) 
        nextY += 20
        self.sourcesListbox = wx.ListBox(self,pos=(startX,nextY),size=(self.windowWidth,100))
        nextY += 105
        textSize = self.labelSources.GetSize()[0] +10
        self.sourceTypeSelect= wx.ComboBox(self,pos=(startX,nextY),size=(100,30),style=wx.CB_DROPDOWN|wx.CB_READONLY,
            choices=self.sourceTypes)
        self.sourceTypeSelect.SetSelection(0)
        self.sourceConfig = wx.TextCtrl(self,pos=(startX+100,nextY),size=(self.windowWidth-100,20),style = wx.TE_PROCESS_ENTER)
        nextY += 20
        self.sourceAddButton = wx.Button(self,-1,'Add new source',pos=(startX,nextY),size=(self.windowWidth/2,25))
        self.sourceRemovButton = wx.Button(self,-1,'Remove source',pos=(startX+self.windowWidth/2,nextY),size=(self.windowWidth/2,25))
        nextY += 30
        self.sourceAddButton.Disable()
        self.sourceRemovButton.Disable()
        self.sourcesEditLocked = True

        nextY += 20
        self.labelResolution= wx.StaticText(self,label = "Minimal resolution:" ,pos=(startX,nextY+2),style = wx.ALIGN_LEFT) 
        textSize = self.labelResolution.GetSize()[0] +10
        self.minResSelect = wx.ComboBox(self,pos=(startX+textSize,nextY),size=(self.windowWidth-textSize,30),style=wx.CB_DROPDOWN|wx.CB_READONLY,
            choices=[x['name'] for x in self.minResolutionsSelections])
        self.minResSelect.SetSelection(self._getCurrentMinResolutionSelectID())
        nextY += 30

        nextY += 20

        self.labelStatus = wx.TextCtrl(self,pos=(startX,nextY),size=(self.windowWidth,40),style = wx.TE_READONLY| wx.TE_MULTILINE| wx.TE_NO_VSCROLL ) 
        self.labelStatus.SetLabelText('Initializing...')
        self.labelStatus.SetBackgroundColour((173,173,173))
        nextY += 30

        self.changeNowButton.Bind(wx.EVT_BUTTON, lambda x: self.parentFrame.notifyMain({'changeWallpaper':True}))
        self.timeSelect.Bind(wx.EVT_COMBOBOX, self._onTimeSelectChange)
        self.sourceAddButton.Bind(wx.EVT_BUTTON, self._addSource)
        self.sourceConfig.Bind(wx.EVT_TEXT_ENTER,self._addSource)
        self.sourceRemovButton.Bind(wx.EVT_BUTTON,self._removeSource)
        self.minResSelect.Bind(wx.EVT_COMBOBOX, self._onResolutionSelectChange)
        self.sourcesListbox.Bind(wx.EVT_LISTBOX,lambda x: self._sourceEditStatusChanged())

    def _sourceEditStatusChanged(self):
        if self.sourcesListbox.GetSelection()>=0 and not self.sourcesEditLocked:
            self.sourceRemovButton.Enable()
        else:
            self.sourceRemovButton.Disable()

        if self.sourcesEditLocked:
            self.sourceAddButton.Disable()
        else:
            self.sourceAddButton.Enable()

    def _updateSourcesList(self):
        sourcesListStrings = [ x.getTypeName()+':'+x.getName() for x in self.imageSources]
        self.sourcesListbox.SetItems(sourcesListStrings)

    def _removeSource(self,event):
        selectedSourceID = self.sourcesListbox.GetSelection()
        if selectedSourceID>=0:
            self.parentFrame.notifyMain({'removeSource':selectedSourceID})

    def _addSource(self,event):
        sourceType = self.sourceTypeSelect.GetStringSelection()
        sourceConfig = self.sourceConfig.GetValue()
        if sourceConfig:
            sourceDict={
                'type':sourceType,
                'config':sourceConfig
            }
            self.parentFrame.notifyMain({'addSource':sourceDict})
    
    def _onTimeSelectChange(self,event):
        selected = self.timeSelect.GetSelection()
        selectedPeriod = self.timeSelections[selected]['value']
        self.parentFrame.notifyMain({'setRefreshTimeout':selectedPeriod})
        self.wallpaperRefreshTimeout = selectedPeriod
        self.log.info(f'GUI_WallpaperFrame: wallpaper refresh time changed to {selectedPeriod}')

    def _onResolutionSelectChange(self,event):
        selected = self.minResSelect.GetSelection()
        selectedResolution = self.minResolutionsSelections[selected]['value']
        self.parentFrame.notifyMain({'setMinResolution':selectedResolution})
        self.wallpaperMinResolution = selectedResolution
        self.log.info(f'GUI_WallpaperFrame: wallpaper min resolution changed to {str(selectedResolution)}')

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
            wx.CallAfter(self.parentFrame.notifyMain,{'setRefreshTimeout':currentSelection})
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
            wx.CallAfter(self.parentFrame.notifyMain,{'setMinResolution':currentSelection})
            self.wallpaperMinResolution = currentSelection

        return selectedItem

    def notifyGUI(self,argsDict):
        if 'status' in argsDict:
            self.labelStatus.SetValue(argsDict['status'])
            self.labelStatus.Update()
        if 'blockWallpaperChange' in argsDict:
            if argsDict['blockWallpaperChange']:
                self.changeNowButton.Disable()
            else:
                self.changeNowButton.Enable()
        if 'imageSources' in argsDict:
            self.imageSources = argsDict['imageSources']
            self._updateSourcesList()
        if 'lockSourceEdit' in argsDict:
            if argsDict['lockSourceEdit']:
                self.sourcesEditLocked = True
            else:
                self.sourcesEditLocked = False
            self._sourceEditStatusChanged()
