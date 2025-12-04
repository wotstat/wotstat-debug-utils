from Event import SafeEvent
from .Line import Line

class CheckboxLine(Line):
  
  def __init__(self, properties=3, commands=1):
    # type: (str, int, int) -> None
    super(CheckboxLine, self).__init__(type='checkbox', properties=properties, commands=commands)
    self.onToggle = SafeEvent()
  
  def _initialize(self):
    # type: () -> None
    super(CheckboxLine, self)._initialize()
    self._addStringProperty('label', '')
    self._addBoolProperty('isChecked', False)
    self._onCheckboxToggleCommand = self._addCommand('onCheckboxToggle')
    
    self._onCheckboxToggleCommand += self._onCheckboxToggle
    
  def _finalize(self):
    self._onCheckboxToggleCommand -= self._onCheckboxToggle
    return super(CheckboxLine, self)._finalize()

  def _onCheckboxToggle(self, args={}):
    # type: (dict) -> None
    value = args.get('value', False)
    self.isChecked = value
    self.onToggle(value)

  @property
  def label(self):
    # type: () -> str
    return self._getString(1)
  
  @label.setter
  def label(self, value):
    # type: (str) -> None
    self._setString(1, value)
  
  @property
  def isChecked(self):
    # type: () -> bool
    return self._getBool(2)
  
  @isChecked.setter
  def isChecked(self, value):
    # type: (bool) -> None
    self._setBool(2, value)
    