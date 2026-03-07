from gui.debugUtils import ui
from .SpottingUtil import SpottingUtil
from ...i18n import t

class SpottingUtils(object):
  
  def __init__(self):
    self.panel = ui.createPanel(t('section.spottingUtils'))
    self.spottingUtil = SpottingUtil(self.panel)
    