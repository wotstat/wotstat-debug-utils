from ..mods.wotstatDebugUtils.ui.UiController import UiController
from ..mods.wotstatDebugUtils.gizmos.GizmosController import GizmosController
from ..mods.wotstatDebugUtils.drawer.DrawerController import DrawerController
from ..mods.wotstatDebugUtils.gizmos.models.LineModel import LineEnd
from ..mods.wotstatDebugUtils.utils import cssToHexColor

gizmos = GizmosController()
ui = UiController()
drawer = DrawerController()

class NiceColors:
  BLACK = '#000000'
  BLUE = '#0A84FF'
  GREEN = '#30D158'
  INDIGO = '#5E5CE6'
  ORANGE = '#FF9F0A'
  PINK = '#FF375F'
  PURPLE = '#BF5AF2'
  RED = '#FF453A'
  TEAL = '#64D2FF'
  YELLOW = '#FFD60A'

class NiceColorsHex:
  BLACK = cssToHexColor(NiceColors.BLACK)
  BLUE = cssToHexColor(NiceColors.BLUE)
  GREEN = cssToHexColor(NiceColors.GREEN)
  INDIGO = cssToHexColor(NiceColors.INDIGO)
  ORANGE = cssToHexColor(NiceColors.ORANGE)
  PINK = cssToHexColor(NiceColors.PINK)
  PURPLE = cssToHexColor(NiceColors.PURPLE)
  RED = cssToHexColor(NiceColors.RED)
  TEAL = cssToHexColor(NiceColors.TEAL)
  YELLOW = cssToHexColor(NiceColors.YELLOW)
  
LineEnd = LineEnd