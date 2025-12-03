from frameworks.wulf import ViewModel, Array
from .gizmos.models.MarkerModel import MarkerModel
from .gizmos.models.LineModel import LineModel
from .gizmos.models.PolyLineModel import PolyLineModel
from .gizmos.models.BoxModel import BoxModel
from .ui.models.UiModel import UiModel

class DebugViewModel(ViewModel):
  
  def __init__(self, properties=5, commands=0):
    # type: (int, int) -> None
    super(DebugViewModel, self).__init__(properties=properties, commands=commands)
  
  def _initialize(self):
    # type: () -> None
    super(DebugViewModel, self)._initialize()
    self._addArrayProperty('markers', Array())
    self._addArrayProperty('lines', Array())
    self._addArrayProperty('polyLines', Array())
    self._addArrayProperty('boxes', Array())
    self._addViewModelProperty('ui', UiModel())

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
    
  def getPolyLines(self):
    # type: () -> Array
    return self._getArray(2)
  
  def setPolyLines(self, value):
    # type: (Array) -> None
    self._setArray(2, value)
    
  def getBoxes(self):
    # type: () -> Array
    return self._getArray(3)
  
  def setBoxes(self, value):
    # type: (Array) -> None
    self._setArray(3, value)
    
  def getUi(self):
    # type: () -> UiModel
    return self._getViewModel(4)
  
  def setUi(self, value):
    # type: (UiModel) -> None
    self._setViewModel(4, value)
  
  @staticmethod
  def getMarkersType():
    return MarkerModel
  
  @staticmethod
  def getLinesType():
    return LineModel
  
  @staticmethod
  def getPolyLinesType():
    return PolyLineModel
  
  @staticmethod
  def getBoxesType():
    return BoxModel