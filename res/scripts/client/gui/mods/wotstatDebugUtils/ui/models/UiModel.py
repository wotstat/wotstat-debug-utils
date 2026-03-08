
from frameworks.wulf import ViewModel, Array
from .lines.Panel import Panel

class UiModel(ViewModel):
  def __init__(self, properties=2, commands=0):
    # type: (int, int) -> None
    super(UiModel, self).__init__(properties=properties, commands=commands)
  
  def _initialize(self):
    # type: () -> None
    super(UiModel, self)._initialize()
    self._addArrayProperty('panels', Array[Panel]())
    self._addBoolProperty('showStatisticsPanel', False)

  @property
  def panels(self):
    # type: () -> Array
    return self._getArray(0)
  
  @panels.setter
  def panels(self, value):
    # type: (Array) -> None
    self._setArray(0, value)
  
  @property
  def showStatisticsPanel(self):
    # type: () -> bool
    return self._getBool(1)
  
  @showStatisticsPanel.setter
  def showStatisticsPanel(self, value):
    # type: (bool) -> None
    self._setBool(1, value)