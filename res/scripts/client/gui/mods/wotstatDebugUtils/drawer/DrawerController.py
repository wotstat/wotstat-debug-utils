import BigWorld

from helpers.CallbackDelayer import CallbackDelayer
from DebugDrawer import DebugDrawer, Sphere, BM_TRANSPARENT
from Math import Vector3

import typing
if typing.TYPE_CHECKING:
  from DebugDrawer import Line, Sphere

class LineModel:
  def __init__(self, points, p1, p2, width, color, backColor, zTest, zWrite, controller):
    self.p1 = p1
    self.p2 = p2
    self.points = points
    self.width = width
    self.color = color
    self.backColor = backColor
    self.zTest = zTest
    self.zWrite = zWrite
    self.__controller = controller # type: DrawerController

  def __setRenderPoints(self, line):
    # type: (Line) -> None
    if self.p1 is not None and self.p2 is not None:
      line.points([self.p1, self.p2])
    elif self.points is not None:
      line.points(self.points)

  def render(self, dd):
    # type: (DebugDrawer) -> None
    line = dd.line() # type: Line

    if self.width is not None: line.width(self.width)
    if self.color is not None: line.colour(self.color)

    if self.backColor is None:
      if self.zTest is not None: line.zTest(self.zTest)
      if self.zWrite is not None: line.zWrite(self.zWrite)

    self.__setRenderPoints(line)

    if self.backColor is not None:
      lineBack = dd.line() # type: Line
      if self.width is not None: lineBack.width(self.width)
      lineBack.colour(self.backColor)
      lineBack.zTest(False)
      lineBack.zWrite(False)
      self.__setRenderPoints(lineBack)

  def destroy(self):
    self.__controller.removeLine(self)

class SphereModel:
  def __init__(self, position, radius, color, backColor, wireframe, transparent, zTest, zWrite, controller):
    self.position = position
    self.radius = radius
    self.color = color
    self.backColor = backColor
    self.wireframe = wireframe
    self.transparent = transparent
    self.zTest = zTest
    self.zWrite = zWrite
    self.__controller = controller # type: DrawerController
    
  def __setRadius(self, sphere):
    # type: (Sphere) -> None
    if self.radius is None: return

    if isinstance(self.radius, (int, float)):
      sphere.radius(self.radius)
    elif isinstance(self.radius, tuple) and len(self.radius) == 3:
      sphere.scale(self.radius)
    elif isinstance(self.radius, Vector3):
      sphere.scale(self.radius)

  def render(self, dd):
    # type: (DebugDrawer) -> None
    sphere = dd.sphere() # type: Sphere

    if self.position is not None: sphere.position(self.position)
    if self.radius is not None: self.__setRadius(sphere)
    if self.color is not None: sphere.colour(self.color)
    if self.wireframe is not None: sphere.wireframe(self.wireframe)
    if self.transparent: sphere.blendMode(BM_TRANSPARENT)

    if self.backColor is None:
      if self.zTest is not None: sphere.zTest(self.zTest)
      if self.zWrite is not None: sphere.zWrite(self.zWrite)

    if self.backColor is not None:
      sphereBack = dd.sphere() # type: Sphere
      if self.position is not None: sphereBack.position(self.position)
      if self.radius is not None: self.__setRadius(sphereBack)
      sphereBack.colour(self.backColor)
      sphereBack.zTest(False)
      sphereBack.zWrite(False)

  def destroy(self):
    self.__controller.removeSphere(self)


class DrawerController(CallbackDelayer):

  def __init__(self):
    CallbackDelayer.__init__(self)
    self.lines = [] # type: list[LineModel]
    self.spheres = [] # type: list[SphereModel]
    
    self.delayCallback(0.0, self.update)

  def update(self):
    dd = DebugDrawer() # type: DebugDrawer

    for line in self.lines:
      try: line.render(dd)
      except Exception as e: print('Error rendering debug line:', line, e)
    
    for sphere in self.spheres:
      try: sphere.render(dd)
      except Exception as e: print('Error rendering debug sphere:', sphere, e)

    return 0
  
  def createLine(self, points=None, p1=None, p2=None,
                 width=None, color=None, backColor=None,
                 zTest=None, zWrite=None, timeout=None):
    line = LineModel(points, p1, p2, width, color, backColor, zTest, zWrite, controller=self)
    self.lines.append(line)

    if timeout is not None: BigWorld.callback(timeout, line.destroy)

    return line

  def createSphere(self, position=None, radius=None,
                   color=None, backColor=None, wireframe=None, transparent=None,
                   zTest=None, zWrite=None, timeout=None):
    sphere = SphereModel(position, radius, color, backColor, wireframe, transparent, zTest, zWrite, controller=self)
    self.spheres.append(sphere)

    if timeout is not None: BigWorld.callback(timeout, sphere.destroy)

    return sphere

  def removeLine(self, line):
    if line in self.lines:
      self.lines.remove(line)

  def removeSphere(self, sphere):
    if sphere in self.spheres:
      self.spheres.remove(sphere)