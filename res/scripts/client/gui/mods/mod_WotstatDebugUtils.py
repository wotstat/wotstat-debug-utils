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
# from skeletons.gui.impl import IGuiLoader
# from helpers import dependency
# from openwg_gameface import res_id_by_key
# import Math

# uiLoader = dependency.instance(IGuiLoader)
# view = uiLoader.windowsManager.getViewByLayoutID(res_id_by_key('WOTSTAT_DEBUG_UTILS_VIEW'))

# for y in range(62):
#     i = view.createMarker()
#     view.setMarkerPosition(i, Math.Vector3(5,y/8.0,5))
# #view.destroyMarker(0)




# from gui.debugUtils import ui

#panel = ui.createPanel('test3')
#
#def onClick():
#   print('onClick')
#   
#def onCheckBoxToggle(value):
#   print('onCheckBoxToggle', value)
#   
#def onInput(value):
#   print('onInput', value)
#
#textLine = panel.addTextLine('textLine')
#btnLine = panel.addButtonLine('btnLine', 'label', onClick)
#checkBox = panel.addCheckboxLine('checkBox defalt', onToggleCallback=onCheckBoxToggle)
#valueLine = panel.addValueLine('valueLine', 'val123')
#separatorLine = panel.addSeparatorLine()
#inputLine = panel.addTextInputLine('inputLine', value='value', onChangeCallback=onInput)
#inputNum = panel.addNumberInputLine('numberInput', value=1, onChangeCallback=onInput)