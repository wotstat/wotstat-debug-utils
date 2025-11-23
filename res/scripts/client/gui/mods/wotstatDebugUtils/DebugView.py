import typing
import Math
from frameworks.wulf import WindowFlags, ViewSettings, ViewFlags
from gui.impl.pub import ViewImpl, WindowImpl
from skeletons.gui.impl import IGuiLoader
from helpers import dependency
from openwg_gameface import ModDynAccessor, gf_mod_inject
try: from GUI import WGMarkerPositionController as MarkerPositionController
except ImportError: from GUI import MarkerPositionController

from .Logger import Logger
from .models.DebugViewModel import DebugViewModel
from .MarkersManager import MarkersManager
  
WOTSTAT_DEBUG_UTILS_VIEW = 'WOTSTAT_DEBUG_UTILS_VIEW'

logger = Logger.instance()


class DebugView(ViewImpl):
  
  viewLayoutID = ModDynAccessor(WOTSTAT_DEBUG_UTILS_VIEW)
  
  def __init__(self):
    settings = ViewSettings(DebugView.viewLayoutID(), flags=ViewFlags.VIEW, model=DebugViewModel())
    super(DebugView, self).__init__(settings)
    
    self.markersCtrl = MarkerPositionController() # type: MarkerPositionController
    self.pointMarkersManager = MarkersManager(self.markersCtrl, self.viewModel.getMarkersType(), self.viewModel.getMarkers())
    self.lineMarkersManager = MarkersManager(self.markersCtrl, self.viewModel.getLinesType(), self.viewModel.getLines())


  @property
  def viewModel(self):
    # type: () -> DebugViewModel
    return super(DebugView, self).getViewModel()

  def _finalize(self):
    super(DebugView, self)._finalize()
    
  def createMarker(self):
    return self.pointMarkersManager.create()
  
  def destroyMarker(self, markerID):
    return self.pointMarkersManager.destroy(markerID)
    
  def setupMarker(self, markerID, position=None, size=None, color=None, text=None):
    self.pointMarkersManager.setup(markerID, position, size, color, text)
    
  def createLine(self):
    return self.lineMarkersManager.create()
  
  def destroyLine(self, lineID):
    return self.lineMarkersManager.destroy(lineID)
  
  def setupLine(self, lineID, p1=None, p2=None, width=None, color=None, end1=None, end2=None):
    self.lineMarkersManager.setup(lineID, p1, p2, width, color, end1, end2)


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
