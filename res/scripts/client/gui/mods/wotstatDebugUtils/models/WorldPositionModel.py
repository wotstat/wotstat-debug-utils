from frameworks.wulf import ViewModel

import typing
if typing.TYPE_CHECKING:
  try: from GUI import WGMarkerPositionController as MarkerPositionController
  except ImportError: from GUI import MarkerPositionController

class WorldPositionModel(ViewModel):

  def __init__(self, properties=4, commands=0):
    # type: (int, int) -> None
    super(WorldPositionModel, self).__init__(properties=properties, commands=commands)
    self.isAttached = False
    
  def _initialize(self):
    # type: () -> None
    super(WorldPositionModel, self)._initialize()
    self._addRealProperty('posx', 0.0)
    self._addRealProperty('posy', 0.0)
    self._addRealProperty('scale', 0.0)
    self._addBoolProperty('isVisible', False)
    
  def setPosx(self, value):
    # type: (float) -> None
    self._setReal(0, value)
    
  def getPosx(self):
    # type: () -> float
    return self._getReal(0)
  
  def setPosy(self, value):
    # type: (float) -> None
    self._setReal(1, value)
    
  def getPosy(self):
    # type: () -> float
    return self._getReal(1)
  
  def setScale(self, value):
    # type: (float) -> None
    self._setReal(2, value)
    
  def getScale(self):
    # type: () -> float
    return self._getReal(2)

  def setIsVisible(self, value):
    # type: (bool) -> None
    self._setBool(3, value)
    
  def getIsVisible(self):
    # type: () -> bool
    return self._getBool(3)
  
  def attach(self, markerCtrl, position):
    # type: (MarkerPositionController, any) -> None
    if self.isAttached: markerCtrl.remove(self.proxy)
    markerCtrl.add(self.proxy, position)
    self.isAttached = True
    
  def detach(self, markerCtrl):
    # type: (MarkerPositionController) -> None
    if self.isAttached: markerCtrl.remove(self.proxy)
    self.isAttached = False

class OffscreenWorldPositionModel(WorldPositionModel):

  def __init__(self, properties=6, commands=0):
    # type: (int, int) -> None
    super(OffscreenWorldPositionModel, self).__init__(properties=properties, commands=commands)
    
  def _initialize(self):
    # type: () -> None
    super(OffscreenWorldPositionModel, self)._initialize()
    self._addRealProperty('ndcLimitX', 200)
    self._addRealProperty('ndcLimitY', 200)
    
  def getNdcLimitX(self):
    # type: () -> float
    return self._getReal(4)
  
  def setNdcLimitX(self, value):
    # type: (float) -> None
    self._setReal(4, value)
    
  def getNdcLimitY(self):
    # type: () -> float
    return self._getReal(5)
  
  def setNdcLimitY(self, value):
    # type: (float) -> None
    self._setReal(5, value)