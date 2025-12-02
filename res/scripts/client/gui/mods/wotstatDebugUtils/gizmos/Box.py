import typing
import Math

if typing.TYPE_CHECKING:
  from typing import Tuple, Optional
  from .GizmosController import GizmosController

class Box(object):
  def __init__(self, controller):
    # type: (GizmosController) -> None
    self._controller = controller
    self._width = None # type: Optional[float]
    self._color = None # type: Optional[int]
    self._p0 = None # type: Optional[Tuple[float, float, float]]
    self._p1 = None # type: Optional[Tuple[float, float, float]]
    self._p2 = None # type: Optional[Tuple[float, float, float]]
    self._p3 = None # type: Optional[Tuple[float, float, float]]
    self._p4 = None # type: Optional[Tuple[float, float, float]]
    self._p5 = None # type: Optional[Tuple[float, float, float]]
    self._p6 = None # type: Optional[Tuple[float, float, float]]
    self._p7 = None # type: Optional[Tuple[float, float, float]]
    
  @property
  def width(self):
    return self._width
  
  @property
  def color(self):
    return self._color
  
  @property
  def p0(self): return self._p0
  @property
  def p1(self): return self._p1
  @property
  def p2(self): return self._p2
  @property
  def p3(self): return self._p3
  @property 
  def p4(self): return self._p4
  @property
  def p5(self): return self._p5
  @property
  def p6(self): return self._p6
  @property
  def p7(self): return self._p7

  @width.setter
  def width(self, value): 
    self._setup(width=value)
  
  @color.setter
  def color(self, value): 
    self._setup(color=value)
    
  @p0.setter
  def p0(self, value): self._setup(p0=value)
  @p1.setter
  def p1(self, value): self._setup(p1=value)
  @p2.setter
  def p2(self, value): self._setup(p2=value)
  @p3.setter
  def p3(self, value): self._setup(p3=value)
  @p4.setter
  def p4(self, value): self._setup(p4=value)
  @p5.setter
  def p5(self, value): self._setup(p5=value)
  @p6.setter
  def p6(self, value): self._setup(p6=value)
  @p7.setter
  def p7(self, value): self._setup(p7=value)
  
  
  def _setup(self, width=None, color=None,
             p0=None, p1=None, p2=None, p3=None, p4=None, p5=None, p6=None, p7=None):
    if width is not None: self._width = width
    if color is not None: self._color = color
    if p0 is not None: self._p0 = p0
    if p1 is not None: self._p1 = p1
    if p2 is not None: self._p2 = p2
    if p3 is not None: self._p3 = p3
    if p4 is not None: self._p4 = p4
    if p5 is not None: self._p5 = p5
    if p6 is not None: self._p6 = p6
    if p7 is not None: self._p7 = p7
    self._controller._setupBox(self)
    
  def from8PointsArray(self, points):
    if len(points) != 8:
      raise ValueError("points must be an array of 8 elements")
    self._setup(
      p0=points[0], p1=points[1], p2=points[2], p3=points[3],
      p4=points[4], p5=points[5], p6=points[6], p7=points[7]
    )
    
  def from8Points(self, p0, p1, p2, p3, p4, p5, p6, p7):
    self._setup(p0=p0, p1=p1, p2=p2, p3=p3, p4=p4, p5=p5, p6=p6, p7=p7)
    
  def fromCenterSizeRotationMatrix(self, center, w, h, d, rotationMatrix):
    # type: (Math.Vector3, float, float, float, Math.Matrix) -> None
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
    
    worldPoints = [rotationMatrix.applyVector(p) + center for p in localPoints]
    self.from8PointsArray(worldPoints)
    
  def fromCenterSizeRotation(self, center, w, h, d, rotationX=0, rotationY=0, rotationZ=0):
    rotMat = Math.Matrix() # type: Math.Matrix
    rotMat.setRotateYPR((rotationY, rotationX, rotationZ))
    self.fromCenterSizeRotationMatrix(center, w, h, d, rotMat)
  
  def from4CornerPoints(self, zero, right, up, forward):
    p0 = zero
    p1 = right
    p3 = up
    p4 = forward
    
    w = (p1 - p0)
    h = (p3 - p0)
    d = (p4 - p0)
    
    p2 = p1 + h
    p4 = p0 + d
    p5 = p4 + w
    p6 = p5 + h
    p7 = p3 + d
    
    self.from8Points(p0, p1, p2, p3, p4, p5, p6, p7)
  
  def destroy(self):
    # type: () -> None
    self._controller._destroyBox(self)
    