from frameworks.wulf import ViewModel, Array
from .Line import Line
from .TextLine import TextLine
from .ButtonLine import ButtonLine
from .CheckboxLine import CheckboxLine
from .ValueLine import ValueLine
from .SeparatorLine import SeparatorLine
from .TextInputLine import TextInputLine
from .NumberInputLine import NumberInputLine
from typing import Callable

class Panel(ViewModel):
  def __init__(self, name, properties=1, commands=0):
    # type: (str, int, int) -> None
    self.defaultName = name
    super(Panel, self).__init__(properties=properties, commands=commands)
  
  def _initialize(self):
    # type: () -> None
    super(Panel, self)._initialize()
    self._addStringProperty('name', self.defaultName)
    self._addArrayProperty('lines', Array[Line]())

  @property
  def name(self):
    # type: () -> str
    return self._getString(0)
  
  @name.setter
  def name(self, value):
    # type: (str) -> None
    self._setString(0, value)
  
  @property
  def lines(self):
    # type: () -> Array
    return self._getArray(1)
  
  @lines.setter
  def lines(self, value):
    # type: (Array) -> None
    self._setArray(1, value)
  
  def _addLine(self, line):
    # type: (Line) -> None
    lines = self.lines
    lines.addViewModel(line)
    lines.invalidate()
    
  def addTextLine(self, text):
    # type: (str) -> None
    line = TextLine()
    line.text = text
    self._addLine(line)
    return line
    
  def addButtonLine(self, label, buttonText, onClickCallback):
    # type: (str, str, Callable) -> None
    line = ButtonLine()
    line.label = label
    line.buttonText = buttonText
    self._addLine(line)
    line.onButtonClick += onClickCallback
    return line
  
  def addCheckboxLine(self, label, isChecked=False, onToggleCallback=None):
    # type: (str, bool, Callable) -> None
    line = CheckboxLine()
    line.label = label
    line.isChecked = isChecked
    self._addLine(line)
    if onToggleCallback is not None:
      line.onToggle += onToggleCallback
    return line
  
  def addValueLine(self, label, value):
    # type: (str, str) -> None
    line = ValueLine()
    line.label = label
    line.value = value
    self._addLine(line)
    return line
  
  def addSeparatorLine(self):
    # type: () -> None
    line = SeparatorLine()
    self._addLine(line)
    return line
  
  def addTextInputLine(self, label, value='', onChangeCallback=None):
    # type: (str, str, Callable) -> None
    line = TextInputLine()
    line.label = label
    line.value = value
    self._addLine(line)
    if onChangeCallback is not None:
      line.onChange += onChangeCallback
    return line
  
  def addNumberInputLine(self, label, value=0, onChangeCallback=None):
    # type: (str, float, Callable) -> None
    line = NumberInputLine()
    line.label = label
    line.value = value
    self._addLine(line)
    if onChangeCallback is not None:
      line.onChange += onChangeCallback
    return line
  
  @staticmethod
  def getLinesType():
    return Line
    
  def remove(self):
    # type: () -> None
    from gui.debugUtils import ui as uiController
    uiController.removePanel(self)
    
    for line in self.getLines():
      if isinstance(line, ButtonLine):
        line.onButtonClick -= None # remove all listeners
