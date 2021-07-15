import wx
import wx.adv
import logging
import copy

from resources import Resources
from GUI.common import createMenuItem
from database import WallpaperDatabase

from GUI.mainPanel import MainPanel

class WallpaperFrame(wx.Frame):
    def __init__(self,wxApp,config):
        super(WallpaperFrame, self).__init__(None, style= wx.CAPTION |	 wx.CLOSE_BOX | wx.MINIMIZE_BOX)
        self.SetTitle(Resources['APP_NAME'])
        self.SetIcon(wx.Icon(wx.Bitmap(Resources['ICON_PATH'])))

        self.db = WallpaperDatabase()
        
        self.windowWidth = 290
        self.panelHeight = 405
        self.windowHeight = self.panelHeight

        self.wxApp = wxApp
        self.log = logging.getLogger('WallpaperChanger')
        self.historyLength = 40
        
        self.Bind(wx.EVT_CLOSE, lambda x: self.wxApp.notifyMain({'handleExit':True}))
        self.Bind(wx.EVT_ICONIZE, self._onIconize)

        self.selectMainPanelBtn = wx.Button(self,-1,'Main',pos=(0,0),size=(self.windowWidth/2+5,30))
        self.selectHistoryPanelBtn = wx.Button(self,-1,'History',pos=(self.windowWidth/2+5,0),size=(self.windowWidth/2+5,30))
        
        self.mainPanel = MainPanel(self,config,self.windowWidth)
        self.mainPanel.SetSize(size = (self.windowWidth+25,self.panelHeight-30))
        self.mainPanel.SetPosition((0,30))

        self._buildHistoryPanel(40)

        self.selectMainPanelBtn.Bind(wx.EVT_BUTTON, self._showMainPanel)
        self.selectHistoryPanelBtn.Bind(wx.EVT_BUTTON, self._showHistoryPanel)

        self.baseFont = self.selectMainPanelBtn.GetFont()
        self.selectMainPanelBtn.SetFont(self.selectMainPanelBtn.GetFont().Bold())
        self.SetClientSize(size = (self.windowWidth+10,self.windowHeight))

    def _onIconize(self,event):
        if event.IsIconized():
            self.wxApp.toggleShow()


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

        self.historListbox = wx.ListBox(self.historyPanel,pos=(startX,nextY),size=(self.windowWidth,self.panelHeight-40))
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

    #
    # called by panels
    #    

    def notifyMain(self,argsDict):
        self.wxApp.notifyMain(argsDict)
    
    #
    # called by App
    #

    def notifyGUI(self,argsDict):
        self.mainPanel.notifyGUI(argsDict)
        if 'updateHistory' in argsDict and argsDict['updateHistory']:      
            self._updateHistoryList()

