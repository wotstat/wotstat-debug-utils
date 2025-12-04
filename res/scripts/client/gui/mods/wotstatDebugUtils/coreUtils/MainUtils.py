import BigWorld, GUI
from gui.debugUtils import ui, gizmos, NiceColors
from gui import InputHandler
import Keys
from AvatarInputHandler import cameras
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace

import typing
if typing.TYPE_CHECKING:
  from ..gizmos.PolyLine import PolyLine



collideSegment = BigWorld.wg_collideSegment if hasattr(BigWorld, 'wg_collideSegment') else BigWorld.collideSegment

class MainUtils(object):
  
  def __init__(self):
    self.panel = ui.createPanel('Main utils')
    
    self.raycast = self.panel.addCheckboxLine('Raycast line (MMB)', onToggleCallback=self.onRaycastToggle)
    
    self.lines = [] # type: list[PolyLine]
    
  def onRaycastToggle(self, value):
    if value:
      InputHandler.g_instance.onKeyUp += self.handleKeyUpEvent
    else:
      InputHandler.g_instance.onKeyUp -= self.handleKeyUpEvent
      self.clear()
  
  def clear(self):
    for line in self.lines: line.destroy()
    self.lines = []
  
  def handleKeyUpEvent(self, event):
    # type: (BigWorld.KeyEvent) -> None
    if event.key != Keys.KEY_MIDDLEMOUSE: return
    
    self.clear()
    
    cursorPosition = GUI.mcursor().position
    ray, wpoint = cameras.getWorldRayAndPoint(cursorPosition.x, cursorPosition.y)
    
    startPoint = wpoint
    endPoint = wpoint + ray * 3000
    
    hangarSpace = dependency.instance(IHangarSpace)
    spaceID = hangarSpace.spaceID if hangarSpace is not None and hangarSpace.spaceID is not None else BigWorld.player().spaceID
    
    STEP = 50
    collision = collideSegment(spaceID, startPoint, endPoint)
    if collision is None:
      points = [startPoint + ray * i * STEP for i in range(100)]
      self.lines.append(gizmos.createPolyLine(points, 1, NiceColors.RED))
    else:
      points = [startPoint + ray * i * STEP for i in range(1, int((collision.closestPoint - startPoint).length / STEP))]
      points.append(collision.closestPoint)
      points.insert(0, startPoint)
      self.lines.append(gizmos.createPolyLine(points, 1, NiceColors.GREEN))
