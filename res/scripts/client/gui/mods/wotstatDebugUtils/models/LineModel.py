from frameworks.wulf import ViewModel
from .WorldPositionModel import OffscreenWorldPositionModel

from ..MarkersManager import IMarkerManageable

class LineModel(ViewModel, IMarkerManageable):
  def __init__(self, properties=4, commands=0):
    # type: (int, int) -> None
    super(LineModel, self).__init__(properties=properties, commands=commands)
  
  def _initialize(self):
    # type: () -> None
    super(LineModel, self)._initialize()
    self._addViewModelProperty('p1', OffscreenWorldPositionModel())
    self._addViewModelProperty('p2', OffscreenWorldPositionModel())
    self._addRealProperty('width', 1.0)
    self._addStringProperty('color', "#00AAFF")
  
  @property
  def p1(self):
    # type: () -> OffscreenWorldPositionModel
    return self._getViewModel(0)
  
  @property
  def p2(self):
    # type: () -> OffscreenWorldPositionModel
    return self._getViewModel(1)
  
  @staticmethod
  def getP1Type():
    return OffscreenWorldPositionModel
  
  @staticmethod
  def getP2Type():
    return OffscreenWorldPositionModel
  
  def getWidth(self):
    # type: () -> float
    return self._getReal(2)
  
  def setWidth(self, value):
    # type: (float) -> None
    self._setReal(2, value)
    
  def getColor(self):
    # type: () -> str
    return self._getString(3)
  
  def setColor(self, value):
    # type: (str) -> None
    self._setString(3, value)
    
  def destroy(self, markerCtrl):
    self.p1.detach(markerCtrl)
    self.p2.detach(markerCtrl)
      
  def setup(self, markerCtrl, p1=None, p2=None, width=None, color=None):

    if p1 is not None: self.p1.attach(markerCtrl, p1)
    if p2 is not None: self.p2.attach(markerCtrl, p2)
    
    with self.transaction() as (tx):
      if width is not None:
        tx.setWidth(width)
        
      if color is not None:
        tx.setColor(color)