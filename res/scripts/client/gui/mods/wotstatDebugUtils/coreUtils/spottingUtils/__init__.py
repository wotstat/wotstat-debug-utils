from gui.debugUtils import ui
from .SpottingUtil import SpottingUtil

class SpottingUtils(object):
  
  def __init__(self):
    self.panel = ui.createPanel('Spotting utils')
    self.spottingUtil = SpottingUtil(self.panel)
    