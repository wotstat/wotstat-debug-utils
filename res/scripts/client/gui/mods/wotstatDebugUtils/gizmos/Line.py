import typing

if typing.TYPE_CHECKING:
  from typing import Tuple, Optional
  from .GizmosController import GizmosController

class Line(object):
  def __init__(self, controller):
    # type: (GizmosController) -> None
    self._controller = controller
    self._p1 = None
    self._p2 = None
    self._width = None # type: Optional[float]
    self._color = None # type: Optional[int]
    self._end1 = None # type: Optional[str]
    self._end2 = None # type: Optional[str]

  @property
  def p1(self):
    # type: () -> Optional[Tuple[float, float, float]]
    return self._p1
  
  @property
  def p2(self):
    # type: () -> Optional[Tuple[float, float, float]]
    return self._p2
  
  @property
  def width(self):
    # type: () -> Optional[float]
    return self._width
  
  @property
  def color(self):
    # type: () -> Optional[int]
    return self._color
  
  @property
  def end1(self):
    # type: () -> Optional[str]
    return self._end1
  
  @property
  def end2(self):
    # type: () -> Optional[str]
    return self._end2
  
  @p1.setter
  def p1(self, value):
    # type: (Optional[Tuple[float, float, float]]) -> None
    self._setup(p1=value)
    
  @p2.setter
  def p2(self, value):
    # type: (Optional[Tuple[float, float, float]]) -> None
    self._setup(p2=value)
    
  @width.setter
  def width(self, value):
    # type: (Optional[float]) -> None
    self._setup(width=value)
    
  @color.setter
  def color(self, value):
    # type: (Optional[int]) -> None
    self._setup(color=value)
    
  @end1.setter
  def end1(self, value):
    # type: (Optional[str]) -> None
    self._setup(end1=value)
    
  @end2.setter
  def end2(self, value):
    # type: (Optional[str]) -> None
    self._setup(end2=value)
    
  def _setup(self, p1=None, p2=None, width=None, color=None, end1=None, end2=None):
    # type: (typing.Optional[typing.Tuple[float, float, float]], typing.Optional[typing.Tuple[float, float, float]], typing.Optional[float], typing.Optional[int], typing.Optional[str], typing.Optional[str]) -> None
    
    if p1 is not None: self._p1 = p1
    if p2 is not None: self._p2 = p2
    if width is not None: self._width = width
    if color is not None: self._color = color
    if end1 is not None: self._end1 = end1
    if end2 is not None: self._end2 = end2
    self._controller._setupLine(self)
    
  def destroy(self):
    # type: () -> None
    self._controller._destroyLine(self)
    