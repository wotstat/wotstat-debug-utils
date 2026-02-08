import BigWorld, GUI, Math, math
import Keys
import time
from gui import InputHandler
from AvatarInputHandler import cameras
from gui.debugUtils import ui, gizmos, drawer, NiceColors, NiceColorsHex
from helpers.CallbackDelayer import CallbackDelayer

from helpers import dependency, isPlayerAvatar
from skeletons.gui.shared.utils import IHangarSpace
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle

from Vehicle import SegmentCollisionResultExt
from ProjectileMover import EntityCollisionData

try: 
  from shared_utils.vehicle_utils import getMatinfo
except ImportError:
  from vehicle_systems.tankStructure import TankPartIndexes
  from vehicle_systems.model_assembler import collisionIdxToTrackPairIdx
  from items import vehicles

  def getMatinfo(vehicleEntity, partIndex, matKind, isWheeledVehicle):
    typeDescriptor = vehicleEntity.typeDescriptor
    collisionComponent = vehicleEntity.appearance.collisions

    matInfo = None
    if partIndex == TankPartIndexes.CHASSIS:
      matInfo = typeDescriptor.chassis.materials.get(matKind)
    elif partIndex == TankPartIndexes.HULL:
      matInfo = typeDescriptor.hull.materials.get(matKind)
    elif partIndex == TankPartIndexes.TURRET:
      matInfo = typeDescriptor.turret.materials.get(matKind)
    elif partIndex == TankPartIndexes.GUN:
      matInfo = typeDescriptor.gun.materials.get(matKind)
    elif partIndex > len(TankPartIndexes.ALL):
      trackPairIdx = collisionIdxToTrackPairIdx(partIndex, typeDescriptor)
      if trackPairIdx is not None:
        matInfo = typeDescriptor.chassis.tracks[trackPairIdx].materials.get(matKind)
    elif isWheeledVehicle and collisionComponent is not None:
      wheelName = collisionComponent.getPartName(partIndex)
      if wheelName is not None:
        matInfo = typeDescriptor.chassis.wheelsArmor.get(wheelName, None)
    if matInfo is None:
      commonMaterialsInfo = vehicles.g_cache.commonConfig['materials']
      matInfo = commonMaterialsInfo.get(matKind)
    return matInfo

import typing
if typing.TYPE_CHECKING:
  from ...gizmos.PolyLine import PolyLine
  from ...gizmos.Marker import Marker
  from ...ui.models.UiModel import Panel

collideSegment = BigWorld.wg_collideSegment if hasattr(BigWorld, 'wg_collideSegment') else BigWorld.collideSegment
collideDynamicStatic = BigWorld.wg_collideDynamicStatic if hasattr(BigWorld, 'wg_collideDynamicStatic') else BigWorld.collideDynamicStatic


def round(x, digits=0):
  if digits == 0:
    return int(x + 0.5)
  else:
    mult = 10 ** digits
    return float(int(x * mult + 0.5)) / mult

class RaycastUtil(CallbackDelayer):
  hangarSpace = dependency.descriptor(IHangarSpace)
  
  def __init__(self, panel):
    # type: (Panel) -> None

    CallbackDelayer.__init__(self)

    self.panel = panel
    self.showMatInfo = False
    self.lineIs3D = False
    self.header = self.panel.addHeaderLine('Raycast')
    self.distanceLine = self.panel.addValueLine('Cursor distance', value='0')
    self.raycastLine = self.panel.addCheckboxLine('Raycast line (MMB)', onToggleCallback=self.onRaycastToggle)
    self.raycastMatInfo = self.panel.addCheckboxLine('  Mat info', onToggleCallback=self.onMatInfoToggle)
    self.raycast3DLine = self.panel.addCheckboxLine('  Line 3D', onToggleCallback=self.on3DLineToggle)
    self.lines = [] # type: list[PolyLine]
    self.markers = [] # type: list[Marker]
    
    self.lastSegments = None # type: typing.Optional[typing.List[typing.Tuple[Math.Vector3, any, SegmentCollisionResultExt]]]
    self.lastStartPoint = None # type: typing.Optional[Math.Vector3]
    self.lastEndPoint = None # type: typing.Optional[Math.Vector3]

    self.lastDistanceUpdateTime = 0
    self.delayCallback(0, self.update)
    
  def dispose(self):
    self.clear()
    self.panel.removeLine(self.raycastLine)
    self.panel.removeLine(self.raycastMatInfo)
    self.panel.removeLine(self.raycast3DLine)

  def update(self):
    if self.lastDistanceUpdateTime + 0.1 > time.time(): return 0.0
    self.lastDistanceUpdateTime = time.time()

    cursorPosition = GUI.mcursor().position
    ray, wpoint = cameras.getWorldRayAndPoint(cursorPosition.x, cursorPosition.y)
    ray.normalise()
    
    startPoint = wpoint
    endPoint = wpoint + ray * 3000

    spaceId = None
    if self.hangarSpace and self.hangarSpace.spaceID is not None:
      spaceId = self.hangarSpace.spaceID
    elif isPlayerAvatar():
      spaceId = BigWorld.player().spaceID

    if spaceId is None:
      self.distanceLine.value = '-'
      return 0.0

    res = None
    for _ in range(40):
      res = collideDynamicStatic(spaceId, startPoint, endPoint, 128, -1, 0, 0)
      if res is None: break

      if isPlayerAvatar():
        vehicle = BigWorld.player().vehicle
        if vehicle is not None and res[1] and res[2] == vehicle.id:
          startPoint = res[0] + ray * 0.01
          continue

      break

    if res is not None:
      dist = (res[0] - startPoint).length
      self.distanceLine.value = str(round(dist, 2)) + 'm'
    else:
      self.distanceLine.value = '-'

    return 0.0

  def onMatInfoToggle(self, value):
    self.showMatInfo = value
    self.render()

  def on3DLineToggle(self, value):
    self.lineIs3D = value
    self.render()

  def onRaycastToggle(self, value):
    if value:
      InputHandler.g_instance.onKeyUp += self.handleKeyUpEvent
    else:
      InputHandler.g_instance.onKeyUp -= self.handleKeyUpEvent
      self.clear()
      self.lastSegments = None
      self.lastStartPoint = None
      self.lastEndPoint = None
      
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
          if matInfo is None: continue
          segments.append((startPoint + ray * dist, collision, SegmentCollisionResultExt(dist, hitAngleCos, matInfo, parIndex)))
          
      currentPoint = startPoint
      for _ in range(40):
        res = collideSegment(spaceID, currentPoint, endPoint)
        if res is None: break
        segments.append((res.closestPoint, None, None))
        currentPoint = res.closestPoint + ray * 0.01
               
    else:
      currentPoint = startPoint
      
      for _ in range(40):
        collisionFlags=128
        res = collideDynamicStatic(spaceID, currentPoint, endPoint, collisionFlags, -1, 0, 0)
        
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
    
    self.lastSegments = segments
    self.lastStartPoint = startPoint
    self.lastEndPoint = endPoint
    
    self.render()
      
  def render(self):
    self.clear()
    if self.lastSegments is None: return
    
    segments = self.lastSegments
    startPoint = self.lastStartPoint
    endPoint = self.lastEndPoint


    if self.lineIs3D:
      if len(segments) == 0:
        "#E0C4C3"
        self.lines.append(drawer.createLine(color=NiceColorsHex.RED, backColor=0xE0C4C3, p1=startPoint, p2=endPoint))
      else:
        "#757C77"
        self.lines.append(drawer.createLine(color=NiceColorsHex.GREEN, backColor=0x757C77, p1=startPoint, p2=endPoint))
    else:
      farthestPoint = None
      farthestDist = 0
      
      for pos, collision, seg in segments:
        dist = (pos - startPoint).length
        if dist > farthestDist:
          farthestDist = dist
          farthestPoint = pos
      
      lastPoint = startPoint
      for pos, _, _ in segments:
        if (lastPoint - pos).length < 0.01: continue
        # line = drawer.createLine(color=NiceColors.GREEN if pos == farthestPoint else NiceColors.RED, p1=lastPoint, p2=pos, width=1)
        line = gizmos.createPolyLine(width=1, color=NiceColors.GREEN if farthestPoint else NiceColors.RED)
        line.fromAutoSegments(lastPoint, pos)
        self.lines.append(line)
        lastPoint = pos
        
      if len(segments) > 0 and segments[-1][2] is not None and (lastPoint - endPoint).length < 0.01:
        line = gizmos.createPolyLine(width=1, color=NiceColors.GREEN)
        line.fromAutoSegments(lastPoint, endPoint)
        self.lines.append(line)
        
      if len(segments) == 0:
        line = gizmos.createPolyLine(width=1, color=NiceColors.RED)
        line.fromAutoSegments(startPoint, endPoint)
        self.lines.append(line)
        
    for pos, collision, seg in segments:
      dist = (pos - startPoint).length
      if seg:
        if not seg.matInfo: continue
        
        armorText = str(int(seg.matInfo.armor)) if int(seg.matInfo.armor) == seg.matInfo.armor else str(round(seg.matInfo.armor, 2))
        angleText = str(round(math.degrees(math.acos(seg.hitAngleCos)), 1))
        l = armorText + 'mm (' + angleText + '°)'
        l += '\ndist: ' + str(round(dist, 2)) + 'm'
        
        if not self.showMatInfo: l = None
        
        self.markers.append(gizmos.createMarker(pos, size=5, text=l, color=NiceColors.GREEN))
      else:
        l = str(round(dist, 2)) + 'm' if self.showMatInfo else None
        self.markers.append(gizmos.createMarker(pos, size=5, text=l, color=NiceColors.GREEN))