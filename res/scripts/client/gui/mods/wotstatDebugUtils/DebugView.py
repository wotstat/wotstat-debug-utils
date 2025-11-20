import typing
import Math
from frameworks.wulf import ViewModel, Array, WindowFlags, ViewSettings, ViewFlags
from gui.impl.pub import ViewImpl, WindowImpl
from skeletons.gui.impl import IGuiLoader
from helpers import dependency
from openwg_gameface import ModDynAccessor, gf_mod_inject
try: from GUI import WGMarkerPositionController as MarkerPositionController
except ImportError: from GUI import MarkerPositionController


from .Logger import Logger
  
WOTSTAT_DEBUG_UTILS_VIEW = 'WOTSTAT_DEBUG_UTILS_VIEW'

logger = Logger.instance()

class WorldPositionModel(ViewModel):

  def __init__(self, properties=4, commands=0):
    # type: (int, int) -> None
    super(WorldPositionModel, self).__init__(properties=properties, commands=commands)
    
  def _initialize(self):
    # type: () -> None
    super(WorldPositionModel, self)._initialize()
    self._addRealProperty('posx', 0.0)
    self._addRealProperty('posy', 0.0)
    self._addRealProperty('scale', 0.0)
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

  def setIsVisible(self, value):
    # type: (bool) -> None
    self._setBool(3, value)
    
  def getIsVisible(self):
    # type: () -> bool
    return self._getBool(3)

class MarkerModel(WorldPositionModel):
  def __init__(self, properties=9, commands=0):
    super(MarkerModel, self).__init__(properties=properties, commands=commands)
    
    self._addRealProperty('ndcLimitX', 2)
    self._addRealProperty('ndcLimitY', 2)
    
    self._addRealProperty('size', 10)
    self._addStringProperty('color', "#00AAFF")
    self._addStringProperty('text', '')
    
  def getSize(self):
    return self._getReal(6)
  
  def setSize(self, value):
    self._setReal(6, value)
    
  def getColor(self):
    return self._getString(7)
  
  def setColor(self, value):
    self._setString(7, value)
    
  def getText(self):
    return self._getString(8)
  
  def setText(self, value):
    self._setString(8, value)

class DebugViewModel(ViewModel):
  
  def __init__(self, properties=1, commands=0):
    # type: (int, int) -> None
    super(DebugViewModel, self).__init__(properties=properties, commands=commands)
  
  def _initialize(self):
    # type: () -> None
    super(DebugViewModel, self)._initialize()
    self._addArrayProperty('markers', Array())

  def getMarkers(self):
    # type: () -> Array
    return self._getArray(0)
  
  def setMarkers(self, value):
    # type: (Array) -> None
    self._setArray(0, value)
  
  @staticmethod
  def getMarkersType():
    return MarkerModel

class DebugView(ViewImpl):
  
  viewLayoutID = ModDynAccessor(WOTSTAT_DEBUG_UTILS_VIEW)
  
  def __init__(self):
    settings = ViewSettings(DebugView.viewLayoutID(), flags=ViewFlags.VIEW, model=DebugViewModel())
    super(DebugView, self).__init__(settings)
    
    self.markersCtrl = MarkerPositionController() # type: MarkerPositionController
    self.markers = self.viewModel.getMarkers()
    self.markersDict = {} # type: typing.Dict[int, MarkerModel]
    self.markersIndexes = {} # type: typing.Dict[int, int]
    self._nextMarkerID = 0

  @property
  def viewModel(self):
    # type: () -> DebugViewModel
    return super(DebugView, self).getViewModel()

  def _finalize(self):
    # type: () -> None
    super(DebugView, self)._finalize()
    
  def createMarker(self):
    # type: () -> int
    markerModel = self.viewModel.getMarkersType()()
    self.markers.addViewModel(markerModel)
    markerID = self._nextMarkerID
    self.markersDict[markerID] = markerModel
    self.markersIndexes[markerID] = len(self.markers) - 1
    self._nextMarkerID += 1
    self.markersCtrl.add(markerModel.proxy, Math.Vector3(0,0,0))
    logger.debug("Created marker %d" % markerID)
    return markerID
  
  def destroyMarker(self, markerID):
    # type: (int) -> None
    markerModel = self.markersDict[markerID]
    self.markersCtrl.remove(markerModel.proxy)
    
    markerIndex = self.markersIndexes[markerID]
    self.markers.remove(markerIndex)
    del self.markersDict[markerID]
    del self.markersIndexes[markerID]
    
    for mid, index in self.markersIndexes.items():
      if index > markerIndex:
        self.markersIndexes[mid] = index - 1
        
    logger.debug("Destroyed marker %d" % markerID)
    
  def setupMarker(self, markerID, position=None, size=None, color=None, text=None):
    # type: (int, Any) -> None
    
    marker = self.markersDict[markerID]
    if not marker:
      logger.error("Marker %d not found!" % markerID)
      return
    
    if position:
      self.markersCtrl.remove(self.markersDict[markerID].proxy)
      self.markersCtrl.add(self.markersDict[markerID].proxy, position)
      
    if size is not None:
      marker.setSize(size)
      
    if color is not None:
      marker.setColor(color)
      
    if text is not None:
      marker.setText(text)
      
    logger.info("Setup marker %d" % markerID)


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
