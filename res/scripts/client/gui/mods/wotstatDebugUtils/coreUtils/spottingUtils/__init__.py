from gui.debugUtils import ui
from .SpottingUtil import SpottingUtil
from ...Restriction import Restriction
from ...i18n import t

class SpottingUtils(object):
  
  def __init__(self):
    self.panel = ui.createPanel(t('section.spottingUtils'))
    self.spottingUtil = SpottingUtil(self.panel)
    Restriction.instance().onRestrictionChange += self.onRestrictionChange

  def onRestrictionChange(self, allowed):
    self.panel.enabled = allowed
    self.spottingUtil.allowed = allowed