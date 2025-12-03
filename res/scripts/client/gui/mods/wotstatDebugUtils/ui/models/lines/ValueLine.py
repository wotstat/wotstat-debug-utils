from .Line import Line

class ValueLine(Line):
  def __init__(self, properties=2, commands=0):
    # type: (str, int, int) -> None
    super(ValueLine, self).__init__(type='value', properties=properties, commands=commands)
    
  def _initialize(self):
    # type: () -> None
    super(ValueLine, self)._initialize()
    self._addStringProperty('label', '')
    self._addStringProperty('value', '')

  @property
  def label(self):
    # type: () -> str
    return self._getString(1)
  
  @label.setter
  def label(self, value):
    # type: (str) -> None
    self._setString(1, value)
  
  @property
  def value(self):
    # type: () -> str
    return self._getString(2)
  
  @value.setter
  def value(self, value):
    # type: (str) -> None
    self._setString(2, value)