import Keys
import BigWorld

from gui import InputHandler
from gui.app_loader.settings import APP_NAME_SPACE
try: from GUI import WGMarkerPositionController as MarkerPositionController
except ImportError: from GUI import MarkerPositionController
from skeletons.gui.impl import IGuiLoader
from helpers import dependency
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus

try: from openwg_gameface import res_id_by_key
except ImportError: pass

from .DebugView import WotstatDebugWindow, WOTSTAT_DEBUG_UTILS_VIEW
from .Logger import Logger, SimpleLoggerBackend
from gui.debugUtils import ui as uiController

from .coreUtils.mainUtils import MainUtils
from .coreUtils.replaysUtils import ReplaysUtils
from .coreUtils.freeCamera import FreeCameraUtils
from .coreUtils.shootingUtils import ShootingUtils
from .coreUtils.spottingUtils import SpottingUtils

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
    
    g_eventBus.addListener(events.AppLifeCycleEvent.INITIALIZED, self.onAppInitialized, EVENT_BUS_SCOPE.GLOBAL)
    
    InputHandler.g_instance.onKeyUp += self.__handleKeyUpEvent
    self.utils = [
      MainUtils(),
      ShootingUtils(),
      SpottingUtils(),
      ReplaysUtils(),
      FreeCameraUtils()
    ]

  def dispose(self):
    logger.info("Stopping WotstatDebugUtils")
    g_eventBus.removeListener(events.AppLifeCycleEvent.INITIALIZED, self.onAppInitialized, EVENT_BUS_SCOPE.GLOBAL)
    InputHandler.g_instance.onKeyUp -= self.__handleKeyUpEvent
    
  def __handleKeyUpEvent(self, event):
    # type: (BigWorld.KeyEvent) -> None

    # if event.key == Keys.KEY_F11:
      # self.showWindow()uiController

    pass
    # if event.key == Keys.KEY_B:
    #   self.showWindow()
    
  def showWindow(self):
    uiLoader = dependency.instance(IGuiLoader) # type: IGuiLoader
    view = uiLoader.windowsManager.getViewByLayoutID(res_id_by_key(WOTSTAT_DEBUG_UTILS_VIEW))
    if view: view.getWindow().destroy()
      
    WotstatDebugWindow().load()

  def onAppInitialized(self, event):
    if event.ns == APP_NAME_SPACE.SF_LOBBY:
      self.showWindow()
    elif event.ns == APP_NAME_SPACE.SF_BATTLE:
      self.showWindow()