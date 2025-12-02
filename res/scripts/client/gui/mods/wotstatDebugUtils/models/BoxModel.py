import Math

from frameworks.wulf import ViewModel
from .WorldPositionModel import OffscreenWorldPositionModel

from ..MarkersManager import IMarkerManageable
import typing
if typing.TYPE_CHECKING:
  try: from GUI import WGMarkerPositionController as MarkerPositionController
  except ImportError: from GUI import MarkerPositionController

class BoxModel(ViewModel, IMarkerManageable):
  def __init__(self, properties=10, commands=0):
    # type: (int, int) -> None
    super(BoxModel, self).__init__(properties=properties, commands=commands)
  
  def _initialize(self):
    # type: () -> None
    super(BoxModel, self)._initialize()
    self._addRealProperty('width', 1.0)
    self._addStringProperty('color', "#00AAFF")
    self._addViewModelProperty('p0', OffscreenWorldPositionModel())
    self._addViewModelProperty('p1', OffscreenWorldPositionModel())
    self._addViewModelProperty('p2', OffscreenWorldPositionModel())
    self._addViewModelProperty('p3', OffscreenWorldPositionModel())
    self._addViewModelProperty('p4', OffscreenWorldPositionModel())
    self._addViewModelProperty('p5', OffscreenWorldPositionModel())
    self._addViewModelProperty('p6', OffscreenWorldPositionModel())
    self._addViewModelProperty('p7', OffscreenWorldPositionModel())
    
  def getWidth(self):
    # type: () -> float
    return self._getReal(0)
  
  def setWidth(self, value):
    # type: (float) -> None
    self._setReal(0, value)
    
  def getColor(self):
    # type: () -> str
    return self._getString(1)
  
  def setColor(self, value):
    # type: (str) -> None
    self._setString(1, value)
    
  def getPoint(self, index):
    # type: (int) -> OffscreenWorldPositionModel
    return self._getViewModel(2 + index)
  
  def setPoint(self, index, value):
    # type: (int, OffscreenWorldPositionModel) -> None
    self._setViewModel(2 + index, value)
  
  def destroy(self, markerCtrl):
    for i in range(8):
      self.getPoint(i).detach(markerCtrl)
      
      
  def setup(self, markerCtrl, width=None, color=None,
            p0=None, p1=None, p2=None, p3=None, p4=None, p5=None, p6=None, p7=None):
    points = [p0, p1, p2, p3, p4, p5, p6, p7]
    with self.transaction() as (tx):
      for i in range(8):
        tx.getPoint(i).attach(markerCtrl, points[i])
      
      if width is not None:
        tx.setWidth(width)
        
      if color is not None:
        tx.setColor(color)
      
  def setup(self, markerCtrl, width=None, color=None, p0=None, p1=None, p2=None, p3=None, p4=None, p5=None, p6=None, p7=None):
    
    with self.transaction() as (tx):
      points = [p0, p1, p2, p3, p4, p5, p6, p7]
      if points.count(None) == 0:
        for i in range(8):
          tx.getPoint(i).attach(markerCtrl, points[i])
      
      if width is not None:
        tx.setWidth(width)
        
      if color is not None:
        tx.setColor(color)