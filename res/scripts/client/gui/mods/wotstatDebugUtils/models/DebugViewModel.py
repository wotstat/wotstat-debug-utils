from frameworks.wulf import ViewModel, Array
from .MarkerModel import MarkerModel
from .LineModel import LineModel

class DebugViewModel(ViewModel):
  
  def __init__(self, properties=2, commands=0):
    # type: (int, int) -> None
    super(DebugViewModel, self).__init__(properties=properties, commands=commands)
  
  def _initialize(self):
    # type: () -> None
    super(DebugViewModel, self)._initialize()
    self._addArrayProperty('markers', Array())
    self._addArrayProperty('lines', Array())

  def getMarkers(self):
    # type: () -> Array
    return self._getArray(0)
  
  def setMarkers(self, value):
    # type: (Array) -> None
    self._setArray(0, value)
    
  def getLines(self):
    # type: () -> Array
    return self._getArray(1)
  
  def setLines(self, value):
    # type: (Array) -> None
    self._setArray(1, value)
  
  @staticmethod
  def getMarkersType():
    return MarkerModel
  
  @staticmethod
  def getLinesType():
    return LineModel