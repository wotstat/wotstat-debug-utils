import Math

from frameworks.wulf import ViewModel
from .WorldPositionModel import OffscreenWorldPositionModel

from ..MarkersManager import IMarkerManageable
import typing
if typing.TYPE_CHECKING:
  try: from GUI import WGMarkerPositionController as MarkerPositionController
  except ImportError: from GUI import MarkerPositionController

class BoxModel(ViewModel, IMarkerManageable):
  def __init__(self, properties=10, commands=0):
    # type: (int, int) -> None
    super(BoxModel, self).__init__(properties=properties, commands=commands)
  
  def _initialize(self):
    # type: () -> None
    super(BoxModel, self)._initialize()
    self._addRealProperty('width', 1.0)
    self._addStringProperty('color', "#00AAFF")
    self._addViewModelProperty('p0', OffscreenWorldPositionModel())
    self._addViewModelProperty('p1', OffscreenWorldPositionModel())
    self._addViewModelProperty('p2', OffscreenWorldPositionModel())
    self._addViewModelProperty('p3', OffscreenWorldPositionModel())
    self._addViewModelProperty('p4', OffscreenWorldPositionModel())
    self._addViewModelProperty('p5', OffscreenWorldPositionModel())
    self._addViewModelProperty('p6', OffscreenWorldPositionModel())
    self._addViewModelProperty('p7', OffscreenWorldPositionModel())
    
  def getWidth(self):
    # type: () -> float
    return self._getReal(0)
  
  def setWidth(self, value):
    # type: (float) -> None
    self._setReal(0, value)
    
  def getColor(self):
    # type: () -> str
    return self._getString(1)
  
  def setColor(self, value):
    # type: (str) -> None
    self._setString(1, value)
    
  def getPoint(self, index):
    # type: (int) -> OffscreenWorldPositionModel
    return self._getViewModel(2 + index)
  
  def setPoint(self, index, value):
    # type: (int, OffscreenWorldPositionModel) -> None
    self._setViewModel(2 + index, value)
  
  def destroy(self, markerCtrl):
    for i in range(8):
      self.getPoint(i).detach(markerCtrl)
      
  def setup(self, markerCtrl, width=None, color=None, 
      center=None, w=None, h=None, d=None, rotationX=None, rotationY=None, rotationZ=None, rotationMatrix=None,
      point0=None, point1=None, point2=None, point3=None):
    # type: (MarkerPositionController, float, str, Math.Vector3, float, float, float, float, float, float, Math.Matrix33, Math.Vector3, Math.Vector3, Math.Vector3, Math.Vector3) -> None

    with self.transaction() as (tx):
      
      if center is not None and w is not None and h is not None and d is not None:
        # Setup by center, dimensions and rotation
        rx = rotationX if rotationX is not None else 0.0
        ry = rotationY if rotationY is not None else 0.0
        rz = rotationZ if rotationZ is not None else 0.0
        
        if rotationMatrix is not None:
          rotMat = rotationMatrix
        else:
          rotMat = Math.Matrix() # type: Math.Matrix
          rotMat.setRotateYPR((ry, rx, rz))
        
        halfW = w / 2.0
        halfH = h / 2.0
        halfD = d / 2.0
        
        localPoints = [
          Math.Vector3(-halfW, -halfH, -halfD),
          Math.Vector3( halfW, -halfH, -halfD),
          Math.Vector3( halfW,  halfH, -halfD),
          Math.Vector3(-halfW,  halfH, -halfD),
          Math.Vector3(-halfW, -halfH,  halfD),
          Math.Vector3( halfW, -halfH,  halfD),
          Math.Vector3( halfW,  halfH,  halfD),
          Math.Vector3(-halfW,  halfH,  halfD),
        ]
        
        for i in range(8):
          worldPos = rotMat.applyVector(localPoints[i]) + center
          tx.getPoint(i).attach(markerCtrl, worldPos)
          
      elif point0 is not None and point1 is not None and point2 is not None and point3 is not None:
        # Setup by 4 corner points (the rest are calculated)
        p0 = point0
        p1 = point1
        p2 = point2
        p3 = point3
        
        u = (p1 - p0)
        v = (p3 - p0)
        p4 = p0 + u + v
        p5 = p1 + v
        p6 = p2 + u
        p7 = p3 + u + v
        
        points = [p0, p1, p2, p3, p4, p5, p6, p7]
        for i in range(8):
          tx.getPoint(i).attach(markerCtrl, points[i])
      
      if width is not None:
        tx.setWidth(width)
        
      if color is not None:
        tx.setColor(color)