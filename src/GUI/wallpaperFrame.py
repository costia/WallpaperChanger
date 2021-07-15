import wx
import logging

from resources import Resources

from GUI.mainPanel import MainPanel
from GUI.historyPanel import HistoryPanel
from GUI.timerPanel import TimerPanel

class WallpaperFrame(wx.Frame):
    def __init__(self,wxApp,config):
        super(WallpaperFrame, self).__init__(None, style= wx.CAPTION |	 wx.CLOSE_BOX | wx.MINIMIZE_BOX)
        self.SetTitle(Resources['APP_NAME'])
        self.SetIcon(wx.Icon(wx.Bitmap(Resources['ICON_PATH'])))

        self.windowWidth = 290
        self.panelHeight = 405
        self.windowHeight = self.panelHeight

        self.wxApp = wxApp
        self.log = logging.getLogger('WallpaperChanger')
        

        self.selectTimerPanelBtn = wx.Button(self,-1,'Main',pos=(0,0),size=(self.windowWidth/3+5,30))
        self.selectHistoryPanelBtn = wx.Button(self,-1,'History',pos=(self.windowWidth/3+5,0),size=(self.windowWidth/3,30))
        self.selectMainPanelBtn = wx.Button(self,-1,'Settings',pos=(self.windowWidth*2/3+5,0),size=(self.windowWidth/3+5,30))
        
        self.mainPanel = MainPanel(self,config,self.windowWidth)
        self.mainPanel.SetSize(size = (self.windowWidth+25,self.panelHeight-30))
        self.mainPanel.SetPosition((0,30))
        self.mainPanel.Show(False)

        self.historyPanel = HistoryPanel(self,self.windowWidth,self.panelHeight)
        self.historyPanel.SetSize(size = (self.windowWidth+25,self.panelHeight-30))
        self.historyPanel.SetPosition((0,30))
        self.historyPanel.Show(False)

        self.timerPanel = TimerPanel(self,self.windowWidth,self.panelHeight)
        self.timerPanel.SetSize(size = (self.windowWidth+25,self.panelHeight-30))
        self.timerPanel.SetPosition((0,30))

        self.Bind(wx.EVT_CLOSE, lambda x: self.wxApp.notifyMain({'handleExit':True}))
        self.Bind(wx.EVT_ICONIZE, self._onIconize)

        self.selectMainPanelBtn.Bind(wx.EVT_BUTTON, self._showMainPanel)
        self.selectHistoryPanelBtn.Bind(wx.EVT_BUTTON, self._showHistoryPanel)
        self.selectTimerPanelBtn.Bind(wx.EVT_BUTTON, self._showTimerPanel)

        self.baseFont = self.selectMainPanelBtn.GetFont()
        self.selectTimerPanelBtn.SetFont(self.selectMainPanelBtn.GetFont().Bold())
        self.SetClientSize(size = (self.windowWidth+10,self.windowHeight))

    def _onIconize(self,event):
        if event.IsIconized():
            self.wxApp.toggleShow()


    def _showHistoryPanel(self,event):
        self.historyPanel.Show(True)
        self.mainPanel.Show(False)
        self.timerPanel.Show(False)
        self.selectMainPanelBtn.SetFont(self.baseFont)
        self.selectHistoryPanelBtn.SetFont(self.baseFont.Bold())
        self.selectTimerPanelBtn.SetFont(self.baseFont)
    
    def _showMainPanel(self,event):
        self.historyPanel.Show(False)
        self.mainPanel.Show(True)
        self.timerPanel.Show(False)
        self.selectMainPanelBtn.SetFont(self.baseFont.Bold())
        self.selectHistoryPanelBtn.SetFont(self.baseFont)
        self.selectTimerPanelBtn.SetFont(self.baseFont)

    def _showTimerPanel(self,event):
        self.historyPanel.Show(False)
        self.mainPanel.Show(False)
        self.timerPanel.Show(True)
        self.selectMainPanelBtn.SetFont(self.baseFont)
        self.selectHistoryPanelBtn.SetFont(self.baseFont)
        self.selectTimerPanelBtn.SetFont(self.baseFont.Bold())

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
        self.historyPanel.notifyGUI(argsDict)
        self.timerPanel.notifyGUI(argsDict)

