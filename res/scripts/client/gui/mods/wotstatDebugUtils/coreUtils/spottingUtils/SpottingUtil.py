import BigWorld, math
from Math import Vector3, Matrix
from vehicle_systems import model_assembler
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
from HangarVehicle import HangarVehicle
from Vehicle import Vehicle
from gui.debugUtils import drawer

import typing
if typing.TYPE_CHECKING:
  from ...drawer.DrawerController import LineModel
  from ...gizmos.Marker import Marker
  from ...ui.models.UiModel import Panel
  from typing import Tuple, Optional, List

class SpottingUtil(object):
  hangarSpace = dependency.descriptor(IHangarSpace) # type: IHangarSpace
  
  def __init__(self, panel):
    # type: (Panel) -> None


    self.bboxLines = [] # type: List[LineModel]

    self.panel = panel

    self.visibilityCheckpoints = self.panel.addCheckboxLine('Visibility checkpoints', onToggleCallback=self.onVisibilityCheckpointsToggle)
    self.viewRangePorts = self.panel.addCheckboxLine('View range ports')
    self.showBBoxes = self.panel.addCheckboxLine('Show BBox', onToggleCallback=self.onBboxVisibilityToggle)
    self.showBBoxAlign = self.panel.addCheckboxLine('  BBox align', onToggleCallback=self.onBboxVisibilityToggle)

    self.panel.addHeaderLine('Rays')
    self.panel.addCheckboxLine('OWN spot rays')
    self.panel.addCheckboxLine('OWN mask rays')

    self.panel.addCheckboxLine('ANY spot rays')
    self.panel.addCheckboxLine('ANY mask rays')

    self.panel.addSeparatorLine()
    self.panel.addCheckboxLine('Min distance text')
    self.panel.addCheckboxLine('Show not direct')
    

    drawer.onBeforeDraw += self.update
    self.hangarSpace.onVehicleChanged += self.updateHangarVehicle

  def dispose(self):
    drawer.onBeforeDraw -= self.update
    self.hangarSpace.onVehicleChanged -= self.updateHangarVehicle

  def onVisibilityCheckpointsToggle(self, value):
    pass

  def onBboxVisibilityToggle(self, value):
    if not self.showBBoxes.isChecked and not self.viewRangePorts.isChecked:
      self.hideBboxes()
    else:
      self.updateHangarVehicle()

  def update(self):
    pass

  def hideBboxes(self):
    for line in self.bboxLines: line.destroy()
    self.bboxLines = []

  def updateHangarVehicle(self):
    isInHangar = self.hangarSpace and self.hangarSpace.spaceID is not None
    if not isInHangar: return

    targetVehicles = [entity for entity in BigWorld.entities.values() if isinstance(entity, ClientSelectableCameraVehicle) and entity.appearance]
    for vehicle in targetVehicles:
      if vehicle.typeDescriptor.hull.hitTester.bbox is None: 
        model_assembler.setupCollisions(vehicle.typeDescriptor, vehicle.appearance.collisions)

    if self.showBBoxes.isChecked:
      self.hideBboxes()
      for vehicle in targetVehicles:
        matrix = Matrix(vehicle.matrix) # type: Matrix
        segments, crosses = getBboxSegments(*getVehicleVisibilityBbox(vehicle))
        for seg in segments:
          self.bboxLines.append(drawer.createLine(points=[matrix.applyPoint(p) for p in seg], color=0xFFFFFF))
        
        if self.showBBoxAlign.isChecked:
          for cross in crosses:
            self.bboxLines.append(drawer.createLine(points=[matrix.applyPoint(p) for p in cross], color=0xcecece))


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

  gunBbox = typeDescr.gun.hitTester.bbox
  if gunBbox:
    gunOffset = typeDescr.chassis.hullPosition + typeDescr.hull.turretPositions[0] + typeDescr.turret.gunPosition

    gunBboxMin = Vector3(gunBbox[0]) + gunOffset
    gunBboxMax = Vector3(gunBbox[1]) + gunOffset
    gunBboxMin.z = gunBboxMax.z = result[0].z

    result = extendBbox(result, (gunBboxMin, gunBboxMax))

  return result
  

    