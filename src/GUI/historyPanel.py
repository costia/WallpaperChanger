import wx
import logging

from GUI.common import createMenuItem
from database import WallpaperDatabase


class HistoryPanel(wx.Panel):
    def __init__(self,frame,windowWidth,panelHeight):
        super(HistoryPanel, self).__init__(frame)
        self.windowWidth = windowWidth
        self.panelHeight = panelHeight
        self.log = logging.getLogger('WallpaperChanger')
        self.parentFrame = frame
        self.db = WallpaperDatabase()
        self.historyLength = 40

        startX = 5
        nextY = 5

        self.historListbox = wx.ListBox(self,pos=(startX,nextY),size=(self.windowWidth,self.panelHeight-40))
        self._updateHistoryList()

        self.popupmenuHistory = wx.Menu()
        createMenuItem(self.popupmenuHistory, 'Copy selection source',  self._onCopySource)
        self.historListbox.Bind(wx.EVT_CONTEXT_MENU, self._onShowHistoryPopup)

    def _updateHistoryList(self):
        names,links = self.db.getLatest(self.historyLength)
        self.historySources = links
        if len(names)>0:
            self.historListbox.SetItems(names)
            self.historListbox.SetSelection(0)

    def _onShowHistoryPopup(self,event):
        self.PopupMenu(self.popupmenuHistory,self.ScreenToClient(event.GetPosition()))

    def _onCopySource(self,event):
        id = self.historListbox.GetSelection()
        source = self.historySources[id]
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(source))
            wx.TheClipboard.Close()
    
    def notifyGUI(self,argsDict):
        if 'updateHistory' in argsDict and argsDict['updateHistory']:      
            self._updateHistoryList()
