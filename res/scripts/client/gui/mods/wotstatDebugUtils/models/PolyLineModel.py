from frameworks.wulf import ViewModel, Array
from .WorldPositionModel import OffscreenWorldPositionModel

from ..MarkersManager import IMarkerManageable
from .LineModel import LineEnd

class PolyLineModel(ViewModel, IMarkerManageable):
  def __init__(self, properties=6, commands=0):
    # type: (int, int) -> None
    super(PolyLineModel, self).__init__(properties=properties, commands=commands)
  
  def _initialize(self):
    # type: () -> None
    super(PolyLineModel, self)._initialize()
    self._addArrayProperty('points', Array[OffscreenWorldPositionModel]())
    self._addRealProperty('width', 1.0)
    self._addStringProperty('color', "#00AAFF")
    self._addNumberProperty('end1', LineEnd.NONE)
    self._addNumberProperty('end2', LineEnd.NONE)
    self._addBoolProperty('closed', False)
  
  def getPoints(self):
    # type: () -> Array[OffscreenWorldPositionModel]
    return self._getArray(0)
  
  def setPoints(self, value):
    # type: (Array[OffscreenWorldPositionModel]) -> None
    self._setArray(0, value)
  
  @staticmethod
  def getPointsType():
    return OffscreenWorldPositionModel
  
  def getWidth(self):
    # type: () -> float
    return self._getReal(1)
  
  def setWidth(self, value):
    # type: (float) -> None
    self._setReal(1, value)
    
  def getColor(self):
    # type: () -> str
    return self._getString(2)
  
  def setColor(self, value):
    # type: (str) -> None
    self._setString(2, value)
    
  def getEnd1(self):
    # type: () -> int
    return self._getNumber(3)
  
  def setEnd1(self, value):
    # type: (int) -> None
    self._setNumber(3, value)
  
  def getEnd2(self):
    # type: () -> int
    return self._getNumber(4)
  
  def setEnd2(self, value):
    # type: (int) -> None
    self._setNumber(4, value)
    
  def getClosed(self):
    # type: () -> bool
    return self._getBool(5)
  
  def setClosed(self, value):
    # type: (bool) -> None
    self._setBool(5, value)
  
  def destroy(self, markerCtrl):
    for point in self.getPoints():
      point.detach(markerCtrl)
      
  def setup(self, markerCtrl, points=None, width=None, color=None, end1=None, end2=None, closed=None):

    with self.transaction() as (tx):
      
      if points is not None:
        
        array = tx.getPoints()
        currentLength = len(array)
        
        if len(points) < currentLength:
          for _ in range(currentLength - len(points)):
            index = len(array) - 1
            
            array[index].detach(markerCtrl)
            array.remove(index)
            
        elif len(points) > currentLength:
          for _ in range(len(points) - currentLength):
            p = OffscreenWorldPositionModel()
            array.addViewModel(p)
        
        for i in range(len(points)):
          pointModel = array[i] # type: OffscreenWorldPositionModel
          pointModel.attach(markerCtrl, points[i])
    
      if width is not None:
        tx.setWidth(width)
        
      if color is not None:
        tx.setColor(color)
        
      if end1 is not None:
        tx.setEnd1(end1)
        
      if end2 is not None:
        tx.setEnd2(end2)
      
      if closed is not None:
        tx.setClosed(closed)