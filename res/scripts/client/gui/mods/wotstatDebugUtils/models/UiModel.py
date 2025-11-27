
from frameworks.wulf import ViewModel, Array

from typing import Callable

class Line(ViewModel):
  def __init__(self, type, properties=0, commands=0):
    # type: (str, int, int) -> None
    self._type = type
    super(Line, self).__init__(properties=properties, commands=commands)
    
  def _initialize(self):
    # type: () -> None
    super(Line, self)._initialize()
    self._addStringProperty('type', self._type)
    
class TextLine(Line):
  def __init__(self, properties=2, commands=0):
    # type: (str, int, int) -> None
    super(TextLine, self).__init__(type='text', properties=properties, commands=commands)
  
  def _initialize(self):
    # type: () -> None
    super(TextLine, self)._initialize()
    self._addStringProperty('text', '')

  def getText(self):
    # type: () -> str
    return self._getString(1)
  
  def setText(self,  value):
    # type: (str) -> None
    self._setString(1, value)

class ButtonLine(Line):
  def __init__(self, properties=3, commands=1):
    # type: (str, int, int) -> None
    super(ButtonLine, self).__init__(type='button', properties=properties, commands=commands)
  
  def _initialize(self):
    # type: () -> None
    super(ButtonLine, self)._initialize()
    self._addStringProperty('text', '')
    self._addStringProperty('buttonLabel', '')
    self.onButtonClick = self._addCommand('onButtonClick')

  def getText(self):
    # type: () -> str
    return self._getString(1)
  
  def setText(self,  value):
    # type: (str) -> None
    self._setString(1, value)
    
  def getButtonLabel(self):
    # type: () -> str
    return self._getString(2)
  
  def setButtonLabel(self,  value):
    # type: (str) -> None
    self._setString(2, value)

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

  def getName(self):
    # type: () -> str
    return self._getString(0)
  
  def setName(self,  value):
    # type: (str) -> None
    self._setString(0, value)
    
  def getLines(self):
    # type: () -> Array
    return self._getArray(1)
  
  def setLines(self, value):
    # type: (Array) -> None
    self._setArray(1, value)
    
  def addTextLine(self, text):
    # type: (str) -> None
    line = TextLine()
    line.setText(text)
    lines = self.getLines()
    lines.addViewModel(line)
    lines.invalidate()
    
    return line
    
  def addButtonLine(self, text, buttonLabel, onClickCallback):
    # type: (str, str, Callable) -> None
    line = ButtonLine()
    line.setText(text)
    line.setButtonLabel(buttonLabel)
    line.onButtonClick += onClickCallback
    lines = self.getLines()
    lines.addViewModel(line)
    lines.invalidate()
    
    return line
    
  @staticmethod
  def getLinesType():
    return Line
    
  def remove(self):
    # type: () -> None
    from ....debugUtils import ui as uiController
    uiController.removePanel(self)
    
    for line in self.getLines():
      if isinstance(line, ButtonLine):
        line.onButtonClick -= None # remove all listeners

class UiModel(ViewModel):
  def __init__(self, properties=1, commands=0):
    # type: (int, int) -> None
    super(UiModel, self).__init__(properties=properties, commands=commands)
  
  def _initialize(self):
    # type: () -> None
    super(UiModel, self)._initialize()
    self._addArrayProperty('panels', Array())
    
  def getPanels(self):
    # type: () -> Array
    return self._getArray(0)
  
  def setPanels(self, value):
    # type: (Array) -> None
    self._setArray(0, value)
    