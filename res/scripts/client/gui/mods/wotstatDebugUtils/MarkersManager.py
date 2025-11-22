
import typing
if typing.TYPE_CHECKING:
  try: from GUI import WGMarkerPositionController as MarkerPositionController
  except ImportError: from GUI import MarkerPositionController
  from frameworks.wulf import ViewModel, Array

from .Logger import Logger

logger = Logger.instance()

class IMarkerManageable(object):
  
  def create(self):
    pass
  
  def setup(self, markersCtrl, **kwargs):
    # type: (MarkerPositionController, ...) -> None
    pass
  
  def destroy(self, markersCtrl):
    # type: (MarkerPositionController) -> None
    pass

class MarkersManager(object):
  
  def __init__(self, markersCtrl, markerType, markersArray):
    # type: (MarkerPositionController, typing.Type, Array) -> None
    self.markers = markersArray
    self.markerType = markerType
    self.markersCtrl = markersCtrl
    self.markersDict = {} # type: typing.Dict[int, any]
    self.markersIndexes = {} # type: typing.Dict[int, int]
    self._nextMarkerID = 0

  def create(self):
    markerModel = self.markerType() # type: IMarkerManageable
    self.markers.addViewModel(markerModel)
    markerID = self._nextMarkerID
    self.markersDict[markerID] = markerModel
    self.markersIndexes[markerID] = len(self.markers) - 1
    self._nextMarkerID += 1
    logger.debug("Created marker %d" % markerID)
    return markerID
  
  def destroy(self, markerID):
    if markerID not in self.markersDict:
      logger.error("Marker %d not found!" % markerID)
      return
    
    markerModel = self.markersDict[markerID] # type: IMarkerManageable
    markerModel.destroy(self.markersCtrl)
    
    markerIndex = self.markersIndexes[markerID]
    self.markers.remove(markerIndex)
    del self.markersDict[markerID]
    del self.markersIndexes[markerID]
    
    for mid, index in self.markersIndexes.items():
      if index > markerIndex:
        self.markersIndexes[mid] = index - 1
  
  def setup(self, id, *a, **kwargs):
    # type: (int, ...) -> None
    if id not in self.markersDict:
      logger.error("Marker %d not found!" % id)
      return
    
    markerModel = self.markersDict[id] # type: IMarkerManageable
    markerModel.setup(self.markersCtrl, *a, **kwargs)