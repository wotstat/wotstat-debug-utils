from Event import SafeEvent
from .DebugView import onDebugViewLoaded, onDebugViewUnloaded, DebugView

from .models.UiModel import Panel

import typing
  
class UiController:
  
  def __init__(self):
    global onDebugViewLoaded, onDebugViewUnloaded
    self.panels = [] # type: typing.List[Panel]
    self.panelIndexes = {} # type: typing.Dict[Panel, int]
    self.currentDebugView = None # type: DebugView
    onDebugViewLoaded += self.onDebugViewLoaded
    onDebugViewUnloaded += self.onDebugViewUnloaded
  
  def onDebugViewLoaded(self, debugView):
    # type: (DebugView) -> None
    self.currentDebugView = debugView
    
    panels = debugView.viewModel.getUi().getPanels()
    for panel in self.panels:
      panels.addViewModel(panel)
    panels.invalidate()
      
  def onDebugViewUnloaded(self, debugView):
    # type: (DebugView) -> None
    if self.currentDebugView != debugView: return
    self.currentDebugView = None
      
  def removePanel(self, panel):
    # type: (Panel) -> None
    
    if panel not in self.panels: return
    
    self.panels.remove(panel)
    
    panelIndex = self.panelIndexes.get(panel, None)
    if panelIndex is not None and self.currentDebugView:
      panels = self.currentDebugView.viewModel.getUi().getPanels()
      panels.remove(panelIndex)
      panels.invalidate()
      
      del self.panelIndexes[panel]
      
      for i in range(panelIndex, len(self.panels)):
        self.panelIndexes[self.panels[i]] = i
  
  def createPanel(self, panelName):
    # type: (str) -> Panel
    panel = Panel(panelName)
    self.panels.append(panel)
    self.panelIndexes[panel] = len(self.panels) - 1
    
    if self.currentDebugView:
      panels = self.currentDebugView.viewModel.getUi().getPanels()
      panels.addViewModel(panel)
      panels.invalidate()
      
      
    return panel