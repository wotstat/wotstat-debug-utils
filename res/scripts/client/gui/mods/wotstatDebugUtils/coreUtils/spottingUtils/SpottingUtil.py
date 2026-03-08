import BigWorld, math
from Math import Vector3, Matrix
from vehicle_systems import model_assembler
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
from Vehicle import Vehicle
from gui.debugUtils import drawer, gizmos
from gui.battle_control import avatar_getter
from collections import OrderedDict


from ...utils import cssToHexColor
from ...i18n import prefix
t = prefix('spottingUtils')

import typing
if typing.TYPE_CHECKING:
  from ...drawer.DrawerController import LineModel, SphereModel
  from ...gizmos.Marker import Marker
  from ...ui.models.UiModel import Panel
  from typing import Tuple, Optional, List, Dict, Union


SPOT_POINT_COLOR = (cssToHexColor("#00aaff"), cssToHexColor("#5990bf"))
MASK_POINT_COLOR = (cssToHexColor("#ff3135"), cssToHexColor("#ab6d67"))

SPOT_LINE_COLOR = cssToHexColor("#0e9eff")
MASK_LINE_COLOR = cssToHexColor("#ff3135")
SPOT_LINE_COLLIDE_COLOR = cssToHexColor("#738292")
MASK_LINE_COLLIDE_COLOR = cssToHexColor("#917a76")

SPOT_TEXT_COLOR = "#86cfff"
MASK_TEXT_COLOR = "#ffb3b4"

MAX_RAY_DISTANCE_SQR = 455 ** 2

collideSegment = BigWorld.wg_collideSegment if hasattr(BigWorld, 'wg_collideSegment') else BigWorld.collideSegment

def isVehiclePlayerTeam(vehicle, playerTeam=None):
  # type: (Vehicle, Optional[int]) -> bool
  if playerTeam is None: return vehicle.isPlayerTeam
  return vehicle.team == playerTeam

class RayInfo(object):
  __slots__ = ('source', 'target', 'distance', 'isDirect', 'targetVehicle')

  def __init__(self, source, target, distance, isDirect=False, targetVehicle=None):
    self.source = source
    self.target = target
    self.distance = distance
    self.isDirect = isDirect
    self.targetVehicle = targetVehicle

class SpottingUtil(object):
  hangarSpace = dependency.descriptor(IHangarSpace) # type: IHangarSpace
  
  def __init__(self, panel):
    # type: (Panel) -> None

    self.drawerable = [] # type: List[Union[LineModel, SphereModel]]
    self.markers = [] # type: List[Marker]

    self.panel = panel

    self.visibilityCheckpoints = self.panel.addCheckboxLine(t('visibilityCheckpoints'), onToggleCallback=self.onCheckboxToggle)
    self.viewRangePorts = self.panel.addCheckboxLine(t('viewRangePorts'), onToggleCallback=self.onCheckboxToggle)
    self.showBBoxes = self.panel.addCheckboxLine(t('showBBox'), onToggleCallback=self.onCheckboxToggle)
    self.showBBoxAlign = self.panel.addCheckboxLine(t('bboxAlign'), onToggleCallback=self.onCheckboxToggle)

    self.panel.addHeaderLine(t('rays'))
    self.ownSpotRays = self.panel.addCheckboxLine(t('ownSpotRays'))
    self.ownMaskRays = self.panel.addCheckboxLine(t('ownMaskRays'))

    self.allySpotRays = self.panel.addCheckboxLine(t('allSpotRays'))
    self.allyMaskRays = self.panel.addCheckboxLine(t('allMaskRays'))

    self.panel.addSeparatorLine()
    self.distanceText = self.panel.addCheckboxLine(t('minDistanceText'))
    self.nearestOnly = self.panel.addCheckboxLine(t('nearestOnly'))
    self.nonDirectRays = self.panel.addCheckboxLine(t('showNonDirect'))
    

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
    arena = avatar_getter.getArena()
    if not arena: return

    vehicles = arena.vehicles.keys()

    targetVehicles = [BigWorld.entities.get(vehicleID) for vehicleID in vehicles if isinstance(BigWorld.entities.get(vehicleID), Vehicle)]

    self.hideBboxes()
    self.draw(targetVehicles)

  def hideBboxes(self):
    for line in self.drawerable: line.destroy()
    self.drawerable = []

  def updateHangarVehicle(self):
    isInHangar = self.hangarSpace and self.hangarSpace.spaceID is not None
    if not isInHangar: return

    self.hideBboxes()
    if not (self.showBBoxes.isChecked or self.viewRangePorts.isChecked or self.visibilityCheckpoints.isChecked): return

    targetVehicles = [entity for entity in BigWorld.entities.values() if isinstance(entity, ClientSelectableCameraVehicle) and entity.appearance]
    for vehicle in targetVehicles:
      if vehicle.typeDescriptor.hull.hitTester.bbox is None and vehicle.appearance.collisions is not None: 
        model_assembler.setupCollisions(vehicle.typeDescriptor, vehicle.appearance.collisions)

    self.draw(targetVehicles)
  
  def draw(self, targetVehicles):
    # type: (List[Vehicle]) -> None

    isInHangar = self.hangarSpace and self.hangarSpace.spaceID is not None
    vehiclePoints = OrderedDict() # type: Dict[Vehicle, Dict[str, Union[Tuple[Vector3, Vector3], List[Vector3], List[List[RayInfo]]]]]

    sortedVehicles = sorted(targetVehicles, key=lambda v: v.id)

    for vehicle in sortedVehicles:
      matrix = Matrix(vehicle.matrix) # type: Matrix

      spotBbox = getVehicleVisibilityBbox(vehicle)
      
      if self.showBBoxes.isChecked:
        segments, crosses = getBboxSegments(*spotBbox)

        for seg in segments:
          self.drawerable.append(drawer.createLine(points=[matrix.applyPoint(p) for p in seg], color=0xFFFFFF))
      
        if self.showBBoxAlign.isChecked:
          for cross in crosses:
            self.drawerable.append(drawer.createLine(points=[matrix.applyPoint(p) for p in cross], color=0xcecece))

      if self.viewRangePorts.isChecked or \
        self.visibilityCheckpoints.isChecked or \
        self.ownMaskRays.isChecked or self.ownSpotRays.isChecked or \
        self.allyMaskRays.isChecked or self.allySpotRays.isChecked:

        maskPoints, spotPoints = getMaskSpotPoints(vehicle, spotBbox)

        vehiclePoints[vehicle] = {
          'mask': maskPoints,
          'spot': spotPoints,
          'bbox': spotBbox,
          'spotRays': []
        }

    for vehicle, points in vehiclePoints.items():
      if self.visibilityCheckpoints.isChecked:
        for p in points['mask']:
          self.drawerable.append(drawer.createSphere(p, radius=0.05, color=MASK_POINT_COLOR[0], backColor=MASK_POINT_COLOR[1]))

      if self.viewRangePorts.isChecked:
        for p in points['spot']:
          self.drawerable.append(drawer.createSphere(p, radius=0.05, color=SPOT_POINT_COLOR[0], backColor=SPOT_POINT_COLOR[1]))

    if isInHangar: return

    ownVehicle = BigWorld.entities.get(BigWorld.player().playerVehicleID)
    ownTeam = ownVehicle.team if hasattr(ownVehicle, 'team') else None
    
    if self.ownSpotRays.isChecked or self.ownMaskRays.isChecked or self.allySpotRays.isChecked or self.allyMaskRays.isChecked or self.distanceText.isChecked:
      enemyVehicles = [v for v in vehiclePoints if v.isAlive() and not isVehiclePlayerTeam(v, ownTeam)]
      allyVehicles = [v for v in vehiclePoints if v.isAlive() and isVehiclePlayerTeam(v, ownTeam)]
      
      groups = []

      if self.allySpotRays.isChecked: groups.append((allyVehicles, enemyVehicles))
      elif self.ownSpotRays.isChecked: groups.append(([ownVehicle], enemyVehicles))

      if self.allyMaskRays.isChecked: groups.append((enemyVehicles, allyVehicles))
      elif self.ownMaskRays.isChecked: groups.append((enemyVehicles, [ownVehicle]))


      directOnly = not self.nonDirectRays.isChecked
      
      for spots, masks in groups:
        for spotVehicle in spots:
          spotPoints = vehiclePoints[spotVehicle]['spot']
          vehiclePoints[spotVehicle]['spotRays'] = []

          for maskVehicle in masks:
            rays = self.processRays(spotPoints, vehiclePoints[maskVehicle]['mask'], directOnly)
            for ray in rays: ray.targetVehicle = maskVehicle
            vehiclePoints[spotVehicle]['spotRays'].append(rays)


      pointsRays = OrderedDict() # type: OrderedDict[Vector3, List[RayInfo]]
      for vehicle, data in vehiclePoints.items():
        spotRays = data.get('spotRays', []) # type: List[List[RayInfo]]

        for group in spotRays:
          if len(group) == 0: continue

          target = [min(group, key=lambda ray: ray.distance)] if self.nearestOnly.isChecked else group
          for ray in target:
            rayColor = (SPOT_LINE_COLOR, SPOT_LINE_COLLIDE_COLOR) if not isVehiclePlayerTeam(ray.targetVehicle, ownTeam) else (MASK_LINE_COLOR, MASK_LINE_COLLIDE_COLOR)
            self.drawerable.append(drawer.createLine(points=[ray.source, ray.target], color=rayColor[0 if ray.isDirect else 1]))

            if self.distanceText.isChecked:
              pointsRays.setdefault(ray.target, []).append(ray)
              pointsRays.setdefault(ray.source, []).append(ray)

      if self.distanceText.isChecked:
        newMarkers = []

        for point, rays in pointsRays.items():
          
          if len(rays) == 0: continue
          marker = self.markers.pop(0) if self.markers else gizmos.createMarker(size=0, color='white') # type: Marker
         
          newMarkers.append(marker)

          minDistance = min(ray.distance for ray in rays)
          marker.position = point

          marker.text = '<span style="color: {};">{:.1f}</span>'.format(SPOT_TEXT_COLOR if any(ray.source == point for ray in rays) else MASK_TEXT_COLOR, math.sqrt(minDistance))

        for marker in self.markers: marker.destroy()
        self.markers = newMarkers

      else:
        for marker in self.markers: marker.destroy()
        self.markers = []

  def processRays(self, source, target, directOnly=False):
    # type: (List[Vector3], List[Vector3], bool) -> List[RayInfo]

    rays = [] # type: List[RayInfo]

    for sourcePoint in source:
      for targetPoint in target:
        distance = sourcePoint.distSqrTo(targetPoint)
        if distance > MAX_RAY_DISTANCE_SQR: continue
        hit = collideSegment(BigWorld.player().spaceID, sourcePoint, targetPoint, 128)
        isDirect = hit is None
        if directOnly and not isDirect: continue
        rays.append(RayInfo(sourcePoint, targetPoint, distance, isDirect))
    
    return rays

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
  maskPoints.append(typeDescr.chassis.hullPosition + typeDescr.hull.turretPositions[0] + typeDescr.turret.gunPosition)
  maskPoints = [matrix.applyPoint(point) for point in maskPoints]

  bboxTopPoint = matrix.applyPoint(Vector3(0, spotBbox[1].y, 0))
  maskPoints.append(bboxTopPoint)
  spotPoints.append(bboxTopPoint)

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
  
  dynamicGunPoint = matrix.applyPoint(gunMatrix.applyPoint(Vector3(0, 0, 0)))
  maskPoints.append(dynamicGunPoint)
  spotPoints.append(dynamicGunPoint)

  return maskPoints, spotPoints