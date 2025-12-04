from Event import SafeEvent
from .Line import Line

class TextInputLine(Line):
    
  def __init__(self, properties=3, commands=1):
    # type: (str, int, int) -> None
    super(TextInputLine, self).__init__(type='text-input', properties=properties, commands=commands)
    self.onChange = SafeEvent()
    
  def _initialize(self):
    # type: () -> None
    super(TextInputLine, self)._initialize()
    self._addStringProperty('label', '')
    self._addStringProperty('value', '')
    self._onInputChangeCommand = self._addCommand('onInputChange')
    
    self._onInputChangeCommand += self._onInputChange
    
  def _finalize(self):
    self._onInputChangeCommand -= self._onInputChange
    return super(TextInputLine, self)._finalize()
  
  def _onInputChange(self, args={}):
    # type: (dict) -> None
    value = args.get('value', '')
    self.value = value
    self.onChange(value)
  
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