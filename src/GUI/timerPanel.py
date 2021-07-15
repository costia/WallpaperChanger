import wx
import logging
import math


class TimerPanel(wx.Panel):
    def __init__(self,frame,windowWidth,panelHeight):
        super(TimerPanel, self).__init__(frame,style = wx.NO_FULL_REPAINT_ON_RESIZE)
        self.windowWidth = windowWidth
        self.panelHeight = panelHeight
        self.log = logging.getLogger('WallpaperChanger')
        self.parentFrame = frame
        self.drawPercent = False

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        # self.Bind(wx.EVT_ERASE_BACKGROUND, lambda x: None )
        self.percent = 0

        self.changeNowButton = wx.Button(self,-1,'Change now',pos=(5,self.panelHeight-70),size=(self.windowWidth,35))
        self.changeNowButton.Bind(wx.EVT_BUTTON, lambda x: self.parentFrame.notifyMain({'changeWallpaper':True}))

    def OnSize(self,event):
        Size  = self.ClientSize
        self._Buffer = wx.EmptyBitmap(*Size)
        self.UpdateDrawing()

    def OnPaint(self, event):
        self.UpdateDrawing()
        dc = wx.BufferedPaintDC(self, self._Buffer)

    def UpdateDrawing(self):
        dc = wx.MemoryDC()
        dc.SelectObject(self._Buffer)
        dc.Clear()
        gc = wx.GraphicsContext.Create(dc)

        size = gc.GetSize()
        center = wx.Point2D(size[0]/2-10,size[1]/2-25)
        radius = size[0]/2.5
        
        path = gc.CreatePath()
        dark = 0.6
        if self.drawPercent:
            gc.SetBrush(wx.Brush(wx.Colour(240,240,240)))
        else:
            gc.SetBrush(wx.Brush(wx.Colour(200,200,200)))
        path = gc.CreatePath()
        path.MoveToPoint(center)
        path.AddCircle(center[0],center[1],radius)
        gc.FillPath(path)

        if self.drawPercent:
            gc.SetBrush(wx.Brush(wx.Colour(73,151,231)))
            path = gc.CreatePath()
            path.MoveToPoint(center)
            startAngle= -(math.pi/2) + self.percent*2*math.pi
            endAngle= -(math.pi/2) 
            path.AddArc(center,radius,startAngle,endAngle,True)
            path.CloseSubpath()
            gc.FillPath(path)

        path = gc.CreatePath()
        dark = 0.6
        gc.SetPen(wx.Pen(wx.Colour(73*dark,151*dark,231*dark),width=5))
        path = gc.CreatePath()
        path.MoveToPoint(center)
        path.AddCircle(center[0],center[1],radius)
        gc.StrokePath(path)

        self.Refresh(eraseBackground=False)
        self.Update()

    def notifyGUI(self,argsDict):
        if 'percentTimer' in argsDict:
            self.percent = 1.0 - argsDict['percentTimer']
            self.Refresh(eraseBackground=False)
        if 'blockWallpaperChange' in argsDict:
            self.percent = 1.0
            self.drawPercent = not argsDict['blockWallpaperChange']
            self.Refresh(eraseBackground=False)
