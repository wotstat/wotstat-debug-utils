
from frameworks.wulf import ViewModel, Array
from Event import SafeEvent

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
    self._addStringProperty('label', '')
    self._addStringProperty('buttonText', '')
    self.onButtonClick = self._addCommand('onButtonClick')

  def getLabel(self):
    # type: () -> str
    return self._getString(1)
  
  def setLabel(self,  value):
    # type: (str) -> None
    self._setString(1, value)
    
  def getButtonText(self):
    # type: () -> str
    return self._getString(2)
  
  def setButtonText(self,  value):
    # type: (str) -> None
    self._setString(2, value)

class CheckboxLine(Line):
  
  class CheckboxType:
    DEFAULT = 'default'
    VISIBILITY = 'visibility'
  
  def __init__(self, properties=4, commands=1):
    # type: (str, int, int) -> None
    super(CheckboxLine, self).__init__(type='checkbox', properties=properties, commands=commands)
    self.onToggle = SafeEvent()
  
  def _initialize(self):
    # type: () -> None
    super(CheckboxLine, self)._initialize()
    self._addStringProperty('label', '')
    self._addBoolProperty('isChecked', False)
    self._addStringProperty('checkboxType', CheckboxLine.CheckboxType.DEFAULT)
    self._onCheckboxToggleCommand = self._addCommand('onCheckboxToggle')
    
    self._onCheckboxToggleCommand += self._onCheckboxToggle
    
  def _finalize(self):
    self._onCheckboxToggleCommand -= self._onCheckboxToggle
    return super()._finalize()

  def _onCheckboxToggle(self, args={}):
    # type: (dict) -> None
    value = args.get('value', False)
    self.setIsChecked(value)
    self.onToggle(value)

  def getLabel(self):
    # type: () -> str
    return self._getString(1)
  
  def setLabel(self,  value):
    # type: (str) -> None
    self._setString(1, value)
    
  def getIsChecked(self):
    # type: () -> bool
    return self._getBool(2)
  
  def setIsChecked(self,  value):
    # type: (bool) -> None
    self._setBool(2, value)
    
  def getCheckboxType(self):
    # type: () -> str
    return self._getString(3)
  
  def setCheckboxType(self, value):
    # type: (str) -> None
    self._setString(3, value)

class ValueLine(Line):
  def __init__(self, properties=2, commands=0):
    # type: (str, int, int) -> None
    super(ValueLine, self).__init__(type='value', properties=properties, commands=commands)
    
  
  def _initialize(self):
    # type: () -> None
    super(ValueLine, self)._initialize()
    self._addStringProperty('label', '')
    self._addStringProperty('value', '')

  def getLabel(self):
    # type: () -> str
    return self._getString(1)
  
  def setLabel(self,  value):
    # type: (str) -> None
    self._setString(1, value)
    
  def getValue(self):
    # type: () -> str
    return self._getString(2)
  
  def setValue(self, value):
    # type: (str) -> None
    self._setString(2, value)

class SeparatorLine(Line):
  def __init__(self, properties=1, commands=0):
    # type: (str, int, int) -> None
    super(SeparatorLine, self).__init__(type='separator', properties=properties, commands=commands)
  
  def _initialize(self):
    # type: () -> None
    super(SeparatorLine, self)._initialize()
    
class InputLine(Line):
  class InputType:
    NUMERIC = 'numeric'
    TEXT = 'text'
    
  def __init__(self, properties=3, commands=1):
    # type: (str, int, int) -> None
    super(InputLine, self).__init__(type='input', properties=properties, commands=commands)
    self.onChange = SafeEvent()
    
  def _initialize(self):
    # type: () -> None
    super(InputLine, self)._initialize()
    self._addStringProperty('label', '')
    self._addStringProperty('value', '')
    self._addStringProperty('inputType', InputLine.InputType.TEXT)
    self._onInputChangeCommand = self._addCommand('onInputChange')
    
    self._onInputChangeCommand += self._onInputChange
    
  def _finalize(self):
    self._onInputChangeCommand -= self._onInputChange
    return super()._finalize()
  
  def _onInputChange(self, args={}):
    # type: (dict) -> None
    value = args.get('value', '')
    self.setValue(value)
    self.onChange(value)
    
  def getLabel(self):
    # type: () -> str
    return self._getString(1)
  
  def setLabel(self,  value):
    # type: (str) -> None
    self._setString(1, value)
    
  def getValue(self):
    # type: () -> str
    return self._getString(2)
  
  def setValue(self, value):
    # type: (str) -> None
    self._setString(2, value)
    
  def getInputType(self):
    # type: () -> str
    return self._getString(3)
  
  def setInputType(self, value):
    # type: (str) -> None
    self._setString(3, value)

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
  
  def _addLine(self, line):
    # type: (Line) -> None
    lines = self.getLines()
    lines.addViewModel(line)
    lines.invalidate()
    
  def addTextLine(self, text):
    # type: (str) -> None
    line = TextLine()
    line.setText(text)
    self._addLine(line)
    return line
    
  def addButtonLine(self, label, buttonText, onClickCallback):
    # type: (str, str, Callable) -> None
    line = ButtonLine()
    line.setLabel(label)
    line.setButtonText(buttonText)
    self._addLine(line)
    line.onButtonClick += onClickCallback
    return line
  
  def addCheckboxLine(self, label, isChecked=False, checkboxType=CheckboxLine.CheckboxType.DEFAULT, onToggleCallback=None):
    # type: (str, bool, str, Callable) -> None
    line = CheckboxLine()
    line.setLabel(label)
    line.setIsChecked(isChecked)
    line.setCheckboxType(checkboxType)
    self._addLine(line)
    if onToggleCallback is not None:
      line.onToggle += onToggleCallback
    return line
  
  def addValueLine(self, label, value):
    # type: (str, str) -> None
    line = ValueLine()
    line.setLabel(label)
    line.setValue(value)
    self._addLine(line)
    return line
  
  def addSeparatorLine(self):
    # type: () -> None
    line = SeparatorLine()
    self._addLine(line)
    return line
  
  def addInputLine(self, label, value='', inputType=InputLine.InputType.TEXT, onChangeCallback=None):
    # type: (str, str, str, Callable) -> None
    line = InputLine()
    line.setLabel(label)
    line.setValue(value)
    line.setInputType(inputType)
    self._addLine(line)
    if onChangeCallback is not None:
      line.onChange += onChangeCallback
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
    