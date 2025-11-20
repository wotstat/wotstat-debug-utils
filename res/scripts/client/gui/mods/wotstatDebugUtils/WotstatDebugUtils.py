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

from .DebugView import WotstatDebugWindow, WOTSTAT_DEBUG_UTILS_VIEW, DebugViewModel, DebugView
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
    from skeletons.gui.impl import IGuiLoader
    from helpers import dependency
    from openwg_gameface import res_id_by_key
    import Math

    uiLoader = dependency.instance(IGuiLoader)
    view = uiLoader.windowsManager.getViewByLayoutID(res_id_by_key('WOTSTAT_DEBUG_UTILS_VIEW')) # type: DebugView

    
    if event.key == Keys.KEY_V:
      self.showWindow()
      
    if not view: return
    
    if event.key == Keys.KEY_4:
      view.setupMarker(view.createMarker(), position=Math.Vector3(0, 0, 5), size=10, color="#77FF08", text='(0, 0, 0)')
    if event.key == Keys.KEY_5:
      for y in range(20): view.setupMarker(view.createMarker(), position=Math.Vector3(5, y / 5.0, 5))
    elif event.key == Keys.KEY_6:
      for y in range(20): 
        view.setupMarker(view.createMarker(), Math.Vector3(0, y / 5.0, 0))
        view.setupMarker(view.createMarker(), Math.Vector3(0, y / 5.0, 5))
        view.setupMarker(view.createMarker(), Math.Vector3(5, y / 5.0, 0))
        view.setupMarker(view.createMarker(), Math.Vector3(5, y / 5.0, 5))
    elif event.key == Keys.KEY_7:
      for y in range(40): 
        view.setupMarker(view.createMarker(), Math.Vector3(0, y / 5.0, 0))
        view.setupMarker(view.createMarker(), Math.Vector3(0, y / 5.0, 5))
        view.setupMarker(view.createMarker(), Math.Vector3(5, y / 5.0, 0))
        view.setupMarker(view.createMarker(), Math.Vector3(5, y / 5.0, 5))
    elif event.key == Keys.KEY_8:
      
      form = "<div class='line'>m: {} <b>{}</b></div>"
      
      for y in range(20): 
        view.setupMarker(view.createMarker(), Math.Vector3(0, y / 3.0, 0), text=form.format(y * 4, '(0, %.2f, 0)' % (y / 3.0)))
        view.setupMarker(view.createMarker(), Math.Vector3(0, y / 3.0, 5), text=form.format(y * 4 + 1, '(0, %.2f, 5)' % (y / 3.0)))
        view.setupMarker(view.createMarker(), Math.Vector3(5, y / 3.0, 0), text=form.format(y * 4 + 2, '(5, %.2f, 0)' % (y / 3.0)))
        view.setupMarker(view.createMarker(), Math.Vector3(5, y / 3.0, 5), text=form.format(y * 4 + 3, '(5, %.2f, 5)' % (y / 3.0)))
    
  def showWindow(self):
    uiLoader = dependency.instance(IGuiLoader) # type: IGuiLoader
    view = uiLoader.windowsManager.getViewByLayoutID(res_id_by_key(WOTSTAT_DEBUG_UTILS_VIEW))
    if view: view.getWindow().destroy()
      
    WotstatDebugWindow().load()
    