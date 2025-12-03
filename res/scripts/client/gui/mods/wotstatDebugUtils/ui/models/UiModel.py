
from frameworks.wulf import ViewModel, Array
from .lines.Panel import Panel


class UiModel(ViewModel):
  def __init__(self, properties=1, commands=0):
    # type: (int, int) -> None
    super(UiModel, self).__init__(properties=properties, commands=commands)
  
  def _initialize(self):
    # type: () -> None
    super(UiModel, self)._initialize()
    self._addArrayProperty('panels', Array[Panel]())
    
  def getPanels(self):
    # type: () -> Array
    return self._getArray(0)
  
  def setPanels(self, value):
    # type: (Array) -> None
    self._setArray(0, value)
    