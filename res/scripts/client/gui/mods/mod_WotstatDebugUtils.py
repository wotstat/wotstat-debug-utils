try:
  import openwg_gameface
except ImportError:
  import logging
  logger = logging.getLogger()
  logger.error('\n' +
                  '!!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!\n'
                  '!!!\n'
                  '!!!   WotStat Debug Utils mod requires the openwg_gameface module to function.\n'
                  '!!!   Without it, this and other GF UI mods will not work correctly.\n'
                  '!!!   Please download and install it from: https://gitlab.com/openwg/wot.gameface/-/releases/\n'
                  '!!!\n'
                  '!!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!\n')

  import sys
  sys.exit()
  
from .wotstatDebugUtils.WotstatDebugUtils import WotstatDebugUtils

debugUtils = WotstatDebugUtils()

def fini():
  debugUtils.dispose()
  
  

# from gui.mods.wotstatDebugUtils.DebugView import WotstatDebugWindow

# from frameworks.wulf import WindowFlags, WindowLayer
# from gui.impl.pub import ViewImpl, WindowImpl
# from skeletons.gui.impl import IGuiLoader
# from skeletons.gui.app_loader import IAppLoader
# from helpers import dependency
# from openwg_gameface import res_id_by_key

# from GUI import WGMarkerPositionController
# import Math

# uiLoader = dependency.instance(IGuiLoader)


# def loadWindow():
#     uiLoader = dependency.instance(IGuiLoader)
#     view = uiLoader.windowsManager.getViewByLayoutID(res_id_by_key('WOTSTAT_DEBUG_UTILS_VIEW'))
#     if view:
#         window = view.getWindow()
#         window.destroy()
#     window = WotstatDebugWindow()
#     print(window)
#     BigWorld.callback(0, lambda: window.load())

# #loadWindow()
# view = uiLoader.windowsManager.getViewByLayoutID(res_id_by_key('WOTSTAT_DEBUG_UTILS_VIEW'))
# #print(view.getWindow().move(400, 200))

# #print(view.getViewModel().getDemoPosition().setNdcLimitY(13))

# markerCtrl = WGMarkerPositionController()
# markerCtrl.clear()
# markerCtrl.add(view.getViewModel().getDemoPosition().proxy, Math.Vector3(20,0,0))