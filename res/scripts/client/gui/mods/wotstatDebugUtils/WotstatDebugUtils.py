import Keys
import Math
import BigWorld

from gui import  InputHandler
try: from GUI import WGMarkerPositionController as MarkerPositionController
except ImportError: from GUI import MarkerPositionController
from skeletons.gui.impl import IGuiLoader
from helpers import dependency

try: from openwg_gameface import res_id_by_key
except ImportError: pass

from .DebugView import WotstatDebugWindow, WOTSTAT_DEBUG_UTILS_VIEW, DebugViewModel
from .Logger import Logger, SimpleLoggerBackend

DEBUG_MODE = '{{DEBUG_MODE}}'
VERSION = '{{VERSION}}'

logger = Logger.instance()
markerCtrl = MarkerPositionController() # type: MarkerPositionController

class WotstatDebugUtils(object):
  
  def __init__(self):
    logger.info("Starting WotstatDebugUtils v%s" % VERSION)
    logger.setup([
      SimpleLoggerBackend(prefix="[MOD_WOTSTAT_DEBUG_UTILS]", minLevel="INFO" if not DEBUG_MODE else "DEBUG"),
    ])
    
    try:
      from openwg_gameface import ModDynAccessor, gf_mod_inject
    except ImportError:
      logger.error("openwg_gameface module is not available, cannot inject CDPView")
      return
    
    
    InputHandler.g_instance.onKeyUp += self.__handleKeyUpEvent

  def dispose(self):
    logger.info("Stopping WotstatDebugUtils")
    
  def __handleKeyUpEvent(self, event):
    # type: (BigWorld.KeyEvent) -> None
    
    if event.key != Keys.KEY_V: return
    self.showWindow()
    
  def showWindow(self):
    uiLoader = dependency.instance(IGuiLoader) # type: IGuiLoader
    view = uiLoader.windowsManager.getViewByLayoutID(res_id_by_key(WOTSTAT_DEBUG_UTILS_VIEW))
    if view:
      view.getWindow().destroy()
      
    WotstatDebugWindow().load()
    
    def setupMarkerCtrl():
      view = uiLoader.windowsManager.getViewByLayoutID(res_id_by_key(WOTSTAT_DEBUG_UTILS_VIEW))
      if view:
        debugViewModel = view.getViewModel() # type: DebugViewModel
        pos = debugViewModel.getDemoPosition()
        if BigWorld.player(): markerCtrl.add(pos.proxy, BigWorld.player().position)
        else: markerCtrl.add(pos.proxy, Math.Vector3(0,0,0))
        
    BigWorld.callback(0.1, setupMarkerCtrl)
    