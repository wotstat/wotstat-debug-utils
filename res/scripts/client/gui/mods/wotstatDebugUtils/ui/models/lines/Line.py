from frameworks.wulf import ViewModel

class Line(ViewModel):
  def __init__(self, type, properties=0, commands=0):
    # type: (str, int, int) -> None
    self._type = type
    super(Line, self).__init__(properties=properties, commands=commands)
    
  def _initialize(self):
    # type: () -> None
    super(Line, self)._initialize()
    self._addStringProperty('type', self._type)
    