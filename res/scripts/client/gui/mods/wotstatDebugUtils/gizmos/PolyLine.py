import math
from math import pi, cos
import typing

import Math

if typing.TYPE_CHECKING:
  from typing import List, Tuple, Optional
  from .GizmosController import GizmosController

def easeInOutSine(t):
  return -(cos(pi * t) - 1) / 2

def interpolatePoints(start, end, segments, easeFunction=easeInOutSine):   
  points = []
  points.append(start)
  for i in range(1, segments):
    t = i / float(segments)
    t = easeFunction(t)
    point = start + (t * (end - start))
    points.append(point)
  points.append(end)
  return points 

class PolyLine(object):
  def __init__(self, controller):
    # type: (GizmosController) -> None
    self._controller = controller
    self._width = None # type: Optional[float]
    self._color = None # type: Optional[int]
    self._end1 = None # type: Optional[int]
    self._end2 = None # type: Optional[int]
    self._closed = None # type: Optional[bool]
    self._points = None # type: Optional[List]
    
  @property
  def points(self):
    # type: () -> Optional[List[Tuple[float, float, float]]]
    return self._points
  
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
    # type: () -> Optional[int]
    return self._end1
  
  @property
  def end2(self):
    # type: () -> Optional[int]
    return self._end2
  
  @property
  def closed(self):
    # type: () -> Optional[bool]
    return self._closed
  
  @closed.setter
  def closed(self, value):
    # type: (Optional[bool]) -> None
    self._setup(closed=value)
    
  @points.setter
  def points(self, value):
    # type: (Optional[List[Tuple[float, float, float]]]) -> None
    self._setup(points=value)
    
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
    # type: (Optional[int]) -> None
    self._setup(end1=value)
    
  @end2.setter
  def end2(self, value):
    # type: (Optional[int]) -> None
    self._setup(end2=value)
    
  def _setup(self, points=None, width=None, color=None, end1=None, end2=None, closed=None):
    # type: (Optional[List[Tuple[float, float, float]]], Optional[float], Optional[int], Optional[int], Optional[int], Optional[bool]) -> None
    if points is not None: self._points = points
    if width is not None: self._width = width
    if color is not None: self._color = color
    if end1 is not None: self._end1 = end1
    if end2 is not None: self._end2 = end2
    if closed is not None: self._closed = closed
    self._controller._setupPolyLine(self)

  def fromCircle(self, center, normal, radius, segments):
    # type: (Tuple[float, float, float], Tuple[float, float, float], float, int) -> None
    cx, cy, cz = center
    nx, ny, nz = normal

    # --- normalize the normal vector ---
    n_len = math.sqrt(nx*nx + ny*ny + nz*nz)
    if n_len == 0: raise ValueError("Normal vector must be non-zero")

    nx /= n_len
    ny /= n_len
    nz /= n_len

    # --- build an orthonormal basis (u, v, n) for the circle's plane ---
    # choose an arbitrary vector that is not parallel to n
    if abs(nx) < 0.9: ax, ay, az = 1.0, 0.0, 0.0
    else: ax, ay, az = 0.0, 1.0, 0.0

    # u = normalize(cross(n, a))
    ux = ny*az - nz*ay
    uy = nz*ax - nx*az
    uz = nx*ay - ny*ax

    u_len = math.sqrt(ux*ux + uy*uy + uz*uz)
    if u_len == 0: raise ValueError("Failed to build basis: normal may be invalid")

    ux /= u_len
    uy /= u_len
    uz /= u_len

    # v = n × u
    vx = ny*uz - nz*uy
    vy = nz*ux - nx*uz
    vz = nx*uy - ny*ux

    # --- generate points on the circle ---
    points = []
    for i in range(segments):
      angle = 2.0 * math.pi * i / segments
      ca = math.cos(angle)
      sa = math.sin(angle)

      # p = center + radius * (ca * u + sa * v)
      x = cx + radius * (ca * ux + sa * vx)
      y = cy + radius * (ca * uy + sa * vy)
      z = cz + radius * (ca * uz + sa * vz)

      points.append(Math.Vector3(x, y, z))

    self._setup(points=points, closed=True)

  def fromStartEnd(self, start, end, segments):
    # type: (Tuple[float, float, float], Tuple[float, float, float], int) -> None
    sx, sy, sz = start
    ex, ey, ez = end

    direction = Math.Vector3(ex - sx, ey - sy, ez - sz)
    length = direction.length
    if length == 0:
      raise ValueError("Start and end points must be different")

    direction.normalise()

    points = []
    points.append(Math.Vector3(sx, sy, sz))
    for i in range(1, segments):
      t = i / float(segments)
      px = sx + direction.x * length * t
      py = sy + direction.y * length * t
      pz = sz + direction.z * length * t
      points.append(Math.Vector3(px, py, pz))
      
    points.append(Math.Vector3(ex, ey, ez))

    self._setup(points=points)
  
  def fromAutoSegments(self, start, end, segmentLength=20, easeFunction=easeInOutSine):

    sx, sy, sz = start
    ex, ey, ez = end
  
    direction = Math.Vector3(ex - sx, ey - sy, ez - sz)
    length = direction.length
    if length == 0:
      raise ValueError("Start and end points must be different")
    
    if length < 3.0:
      self._setup(points=[Math.Vector3(sx, sy, sz), Math.Vector3(ex, ey, ez)])
      return self
    
    direction.normalise()
    
    offsetStart = Math.Vector3(sx, sy, sz) + direction
    offsetEnd = Math.Vector3(ex, ey, ez) - direction
    
    if length < 6.0:
      self._setup(points=[Math.Vector3(sx, sy, sz), offsetStart, offsetEnd, Math.Vector3(ex, ey, ez)])
      return self
    
    segments = max(3, int((length - 2) / segmentLength))
    points = interpolatePoints(offsetStart, offsetEnd, segments, easeFunction)
    points.insert(0, Math.Vector3(sx, sy, sz))
    points.append(Math.Vector3(ex, ey, ez))
    
    self._setup(points=points)
    return self
  
  def destroy(self):
    # type: () -> None
    self._controller._destroyPolyLine(self)
    