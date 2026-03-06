import BigWorld, math
from Math import Vector3, Matrix
from vehicle_systems import model_assembler
from helpers import dependency, isPlayerAvatar
from skeletons.gui.shared.utils import IHangarSpace
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
from HangarVehicle import HangarVehicle
from Vehicle import Vehicle
from gui.debugUtils import drawer
from gui.battle_control import avatar_getter

import typing
if typing.TYPE_CHECKING:
  from ...drawer.DrawerController import LineModel
  from ...ui.models.UiModel import Panel
  from typing import Tuple, List


COLORS = {
  'chassis':   ("#15df55", "#476e4c"),  # green
  'hull':      ("#ffe51d", "#6c6433"),  # yellow
  'turret':    ("#05cff8", "#2e6d7f"),  # cyan
  'gun':       ("#d92eef", "#76567b"),  # magenta
  'trackPair': ("#ff8418", "#82583b"),  # orange
}

COLORS = {k: (int(c[0][1:], 16), int(c[1][1:], 16)) for k, c in COLORS.items()}

class BboxUtil(object):
  hangarSpace = dependency.descriptor(IHangarSpace) # type: IHangarSpace

  def __init__(self, panel):
    # type: (Panel) -> None

    self.showOwn = False
    self.showAny = False
    self.backfaceVisibility = False
    self.lines = [] # type: List[LineModel]

    self.panel = panel
    self.header = self.panel.addHeaderLine('BBOX')
    self.panel.addCheckboxLine('Show OWN bbox', self.showOwn, onToggleCallback=self.onShowOwnToggle)
    self.panel.addCheckboxLine('Show ANY bbox', self.showAny, onToggleCallback=self.onShowAnyToggle)
    self.panel.addCheckboxLine('Backface visibility', self.backfaceVisibility, onToggleCallback=self.onBackfaceVisibilityToggle)

    drawer.onBeforeDraw += self.update
    self.hangarSpace.onVehicleChanged += self.updateHangarVehicle

  def dispose(self):
    drawer.onBeforeDraw -= self.update
    self.hangarSpace.onVehicleChanged -= self.updateHangarVehicle
    self.hideBboxes()

  def onShowOwnToggle(self, value):
    self.showOwn = value
    self.updateHangarVehicle()
    if not self.showOwn and not self.showAny: self.hideBboxes()

  def onShowAnyToggle(self, value):
    self.showAny = value
    self.updateHangarVehicle()
    if not self.showOwn and not self.showAny: self.hideBboxes()

  def onBackfaceVisibilityToggle(self, value):
    self.backfaceVisibility = value
    self.updateHangarVehicle()

  def hideBboxes(self):
    for line in self.lines: line.destroy()
    self.lines = []

  def update(self):
    if not self.showOwn and not self.showAny: return
    isInHangar = self.hangarSpace and self.hangarSpace.spaceID is not None
    if isInHangar: return
    if not isPlayerAvatar(): return

    self.hideBboxes()

    if self.showAny:
      arena = avatar_getter.getArena()
      if not arena: return
      vehicles = arena.vehicles.keys()

      for vehicleID in vehicles:
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle and isinstance(vehicle, Vehicle):
          self.lines.extend(drawVehicleBboxes(vehicle, backRender=self.backfaceVisibility))
          
    elif self.showOwn:
      vehicle = BigWorld.entities.get(BigWorld.player().playerVehicleID)
      if vehicle and isinstance(vehicle, Vehicle):
        self.lines.extend(drawVehicleBboxes(vehicle, backRender=self.backfaceVisibility))

  def updateHangarVehicle(self):
    if not self.showOwn and not self.showAny: return
    isInHangar = self.hangarSpace and self.hangarSpace.spaceID is not None
    if not isInHangar: return

    self.hideBboxes()

    targetVehicles = [entity for entity in BigWorld.entities.values() if isinstance(entity, ClientSelectableCameraVehicle if self.showAny else HangarVehicle) and entity.appearance]
    for vehicle in targetVehicles:
      if vehicle.typeDescriptor.hull.hitTester.bbox is None: 
        model_assembler.setupCollisions(vehicle.typeDescriptor, vehicle.appearance.collisions)
      self.lines.extend(drawVehicleBboxes(vehicle, backRender=self.backfaceVisibility))

def drawBbox(bbox, matrix=Matrix(), color=0xFFFFFF00, backColor=0xFFFFFF00):
  # type: (Tuple[Vector3, Vector3, float], Matrix, int, int) -> List[LineModel]
  bboxMin, bboxMax, _ = bbox
  segments = getBboxSegments(bboxMin, bboxMax)
  return [drawer.createLine(points=[matrix.applyPoint(p) for p in seg], color=color, backColor=backColor) for seg in segments]

def getBboxSegments(bboxMin, bboxMax):
  # type: (Vector3, Vector3) -> Tuple[Tuple[Vector3, Vector3], ...]
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

  return [[points[i] for i in seg] for seg in segments]

def getVehiclePartsBboxes(vehicle):
  # type: (Vehicle) -> dict
  typeDescr = vehicle.typeDescriptor
  vehicleMatrix = Matrix(vehicle.matrix)
  result = {}

  # --- Chassis (main track pair) ---
  chassisBbox = typeDescr.chassis.hitTester.bbox
  if chassisBbox:
    bboxMin, bboxMax, _ = chassisBbox
    result['chassis'] = (bboxMin, bboxMax, Matrix(vehicleMatrix))

  # --- Additional track pairs (separate left/right tracks if available) ---
  trackPairs = typeDescr.chassis.trackPairs
  for idx, trackPair in enumerate(trackPairs[1:], start=1):
    if hasattr(trackPair, 'hitTester') and trackPair.hitTester and trackPair.hitTester.bbox:
      tpBboxMin, tpBboxMax, _ = trackPair.hitTester.bbox
      result['trackPair_%d' % idx] = (tpBboxMin, tpBboxMax, Matrix(vehicleMatrix))

  # --- Hull ---
  hullBbox = typeDescr.hull.hitTester.bbox
  if hullBbox:
    hullBboxMin, hullBboxMax, _ = hullBbox
    hullMatrix = Matrix() # type: Matrix
    hullMatrix.setTranslate(typeDescr.chassis.hullPosition)
    hullMatrix.postMultiply(vehicleMatrix)
    result['hull'] = (hullBboxMin, hullBboxMax, hullMatrix)

  # --- Turret ---

  if hasattr(vehicle.appearance, 'turretMatrix'):
    vehicleTurretMatrix = Matrix(vehicle.appearance.turretMatrix) # type: Matrix
  else:
    vehicleTurretMatrix = Matrix()
    vehicleTurretMatrix.setRotateY(math.radians(vehicle.appearance.turretAndGunAngles.getTurretYaw()))

  turretBbox = typeDescr.turret.hitTester.bbox
  if turretBbox:
    turretBboxMin, turretBboxMax, _ = turretBbox

    turretOffsetMatrix = Matrix() # type: Matrix
    turretOffsetMatrix.setTranslate(typeDescr.chassis.hullPosition + typeDescr.hull.turretPositions[0])
    
    turretMatrix = Matrix(vehicleTurretMatrix) # type: Matrix
    turretMatrix.postMultiply(turretOffsetMatrix)
    turretMatrix.postMultiply(vehicleMatrix)
    result['turret'] = (turretBboxMin, turretBboxMax, turretMatrix)

  # --- Gun (attached to turret: gun pitch -> gun offset -> turret yaw -> turret position -> vehicle) ---
  gunBbox = typeDescr.gun.hitTester.bbox
  if gunBbox:
    gunBboxMin, gunBboxMax, _ = gunBbox
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
    gunMatrix.postMultiply(vehicleMatrix)
    result['gun'] = (gunBboxMin, gunBboxMax, gunMatrix)

  return result

def drawVehicleBboxes(vehicle, backRender=False):
  # type: (Vehicle, bool) -> List[LineModel]

  partBboxes = getVehiclePartsBboxes(vehicle)
  lines = [] # type: List[LineModel]
  
  for partName, (bboxMin, bboxMax, matrix) in partBboxes.items():
    if partName in COLORS:
      color, backColor = COLORS[partName]
    elif partName.startswith('trackPair_'):
      color, backColor = COLORS['trackPair']
    else:
      color, backColor = (0xFFFFFFFF, 0xFFFFFFFF)

    lines.extend(drawBbox((bboxMin, bboxMax, 0), matrix=matrix, color=color, backColor=backColor if backRender else None))

  return lines
