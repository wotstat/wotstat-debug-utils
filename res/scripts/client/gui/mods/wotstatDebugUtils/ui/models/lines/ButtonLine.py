from .Line import Line

class ButtonLine(Line):
  def __init__(self, properties=3, commands=1):
    # type: (str, int, int) -> None
    super(ButtonLine, self).__init__(type='button', properties=properties, commands=commands)
  
  def _initialize(self):
    # type: () -> None
    super(ButtonLine, self)._initialize()
    self._addStringProperty('label', '')
    self._addStringProperty('buttonText', '')
    self.onButtonClick = self._addCommand('onButtonClick')

  @property
  def label(self):
    # type: () -> str
    return self._getString(1)
  
  @label.setter
  def label(self, value):
    # type: (str) -> None
    self._setString(1, value)
  
  @property
  def buttonText(self):
    # type: () -> str
    return self._getString(2)
  
  @buttonText.setter
  def buttonText(self,  value):
    # type: (str) -> None
    self._setString(2, value)