import BigWorld, GUI, Math, math
import Keys
from gui import InputHandler
from AvatarInputHandler import cameras
from gui.debugUtils import ui, gizmos, NiceColors

from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
from shared_utils.vehicle_utils import getMatinfo
from Vehicle import SegmentCollisionResultExt
from ProjectileMover import EntityCollisionData
import typing
if typing.TYPE_CHECKING:
  from ...gizmos.PolyLine import PolyLine
  from ...gizmos.Marker import Marker
  from ...ui.models.UiModel import Panel


# collideSegment = BigWorld.wg_collideSegment if hasattr(BigWorld, 'wg_collideSegment') else BigWorld.collideSegment
class RaycastUtil(object):
  hangarSpace = dependency.descriptor(IHangarSpace)
  
  def __init__(self, panel):
    # type: (Panel) -> None
    self.panel = panel
    self.raycastLine = self.panel.addCheckboxLine('Raycast line (MMB)', onToggleCallback=self.onRaycastToggle)
    self.raycastMatInfo = self.panel.addCheckboxLine('  Mat info', onToggleCallback=self.onMatInfoToggle)
    self.lines = [] # type: list[PolyLine]
    self.markers = [] # type: list[Marker]
    
  def dispose(self):
    self.clear()
    self.panel.removeLine(self.raycastLine)
    self.panel.removeLine(self.raycastMatInfo)

  def onMatInfoToggle(self, value):
    self.clear()

  def onRaycastToggle(self, value):
    if value:
      InputHandler.g_instance.onKeyUp += self.handleKeyUpEvent
    else:
      InputHandler.g_instance.onKeyUp -= self.handleKeyUpEvent
      self.clear()
      
  def clear(self):
    for line in self.lines: line.destroy()
    self.lines = []
    
    for marker in self.markers: marker.destroy()
    self.markers = []
  
  def handleKeyUpEvent(self, event):
    # type: (BigWorld.KeyEvent) -> None
    if event.key != Keys.KEY_MIDDLEMOUSE: return
    self.raycast()

  def raycast(self):    
    self.clear()
    
    cursorPosition = GUI.mcursor().position
    ray, wpoint = cameras.getWorldRayAndPoint(cursorPosition.x, cursorPosition.y)
    ray.normalise()
    
    startPoint = wpoint
    endPoint = wpoint + ray * 3000
    
    isInHangar = self.hangarSpace and self.hangarSpace.spaceID is not None
    spaceID = self.hangarSpace.spaceID if isInHangar else BigWorld.player().spaceID
    
    segments = [] # type: typing.List[typing.Tuple[Math.Vector3, any, SegmentCollisionResultExt]]
    
    if isInHangar:
      heroTankEntityList = [entity for entity in BigWorld.entities.values() if isinstance(entity, ClientSelectableCameraVehicle)]
      entityCollisions = [(e, e.appearance.collisions) for e in heroTankEntityList if hasattr(e, 'appearance') and hasattr(e.appearance, 'collisions')]
        
      segments = []
      for entity, collision in entityCollisions:
        hits = collision.collideAllWorld(startPoint, endPoint)
        if not hits: continue
        for dist, hitAngleCos, matKind, parIndex in hits:
          matInfo = getMatinfo(entity, parIndex, matKind, entity.typeDescriptor.type.isWheeledVehicle)
          segments.append((startPoint + ray * dist, collision, SegmentCollisionResultExt(dist, hitAngleCos, matInfo, parIndex)))
          
      currentPoint = startPoint
      for _ in range(40):
        res = BigWorld.wg_collideSegment(spaceID, currentPoint, endPoint)
        if res is None: break
        segments.append((res.closestPoint, None, None))
        currentPoint = res.closestPoint + ray * 0.01
               
    else:
      currentPoint = startPoint
      
      for _ in range(40):
        collisionFlags=128
        res = BigWorld.wg_collideDynamicStatic(spaceID, currentPoint, endPoint, collisionFlags, -1, 0, 0)
        
        if res is None: break
        
        entityStart = res[0] + ray * -0.1
        
        if res[1]:
          coll = EntityCollisionData(res[2], res[3], res[4], True)
          result = coll.entity.collideSegmentExt(entityStart, res[0] + ray * 20)
          for hit in result:
            segments.append((entityStart + ray * hit.dist, coll.entity.appearance.collisions, hit))
            
          currentPoint = entityStart + ray * result[len(result) - 1].dist + ray * 0.01
        else:
          segments.append((res[0], None, None))
          currentPoint = res[0] + ray * 0.01
    
    farthestPoint = None
    farthestDist = 0
    
    for pos, collision, seg in segments:
      dist = (pos - startPoint).length
      if dist > farthestDist:
        farthestDist = dist
        farthestPoint = pos
    
    
    lastPoint = startPoint
    for pos, _, _ in segments:
      line = gizmos.createPolyLine(width=1, color=NiceColors.GREEN if farthestPoint else NiceColors.RED)
      line.fromAutoSegments(lastPoint, pos)
      self.lines.append(line)
      lastPoint = pos
      
    if len(segments) == 0:
      line = gizmos.createPolyLine(width=1, color=NiceColors.RED)
      line.fromAutoSegments(startPoint, endPoint)
      self.lines.append(line)
        
    for pos, collision, seg in segments:
      if seg:
        if not seg.matInfo: continue
        
        armorText = str(int(seg.matInfo.armor)) if int(seg.matInfo.armor) == seg.matInfo.armor else str(round(seg.matInfo.armor, 2))
        angleText = str(round(math.degrees(math.acos(seg.hitAngleCos)), 1))
        l = armorText + 'mm (' + angleText + '°)'
        self.markers.append(gizmos.createMarker(pos, size=5, text=l, color=NiceColors.GREEN))
      else:
        self.markers.append(gizmos.createMarker(pos, size=5, color=NiceColors.GREEN))