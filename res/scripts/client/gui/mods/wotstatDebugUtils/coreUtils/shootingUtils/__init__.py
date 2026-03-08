from gui.debugUtils import ui
from .projectileUtils.ProjectileUtil import ProjectileUtil
from .AimingUtil import AimingUtil
from ...Restriction import Restriction
from ...i18n import t

class ShootingUtils(object):
  
  def __init__(self):
    self.panel = ui.createPanel(t('section.shootingUtils'))
    self.aimingUtil = AimingUtil(self.panel)
    self.projectileUtil = ProjectileUtil(self.panel)
    Restriction.instance().onRestrictionChange += self.onRestrictionChange
    
  def onRestrictionChange(self, allowed):
    self.panel.enabled = allowed