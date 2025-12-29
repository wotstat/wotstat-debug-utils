from gui.debugUtils import ui
from .Raycast import RaycastUtil

class MainUtils(object):
  
  def __init__(self):
    self.panel = ui.createPanel('Main utils')
    self.raycastUtil = RaycastUtil(self.panel)
    