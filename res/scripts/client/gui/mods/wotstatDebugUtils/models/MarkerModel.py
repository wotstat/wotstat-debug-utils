from .WorldPositionModel import OffscreenWorldPositionModel

from ..MarkersManager import IMarkerManageable

class MarkerModel(OffscreenWorldPositionModel, IMarkerManageable):
  def __init__(self, properties=9, commands=0):
    super(MarkerModel, self).__init__(properties=properties, commands=commands)
    
  def _initialize(self):
    super(MarkerModel, self)._initialize()
  
    self._addRealProperty('size', 10)
    self._addStringProperty('color', "#00AAFF")
    self._addStringProperty('text', '')
    
  def getSize(self):
    return self._getReal(6)
  
  def setSize(self, value):
    self._setReal(6, value)
    
  def getColor(self):
    return self._getString(7)
  
  def setColor(self, value):
    self._setString(7, value)
    
  def getText(self):
    return self._getString(8)
  
  def setText(self, value):
    self._setString(8, value)
    
  def destroy(self, markerCtrl):
    self.detach(markerCtrl)
      
  def setup(self, markerCtrl, position=None, size=None, color=None, text=None):

    if position is not None:
      self.attach(markerCtrl, position)
    
    with self.transaction() as (tx):
      if size is not None:
        tx.setSize(size)
        
      if color is not None:
        tx.setColor(color)
        
      if text is not None:
        tx.setText(text)