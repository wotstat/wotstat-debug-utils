from gui.debugUtils import ui
from .RaycastUtil import RaycastUtil
from .PhysicsUtil import PhysicsUtil

class MainUtils(object):
  
  def __init__(self):
    self.panel = ui.createPanel('Main utils')
    self.raycastUtil = RaycastUtil(self.panel)
    self.physicsUtil = PhysicsUtil(self.panel)
    