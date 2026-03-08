from gui.debugUtils import ui
from .RaycastUtil import RaycastUtil
from .PhysicsUtil import PhysicsUtil
from .BboxUtil import BboxUtil
from ...Restriction import Restriction

from ...i18n import t

class MainUtils(object):
  
  def __init__(self):
    self.panel = ui.createPanel(t('section.mainUtils'))
    self.raycastUtil = RaycastUtil(self.panel)
    self.physicsUtil = PhysicsUtil(self.panel)
    self.bboxUtil = BboxUtil(self.panel)
    Restriction.instance().onRestrictionChange += self.onRestrictionChange

  def onRestrictionChange(self, allowed):
    self.panel.enabled = allowed
    self.raycastUtil.cleanup()
    self.bboxUtil.cleanup()
    