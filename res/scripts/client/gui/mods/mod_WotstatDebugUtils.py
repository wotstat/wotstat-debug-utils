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

#print(ui)


#panel = ui.createPanel('test1')
#textLine = panel.addTextLine('textLine')
#print(line.setText('132436'))
#print(panel1)

#def onClick():
#   print('onClick')
#   
#def onCheckBoxToggle(value):
#   print('onCheckBoxToggle')
#   print(value)
#
#textLine = panel.addTextLine('textLine')
#btnLine = panel.addButtonLine('btnLine', 'label', onClick)
#checkBox = panel.addCheckboxLine('checkBox defalt')
#checkBoxVisibility = panel.addCheckboxLine('checkBox visibility', checkboxType='visibility')
#valueLine = panel.addValueLine('valueLine', 'val123')
#separatorLine = panel.addSeparatorLine()
#inputLine = panel.addInputLine('inputLine', value='value', inputType='text')
#inputLineNum = panel.addInputLine('inputLine num', value='134', inputType='numeric')


#checkBox.onCheckBoxToggle += onCheckBoxToggle
#checkBox.setIsChecked(False)
#print(checkBox.getIsChecked())

#checkBox.setIsChecked(True)

#btn.setButtonLabel('btn label')
#btn.setText('Test')

#panel7.remove()
