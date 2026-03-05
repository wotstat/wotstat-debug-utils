import BigWorld, math
from Math import Vector3, Matrix
from vehicle_systems import model_assembler
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
from HangarVehicle import HangarVehicle
from Vehicle import Vehicle
from gui.debugUtils import drawer
from gui.battle_control import avatar_getter

from ...utils import cssToHexColor

import typing
if typing.TYPE_CHECKING:
  from ...drawer.DrawerController import LineModel
  from ...gizmos.Marker import Marker
  from ...ui.models.UiModel import Panel
  from typing import Tuple, Optional, List, Dict


SPOT_POINT_COLOR = (cssToHexColor("#0e9eff"), cssToHexColor("#5885ae"))
MASK_POINT_COLOR = (cssToHexColor("#ff3135"), cssToHexColor("#ab6d67"))

MY_SPOT_LINE_COLOR = cssToHexColor("#0e9eff")
MY_MASK_LINE_COLOR = cssToHexColor("#ff3135")
MY_SPOT_LINE_COLLIDE_COLOR = cssToHexColor("#738292")
MY_MASK_LINE_COLLIDE_COLOR = cssToHexColor("#917a76")

MAX_RAY_DISTANCE_SQR = 455 ** 2


collideSegment = BigWorld.wg_collideSegment if hasattr(BigWorld, 'wg_collideSegment') else BigWorld.collideSegment

class SpottingUtil(object):
  hangarSpace = dependency.descriptor(IHangarSpace) # type: IHangarSpace
  
  def __init__(self, panel):
    # type: (Panel) -> None


    self.bboxLines = [] # type: List[LineModel]

    self.panel = panel

    self.visibilityCheckpoints = self.panel.addCheckboxLine('Visibility checkpoints', onToggleCallback=self.onCheckboxToggle)
    self.viewRangePorts = self.panel.addCheckboxLine('View range ports', onToggleCallback=self.onCheckboxToggle)
    self.showBBoxes = self.panel.addCheckboxLine('Show BBox', onToggleCallback=self.onCheckboxToggle)
    self.showBBoxAlign = self.panel.addCheckboxLine('  BBox align', onToggleCallback=self.onCheckboxToggle)

    self.panel.addHeaderLine('Rays')
    self.ownSpotRays = self.panel.addCheckboxLine('OWN spot rays')
    self.ownMaskRays = self.panel.addCheckboxLine('OWN mask rays')

    self.anySpotRays = self.panel.addCheckboxLine('ANY spot rays')
    self.anyMaskRays = self.panel.addCheckboxLine('ANY mask rays')

    self.panel.addSeparatorLine()
    self.panel.addCheckboxLine('Min distance text')
    self.nearestOnly = self.panel.addCheckboxLine('Nearest only')
    self.nonDirectRays = self.panel.addCheckboxLine('Show not direct')
    

    drawer.onBeforeDraw += self.update
    self.hangarSpace.onVehicleChanged += self.updateHangarVehicle

  def dispose(self):
    drawer.onBeforeDraw -= self.update
    self.hangarSpace.onVehicleChanged -= self.updateHangarVehicle

  def onCheckboxToggle(self, value):
      self.updateHangarVehicle()

  def update(self):
    isInHangar = self.hangarSpace and self.hangarSpace.spaceID is not None
    if isInHangar: return
    if not avatar_getter.isPlayerAvatar(): return

    arena = avatar_getter.getArena()
    if not arena: return
    vehicles = arena.vehicles.keys()

    targetVehicles = [BigWorld.entities.get(vehicleID) for vehicleID in vehicles if isinstance(BigWorld.entities.get(vehicleID), Vehicle)]

    self.hideBboxes()
    self.draw(targetVehicles)

  def hideBboxes(self):
    for line in self.bboxLines: line.destroy()
    self.bboxLines = []

  def updateHangarVehicle(self):
    isInHangar = self.hangarSpace and self.hangarSpace.spaceID is not None
    if not isInHangar: return

    self.hideBboxes()
    if not (self.showBBoxes.isChecked or self.viewRangePorts.isChecked or self.visibilityCheckpoints.isChecked): return

    targetVehicles = [entity for entity in BigWorld.entities.values() if isinstance(entity, ClientSelectableCameraVehicle) and entity.appearance]
    for vehicle in targetVehicles:
      if vehicle.typeDescriptor.hull.hitTester.bbox is None: 
        model_assembler.setupCollisions(vehicle.typeDescriptor, vehicle.appearance.collisions)

    self.draw(targetVehicles)
  
  def draw(self, targetVehicles):

    isInHangar = self.hangarSpace and self.hangarSpace.spaceID is not None
    vehiclePoints = {} # type: Dict[Vehicle, Dict[str, List[Vector3]]]

    for vehicle in targetVehicles:
      matrix = Matrix(vehicle.matrix) # type: Matrix

      spotBbox = getVehicleVisibilityBbox(vehicle)
      
      if self.showBBoxes.isChecked:
        segments, crosses = getBboxSegments(*spotBbox)

        for seg in segments:
          self.bboxLines.append(drawer.createLine(points=[matrix.applyPoint(p) for p in seg], color=0xFFFFFF))
      
        if self.showBBoxAlign.isChecked:
          for cross in crosses:
            self.bboxLines.append(drawer.createLine(points=[matrix.applyPoint(p) for p in cross], color=0xcecece))

      if self.viewRangePorts.isChecked or \
        self.visibilityCheckpoints.isChecked or \
        self.ownMaskRays.isChecked or self.ownSpotRays.isChecked or \
        self.anyMaskRays.isChecked or self.anySpotRays.isChecked:

        maskPoints, spotPoints = getMaskSpotPoints(vehicle, spotBbox)

        vehiclePoints[vehicle] = {
          'mask': maskPoints,
          'spot': spotPoints,
          'bbox': spotBbox
        }

    for vehicle, points in vehiclePoints.items():
      if self.visibilityCheckpoints.isChecked:
        for p in points['mask']:
          self.bboxLines.append(drawer.createSphere(p, radius=0.05, color=MASK_POINT_COLOR[0], backColor=MASK_POINT_COLOR[1]))

      if self.viewRangePorts.isChecked:
        for p in points['spot']:
          self.bboxLines.append(drawer.createSphere(p, radius=0.05, color=SPOT_POINT_COLOR[0], backColor=SPOT_POINT_COLOR[1]))

    if isInHangar: return

    ownVehicle = BigWorld.entities.get(BigWorld.player().playerVehicleID)
    if self.ownSpotRays.isChecked or self.ownMaskRays.isChecked:
      ownPoints = vehiclePoints.get(ownVehicle)
      ownTeam = ownVehicle.team

      for vehicle, points in vehiclePoints.items():
        if vehicle.team == ownTeam: continue
        if not vehicle.isAlive(): continue

        if self.ownMaskRays.isChecked: self.drawRays(ownPoints['mask'], points['spot'], MY_MASK_LINE_COLOR, MY_MASK_LINE_COLLIDE_COLOR)
        if self.ownSpotRays.isChecked: self.drawRays(ownPoints['spot'], points['mask'], MY_SPOT_LINE_COLOR, MY_SPOT_LINE_COLLIDE_COLOR)

  def drawRays(self, source, target, color, nonDirectColor):
    # type: (List[Vector3], List[Vector3], int, int) -> None

    lines = [] # type: List[Tuple[Vector3, Vector3, Optional[BigWorld.WGCollideSegmentResult], float]]

    for sourcePoint in source:
      for targetPoint in target:
        distance = sourcePoint.distSqrTo(targetPoint)
        if distance > MAX_RAY_DISTANCE_SQR: continue

        hit = collideSegment(BigWorld.player().spaceID, sourcePoint, targetPoint, 128)
        lines.append((sourcePoint, targetPoint, hit is None, distance))

    if self.nearestOnly.isChecked:
      displayOnly = lines if self.nonDirectRays.isChecked else filter(lambda t: t[2], lines)
      lines = [min(displayOnly, key=lambda x: x[3])] if len(displayOnly) > 0 else []

    for sourcePoint, targetPoint, direct, _ in lines:
      lineColor = color if direct else nonDirectColor
      if direct or self.nonDirectRays.isChecked:
        self.bboxLines.append(drawer.createLine(points=[sourcePoint, targetPoint], color=lineColor))

def getBboxSegments(bboxMin, bboxMax):
  # type: (Vector3, Vector3) -> Tuple[List[List[Vector3]], List[List[Vector3]]]
  points = [
    Vector3(bboxMin.x, bboxMin.y, bboxMin.z),
    Vector3(bboxMin.x, bboxMax.y, bboxMin.z),
    Vector3(bboxMin.x, bboxMax.y, bboxMax.z),
    Vector3(bboxMin.x, bboxMin.y, bboxMax.z),
    Vector3(bboxMax.x, bboxMin.y, bboxMin.z),
    Vector3(bboxMax.x, bboxMax.y, bboxMin.z),
    Vector3(bboxMax.x, bboxMax.y, bboxMax.z),
    Vector3(bboxMax.x, bboxMin.y, bboxMax.z),
  ]

  segments = [
    [0, 1, 2, 3, 0, 4, 7, 3],
    [4, 5, 6, 7],
    [2, 6],
    [1, 5]
  ]

  crosses = [
    [0, 2, 7, 5, 0],
    [4, 1, 3, 6, 4],
    [2, 5], [1, 6]
  ]

  return ([[points[i] for i in seg] for seg in segments], [[points[i] for i in seg] for seg in crosses])

def extendBbox(bbox1, bbox2):
  # type: (Optional[Tuple[Vector3, Vector3]], Tuple[Vector3, Vector3]) -> Tuple[Vector3, Vector3]
  min1, max1 = bbox1 if bbox1 else (bbox2[0], bbox2[1])
  min2, max2 = bbox2
  newMin = Vector3(min(min1.x, min2.x), min(min1.y, min2.y), min(min1.z, min2.z))
  newMax = Vector3(max(max1.x, max2.x), max(max1.y, max2.y), max(max1.z, max2.z))
  return newMin, newMax

def getVehicleVisibilityBbox(vehicle):
  # type: (Vehicle) -> Tuple[Vector3, Vector3]
  typeDescr = vehicle.typeDescriptor

  result = None # type: Optional[Tuple[Vector3, Vector3]]
  
  hullBbox = typeDescr.hull.hitTester.bbox
  if hullBbox:
    hullBboxMin, hullBboxMax, _ = hullBbox
    hullOffset = typeDescr.chassis.hullPosition
    result = extendBbox(result, (hullBboxMin + hullOffset, hullBboxMax + hullOffset))

  turretBbox = typeDescr.turret.hitTester.bbox
  if turretBbox:
    turretBboxMin, turretBboxMax, _ = turretBbox
    turretOffset = typeDescr.chassis.hullPosition + typeDescr.hull.turretPositions[0]
    result = extendBbox(result, (turretBboxMin + turretOffset, turretBboxMax + turretOffset))

  # gunBbox = typeDescr.gun.hitTester.bbox
  # if gunBbox:
  #   gunOffset = typeDescr.chassis.hullPosition + typeDescr.hull.turretPositions[0] + typeDescr.turret.gunPosition

  #   gunBboxMin = Vector3(gunBbox[0]) + gunOffset
  #   gunBboxMax = Vector3(gunBbox[1]) + gunOffset
  #   gunBboxMin.z = gunBboxMax.z = result[0].z

  #   result = extendBbox(result, (gunBboxMin, gunBboxMax))

  return result
  
def getMaskSpotPoints(vehicle, spotBbox):
  # type: (Vehicle, Tuple[Vector3, Vector3]) -> Tuple[List[Vector3], List[Vector3]]
  typeDescr = vehicle.typeDescriptor
  matrix = Matrix(vehicle.matrix) # type: Matrix
  spotPoints = []
  maskPoints = []

  # center of each side spotBbox is mask
  center = (spotBbox[0] + spotBbox[1]) * 0.5
  maskPoints.append(Vector3(center.x, center.y, spotBbox[0].z))
  maskPoints.append(Vector3(center.x, center.y, spotBbox[1].z))
  maskPoints.append(Vector3(spotBbox[0].x, center.y, center.z))
  maskPoints.append(Vector3(spotBbox[1].x, center.y, center.z))
  maskPoints.append(Vector3(0, spotBbox[1].y, 0))

  if hasattr(vehicle.appearance, 'turretMatrix'):
    vehicleTurretMatrix = Matrix(vehicle.appearance.turretMatrix) # type: Matrix
  else:
    vehicleTurretMatrix = Matrix()
    vehicleTurretMatrix.setRotateY(math.radians(vehicle.appearance.turretAndGunAngles.getTurretYaw()))

  if hasattr(vehicle.appearance, 'gunMatrix'):
    gunMatrix = Matrix(vehicle.appearance.gunMatrix) # type: Matrix
  else:
    gunMatrix = Matrix()
    gunMatrix.setRotateX(math.radians(vehicle.appearance.turretAndGunAngles.getGunPitch()))

  gunPosMatrix = Matrix() # type: Matrix
  gunPosMatrix.setTranslate(typeDescr.turret.gunPosition)
  gunMatrix.postMultiply(gunPosMatrix)
  gunMatrix.postMultiply(Matrix(vehicleTurretMatrix))
  turretOffsetForGun = Matrix() # type: Matrix
  turretOffsetForGun.setTranslate(typeDescr.chassis.hullPosition + typeDescr.hull.turretPositions[0])
  gunMatrix.postMultiply(turretOffsetForGun)
  
  maskPoints.append(typeDescr.chassis.hullPosition + typeDescr.hull.turretPositions[0] + typeDescr.turret.gunPosition)
  maskPoints.append(gunMatrix.applyPoint(Vector3(0, 0, 0)))

  spotPoints.append(Vector3(0, spotBbox[1].y, 0))
  spotPoints.append(gunMatrix.applyPoint(Vector3(0, 0, 0)))

  return [matrix.applyPoint(point) for point in maskPoints], [matrix.applyPoint(point) for point in spotPoints]