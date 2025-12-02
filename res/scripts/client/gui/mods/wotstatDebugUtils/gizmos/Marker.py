import typing

if typing.TYPE_CHECKING:
  from typing import Tuple, Optional
  from .GizmosController import GizmosController

class Marker(object):
  def __init__(self, controller):
    # type: (GizmosController) -> None
    self._controller = controller
    self._position = None
    self._size = None # type: Optional[float]
    self._color = None # type: Optional[int]
    self._text = None # type: Optional[str]
    
  @property
  def position(self):
    # type: () -> Optional[Tuple[float, float, float]]
    return self._position
  
  @property
  def size(self):
    # type: () -> Optional[float]
    return self._size
  
  @property
  def color(self):
    # type: () -> Optional[int]
    return self._color
  
  @property
  def text(self):
    # type: () -> Optional[str]
    return self._text
  
  @position.setter
  def position(self, value):
    # type: (Optional[Tuple[float, float, float]]) -> None
    self._setup(position=value)
  
  @size.setter
  def size(self, value):
    # type: (Optional[float]) -> None
    self._setup(size=value)
    
  @color.setter
  def color(self, value):
    # type: (Optional[int]) -> None
    self._setup(color=value)
    
  @text.setter
  def text(self, value):
    # type: (Optional[str]) -> None
    self._setup(text=value)
    
  def _setup(self, position=None, size=None, color=None, text=None):
    # type: (Optional[Tuple[float, float, float]], Optional[float], Optional[int], Optional[str]) -> None
    if position is not None: self._position = position
    if size is not None: self._size = size
    if color is not None: self._color = color
    if text is not None: self._text = text
    self._controller._setupMarker(self)
    
  def destroy(self):
    # type: () -> None
    self._controller._destroyMarker(self)
    