import typing

import BigWorld
from ..DebugView import onDebugViewLoaded, onDebugViewUnloaded, DebugView
from .Marker import Marker
from .Line import Line
from .PolyLine import PolyLine
from .Box import Box

class GizmosController:
  
  def __init__(self):
    
    self._markers = {} # type: typing.Dict[Marker, int]
    self._lines = {} # type: typing.Dict[Line, int]
    self._polyLines = {} # type: typing.Dict[PolyLine, int]
    self._boxes = {} # type: typing.Dict[Box, int]
    
    global onDebugViewLoaded, onDebugViewUnloaded
    self._currentDebugView = None # type: DebugView
    onDebugViewLoaded += self._onDebugViewLoaded
    onDebugViewUnloaded += self._onDebugViewUnloaded
  
  def _onDebugViewLoaded(self, debugView):
    # type: (DebugView) -> None
    self._currentDebugView = debugView
    self._addElements()
      
  def _onDebugViewUnloaded(self, debugView):
    # type: (DebugView) -> None
    if self._currentDebugView != debugView: return
    self._currentDebugView = None
    for marker in self._markers.keys(): self._markers[marker] = -1
    for line in self._lines.keys(): self._lines[line] = -1
    for polyLine in self._polyLines.keys(): self._polyLines[polyLine] = -1
    for box in self._boxes.keys(): self._boxes[box] = -1
    
  def _addElements(self):
    for marker, markerID in self._markers.items():
      if markerID == -1:
        newMarkerID = self._currentDebugView.createMarker()
        self._markers[marker] = newMarkerID
        self._setupMarker(marker)
        
    for line, lineID in self._lines.items():
      if lineID == -1:
        newLineID = self._currentDebugView.createLine()
        self._lines[line] = newLineID
        self._setupLine(line)
        
    for polyLine, polyLineID in self._polyLines.items():
      if polyLineID == -1:
        newPolyLineID = self._currentDebugView.createPolyLine()
        self._polyLines[polyLine] = newPolyLineID
        self._setupPolyLine(polyLine)
    
    for box, boxID in self._boxes.items():
      if boxID == -1:
        newBoxID = self._currentDebugView.createBox()
        self._boxes[box] = newBoxID
        self._setupBox(box)
        
  def _setupMarker(self, marker):
    # type: (Marker) -> None
    markerID = self._markers.get(marker, -1)
    if markerID == -1 or not self._currentDebugView:
      return
    
    self._currentDebugView.setupMarker(
      markerID,
      position=marker.position,
      size=marker.size,
      color=marker.color,
      text=marker.text
    )

  def _setupLine(self, line):
    # type: (Line) -> None
    lineID = self._lines.get(line, -1)
    if lineID == -1 or not self._currentDebugView:
      return
    
    self._currentDebugView.setupLine(
      lineID,
      p1=line.p1,
      p2=line.p2,
      width=line.width,
      color=line.color,
      end1=line.end1,
      end2=line.end2
    )
    
  def _setupPolyLine(self, polyLine):
    # type: (PolyLine) -> None
    polyLineID = self._polyLines.get(polyLine, -1)
    if polyLineID == -1 or not self._currentDebugView:
      return
    
    self._currentDebugView.setupPolyLine(
      polyLineID,
      points=polyLine.points,
      width=polyLine.width,
      color=polyLine.color,
      end1=polyLine.end1,
      end2=polyLine.end2,
      closed=polyLine.closed
    )
  
  def _setupBox(self, box):
    # type: (Box) -> None
    boxID = self._boxes.get(box, -1)
    if boxID == -1 or not self._currentDebugView:
      return
    
    self._currentDebugView.setupBox(
      boxID,
      width=box._width,
      color=box._color,
      p0=box._p0, p1=box._p1, p2=box._p2, p3=box._p3, p4=box._p4, p5=box._p5, p6=box._p6, p7=box._p7
    )
  
  def _destroyMarker(self, marker):
    # type: (Marker) -> None
    markerID = self._markers.pop(marker, -1)
    if markerID != -1 and self._currentDebugView:
      self._currentDebugView.destroyMarker(markerID)
  
  def _destroyLine(self, line):
    # type: (Line) -> None
    lineID = self._lines.pop(line, -1)
    if lineID != -1 and self._currentDebugView:
      self._currentDebugView.destroyLine(lineID)
  
  def _destroyPolyLine(self, polyLine):
    # type: (PolyLine) -> None
    polyLineID = self._polyLines.pop(polyLine, -1)
    if polyLineID != -1 and self._currentDebugView:
      self._currentDebugView.destroyPolyLine(polyLineID)
  
  def _destroyBox(self, box):
    # type: (Box) -> None
    boxID = self._boxes.pop(box, -1)
    if boxID != -1 and self._currentDebugView:
      self._currentDebugView.destroyBox(boxID)
  
  def createMarker(self, position=None, size=None, color=None, text=None, timeout=None):
    marker = Marker(self)
    self._markers[marker] = -1
    
    if self._currentDebugView:
      markerID = self._currentDebugView.createMarker()
      self._markers[marker] = markerID
      marker._setup(position=position, size=size, color=color, text=text)
      if timeout is not None: BigWorld.callback(timeout, marker.destroy)
    
    return marker
  
  def createLine(self, p1=None, p2=None, width=None, color=None, end1=None, end2=None, timeout=None):
    line = Line(self)
    self._lines[line] = -1
    
    if self._currentDebugView:
      lineID = self._currentDebugView.createLine()
      self._lines[line] = lineID
      line._setup(p1=p1, p2=p2, width=width, color=color, end1=end1, end2=end2)
      if timeout is not None: BigWorld.callback(timeout, line.destroy)
    
    return line
  
  def createPolyLine(self, points=None, width=None, color=None, end1=None, end2=None, closed=None, timeout=None):
    polyLine = PolyLine(self)
    self._polyLines[polyLine] = -1
    
    if self._currentDebugView:
      polyLineID = self._currentDebugView.createPolyLine()
      self._polyLines[polyLine] = polyLineID
      polyLine._setup(points=points, width=width, color=color, end1=end1, end2=end2, closed=closed)
      if timeout is not None: BigWorld.callback(timeout, polyLine.destroy)
    
    return polyLine
  
  def createBox(self, width=None, color=None, center=None, w=None, h=None, d=None, rotationX=None, rotationY=None, rotationZ=None, timeout=None):
    box = Box(self)
    self._boxes[box] = -1
    
    if self._currentDebugView:
      boxID = self._currentDebugView.createBox()
      self._boxes[box] = boxID
      box._setup(width=width, color=color)
      box.fromCenterSizeRotation(center, w, h, d, rotationX, rotationY, rotationZ)
      if timeout is not None: BigWorld.callback(timeout, box.destroy)
    
    return box
  
  def clearMarkers(self):
    for marker in self._markers.keys():
      self._destroyMarker(marker)
      
  def clearLines(self):
    for line in self._lines.keys():
      self._destroyLine(line)
      
  def clearPolyLines(self):
    for polyLine in self._polyLines.keys():
      self._destroyPolyLine(polyLine)
      
  def clearAll(self):
    self.clearMarkers()
    self.clearLines()
    self.clearPolyLines()