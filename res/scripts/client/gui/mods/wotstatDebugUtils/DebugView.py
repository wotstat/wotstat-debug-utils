from frameworks.wulf import ViewModel
from gui.impl.pub import ViewImpl, WindowImpl
from frameworks.wulf import WindowFlags, ViewSettings, ViewFlags
from skeletons.gui.impl import IGuiLoader
from helpers import dependency
from openwg_gameface import ModDynAccessor, gf_mod_inject

from .Logger import Logger
  
WOTSTAT_DEBUG_UTILS_VIEW = 'WOTSTAT_DEBUG_UTILS_VIEW'

logger = Logger.instance()

class WorldPositionModel(ViewModel):

  def __init__(self, properties=6, commands=0):
    # type: (int, int) -> None
    super(WorldPositionModel, self).__init__(properties=properties, commands=commands)
    
  def _initialize(self):
    # type: () -> None
    super(WorldPositionModel, self)._initialize()
    self._addRealProperty('posx', 0.0)
    self._addRealProperty('posy', 0.0)
    self._addRealProperty('scale', 0.0)
    self._addRealProperty('ndcLimitX', 2.0)
    self._addRealProperty('ndcLimitY', 2.0)
    self._addBoolProperty('isVisible', False)
    
  def setPosx(self, value):
    # type: (float) -> None
    self._setReal(0, value)
    
  def getPosx(self):
    # type: () -> float
    return self._getReal(0)
  
  def setPosy(self, value):
    # type: (float) -> None
    self._setReal(1, value)
    
  def getPosy(self):
    # type: () -> float
    return self._getReal(1)
  
  def setScale(self, value):
    # type: (float) -> None
    self._setReal(2, value)
    
  def getScale(self):
    # type: () -> float
    return self._getReal(2)
  
  def setNdcLimitX(self, value):
    # type: (float) -> None
    self._setReal(3, value)
    
  def getNdcLimitX(self):
    # type: () -> float
    return self._getReal(3)
  
  def setNdcLimitY(self, value):
    # type: (float) -> None
    self._setReal(4, value)
    
  def getNdcLimitY(self):
    # type: () -> float
    return self._getReal(4)
  
  def setIsVisible(self, value):
    # type: (bool) -> None
    self._setBool(5, value)
    
  def getIsVisible(self):
    # type: () -> bool
    return self._getBool(5)


class DebugViewModel(ViewModel):
  
  def __init__(self, properties=2, commands=0):
    # type: (int, int) -> None
    super(DebugViewModel, self).__init__(properties=properties, commands=commands)
  
  def _initialize(self):
    # type: () -> None
    super(DebugViewModel, self)._initialize()
    self._addStringProperty('foo', '')
    self._addViewModelProperty('demoPosition', WorldPositionModel())
  
  def setFoo(self, value):
    # type: (str) -> None
    self._setString(0, value)
    
  def getFoo(self):
    # type: () -> str
    return self._getString(0)
  
  def setDemoPosition(self, value):
    # type: (WorldPositionModel) -> None
    self._setViewModel(1, value)
  
  def getDemoPosition(self):
    # type: () -> WorldPositionModel
    return self._getViewModel(1)
  

class DebugView(ViewImpl):
  
  viewLayoutID = ModDynAccessor(WOTSTAT_DEBUG_UTILS_VIEW)
  
  def __init__(self):
    settings = ViewSettings(DebugView.viewLayoutID(), flags=ViewFlags.VIEW, model=DebugViewModel())
    super(DebugView, self).__init__(settings)

  @property
  def viewModel(self):
    # type: () -> DebugViewModel
    return super(DebugView, self).getViewModel()

  def _finalize(self):
    # type: () -> None
    super(DebugView, self)._finalize()


def get_parent_window():
  ui_loader = dependency.instance(IGuiLoader)
  if ui_loader and ui_loader.windowsManager:
      return ui_loader.windowsManager.getMainWindow()
  return None

class WotstatDebugWindow(WindowImpl):
  
  def __init__(self):
    super(WotstatDebugWindow, self).__init__(
      wndFlags=WindowFlags.WINDOW, content=DebugView(), parent=get_parent_window()
    )
