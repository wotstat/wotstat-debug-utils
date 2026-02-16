from gui.debugUtils import ui
from .projectileUtils.ProjectileUtil import ProjectileUtil
from .AimingUtil import AimingUtil

class ShootingUtils(object):
  
  def __init__(self):
    self.panel = ui.createPanel('Shooting utils')
    self.aimingUtil = AimingUtil(self.panel)
    self.projectileUtil = ProjectileUtil(self.panel)
    