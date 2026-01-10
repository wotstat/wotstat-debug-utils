from .Line import Line

class HeaderLine(Line):
  def __init__(self, properties=2, commands=0):
    # type: (str, int, int) -> None
    super(HeaderLine, self).__init__(type='header', properties=properties, commands=commands)
  
  def _initialize(self):
    # type: () -> None
    super(HeaderLine, self)._initialize()
    self._addStringProperty('text', '')

  @property
  def text(self):
    # type: () -> str
    return self._getString(1)
  
  @text.setter
  def text(self,  value):
    # type: (str) -> None
    self._setString(1, value)
