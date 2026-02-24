import math, Math, BigWorld

from Avatar import PlayerAvatar
from Event import SafeEvent
from Math import Vector3
from VehicleGunRotator import VehicleGunRotator
from gui.debugUtils import gizmos, drawer, NiceColors, NiceColorsHex
from projectile_trajectory import computeProjectileTrajectory
from projectile_trajectory import getShotAngles
from ...utils import cssToHexColor
from .BallisticTrajectory import BallisticTrajectory

from ...Logger import Logger


import typing
if typing.TYPE_CHECKING:
  from VehicleGunRotator import GunMarkerInfo
  from ...ui.models.UiModel import Panel
  from ...gizmos.Marker import Marker
  from typing import Tuple, Optional

logger = Logger.instance()


SERVER_COLOR = cssToHexColor("#64D2FF")
SERVER_BACK_COLOR = cssToHexColor("#6490a2")
AFTER_SERVER_COLOR = cssToHexColor("#B1CEDA")
AFTER_SERVER_BACK_COLOR = cssToHexColor("#868F93")

CLIENT_COLOR = cssToHexColor("#D37CFF")
CLIENT_BACK_COLOR = cssToHexColor("#8f6e9c")
AFTER_CLIENT_COLOR = cssToHexColor("#D0B0D0")
AFTER_CLIENT_BACK_COLOR = cssToHexColor("#948494")

BEFORE_MARKER_TRAJECTORY_EPSILON = 0.01
AFTER_MARKER_TRAJECTORY_EPSILON = 0.02


updateGunMarkerEvent = SafeEvent()
oldUpdateGunMarker = PlayerAvatar.updateGunMarker
def updateGunMarker(self, *a, **k):
  updateGunMarkerEvent(self, *a, **k)
  return oldUpdateGunMarker(self, *a, **k)
PlayerAvatar.updateGunMarker = updateGunMarker

updateGunMarkerClientEvent = SafeEvent()
oldUpdateGunMarkerClient = VehicleGunRotator._VehicleGunRotator__updateGunMarker
def updateGunMarkerClient(self, *a, **k):
  updateGunMarkerClientEvent(self, *a, **k)
  return oldUpdateGunMarkerClient(self, *a, **k)
VehicleGunRotator._VehicleGunRotator__updateGunMarker = updateGunMarkerClient

onShowTracerEvent = SafeEvent()
oldShowTracer = PlayerAvatar.showTracer
def showTracer(self, *a, **k):
  onShowTracerEvent(self, *a, **k)
  return oldShowTracer(self, *a, **k)
PlayerAvatar.showTracer = showTracer


def calculateLineDiskPoints(center, normal, radius, numPoints):
  # type: (Vector3, Vector3, float, int) -> list[Vector3]
  points = []
  normal.normalise()
  if abs(normal.y) < 0.99:
    tangent = normal * Vector3(0, 1, 0)
    tangent.normalise()
  else:
    tangent = normal * Vector3(1, 0, 0)
    tangent.normalise()
  bitangent = normal * tangent

  for i in range(numPoints):
    angle = (i / float(numPoints)) * math.pi * 2.0
    point = center + radius * (math.cos(angle) * tangent + math.sin(angle) * bitangent)
    points.append(point)

  points.append(points[0]) # close the loop
  
  return points, tangent, bitangent

def getMarkerEndPoint(gunRotator, shotPos, shotVec, dispersionAngles):
   # type: (VehicleGunRotator, Vector3, Vector3, list[float]) -> Tuple[Vector3, Vector3, float]
  if hasattr(gunRotator, '_VehicleGunRotator__getGunMarkerPosition'):
    endPos, endDir, size, _, _, _, _ = gunRotator._VehicleGunRotator__getGunMarkerPosition(shotPos, shotVec, dispersionAngles)
  else:
    marker = gunRotator._VehicleGunRotator__getGunMarkerInfo(shotPos, shotVec, dispersionAngles, gunRotator._VehicleGunRotator__gunIndex) # type: GunMarkerInfo
    endPos = marker.position
    endDir = marker.direction
    size = marker.size

  return endPos, endDir, size

def getTrajectories(shotPos, shotVec, endPos, gravity, shellVelocity, afterDuration=5.0):
  # type: (Vector3, Vector3, Vector3, float, float, float) -> Tuple[list[Vector3], Optional[list[Vector3]]]

  acceleration = Vector3(0, -gravity, 0)

  velocity = shotVec # type: Vector3
  velocity.normalise()
  velocity = velocity * shellVelocity
  calc = BallisticTrajectory(shotPos, velocity, acceleration)

  _, markerTime, dist = calc.getNearestPoint(endPos, timeFrom=0.0, timeTo=5.0)
  beforePoints = calc.getTrajectoryPoints(0, markerTime, BEFORE_MARKER_TRAJECTORY_EPSILON)
  afterPoints = calc.getTrajectoryPoints(markerTime, markerTime + afterDuration, AFTER_MARKER_TRAJECTORY_EPSILON) if dist < 0.5 and afterDuration > 0 else []
  return beforePoints, afterPoints

class AimingUtil(object):
  
  def __init__(self, panel):
    # type: (Panel) -> None
    global updateGunMarkerEvent, updateGunMarkerClientEvent, onShowTracerEvent

    self.serverTrajectory = drawer.createLine(points=[], color=SERVER_COLOR, backColor=SERVER_BACK_COLOR)
    self.afterServerTrajectory = drawer.createLine(points=[], color=AFTER_SERVER_COLOR, backColor=AFTER_SERVER_BACK_COLOR)
    self.serverCircle = drawer.createLine(points=[], color=SERVER_COLOR, backColor=SERVER_BACK_COLOR)
    
    self.clientTrajectory = drawer.createLine(points=[], color=CLIENT_COLOR, backColor=CLIENT_BACK_COLOR)
    self.afterClientTrajectory = drawer.createLine(points=[], color=AFTER_CLIENT_COLOR, backColor=AFTER_CLIENT_BACK_COLOR)
    self.clientCircle = drawer.createLine(points=[], color=CLIENT_COLOR, backColor=CLIENT_BACK_COLOR)

    self.showServerCircle = False
    self.showServerTrajectory = True
    self.showClientCircle = False
    self.showClientTrajectory = True
    self.preserveOnShot = False
    self.continuousTrajectory = False
    
    self.panel = panel
    self.header = self.panel.addHeaderLine('Aiming')
    self.panel.addCheckboxLine('Server aiming circle', self.showServerCircle, self.onShowServerCircleChanged)
    self.panel.addCheckboxLine('  Trajectory', self.showServerTrajectory, self.onShowServerTrajectoryChanged)
    self.panel.addCheckboxLine('Client aiming circle', self.showClientCircle, self.onShowClientCircleChanged)
    self.panel.addCheckboxLine('  Trajectory', self.showClientTrajectory, self.onShowClientTrajectoryChanged)
    self.panel.addCheckboxLine('Continuous trajectory', self.continuousTrajectory, self.onContinuousTrajectoryChanged)
    self.panel.addCheckboxLine('Preserve on shot', self.preserveOnShot, self.onPreserveOnShotChanged)


    updateGunMarkerEvent += self.onUpdateGunMarker
    updateGunMarkerClientEvent += self.onUpdateGunMarkerClient
    onShowTracerEvent += self.onShowTracerEvent

  def dispose(self):
    global updateGunMarkerEvent, updateGunMarkerClientEvent, onShowTracerEvent
    
    updateGunMarkerEvent -= self.onUpdateGunMarker
    updateGunMarkerClientEvent -= self.onUpdateGunMarkerClient
    onShowTracerEvent -= self.onShowTracerEvent

  def onShowServerCircleChanged(self, value):
    self.showServerCircle = value
    if not value: self.serverCircle.points = []

  def onShowServerTrajectoryChanged(self, value):
    self.showServerTrajectory = value
    if not value: self.serverTrajectory.points = []

  def onShowClientCircleChanged(self, value):
    self.showClientCircle = value
    if not value: self.clientCircle.points = []

  def onShowClientTrajectoryChanged(self, value):
    self.showClientTrajectory = value
    if not value: self.clientTrajectory.points = []

  def onPreserveOnShotChanged(self, value):
    self.preserveOnShot = value

  def onContinuousTrajectoryChanged(self, value):
    self.continuousTrajectory = value

  def onUpdateGunMarker(self, obj, vehicleID, shotPos, shotVec, dispersionAngle, *a, **k):
    # type: (AimingUtil, PlayerAvatar, int, Vector3, Vector3, float, Tuple, dict) -> None

    if not obj.gunRotator: return

    if not self.showServerTrajectory or not self.showServerCircle:
      self.serverTrajectory.points = []
      self.afterServerTrajectory.points = []

    if not self.showServerCircle:
      self.serverCircle.points = []
      return

    shot = obj.getVehicleDescriptor().shot
    gravity = shot.gravity
    velocity = shot.speed

    endPos, endDir, size = getMarkerEndPoint(obj.gunRotator, shotPos, shotVec, [dispersionAngle, dispersionAngle, dispersionAngle, dispersionAngle])
    diskPoints, tangent, bitangent = calculateLineDiskPoints(endPos, endDir, size / 2.0, 64)

    if self.showServerCircle:
      self.serverCircle.points = diskPoints

      if self.showServerTrajectory:
        trajectoryPoints, afterTrajectoryPoints = getTrajectories(shotPos, shotVec, endPos, gravity, velocity, 5.0 if self.continuousTrajectory else 0.0    )
        self.serverTrajectory.points = trajectoryPoints
        self.afterServerTrajectory.points = afterTrajectoryPoints
  
  def onUpdateGunMarkerClient(self, obj, *a, **k):
    # type: (VehicleGunRotator, Tuple, dict) -> None

    if not self.showClientTrajectory or not self.showClientCircle:
      self.clientTrajectory.points = []
      self.afterClientTrajectory.points = []

    if not self.showClientCircle:
      self.clientCircle.points = []
      return

    shotPos, shotVec = obj.getCurShotPosition()
    dispersionAngles = obj._VehicleGunRotator__dispersionAngles
    shot = obj._avatar.getVehicleDescriptor().shot
    gravity = shot.gravity
    velocity = shot.speed

    endPos, endDir, size = getMarkerEndPoint(obj, shotPos, shotVec, dispersionAngles)
    diskPoints, tangent, bitangent = calculateLineDiskPoints(endPos, endDir, size / 2.0, 64)
    trajectoryPoints, afterTrajectoryPoints = getTrajectories(shotPos, shotVec, endPos, gravity, velocity, 5.0 if self.continuousTrajectory else 0.0)

    if self.showClientCircle:
      self.clientCircle.points = diskPoints

      if self.showClientTrajectory:
        self.clientTrajectory.points = trajectoryPoints
        self.afterClientTrajectory.points = afterTrajectoryPoints

  def onShowTracerEvent(self, obj, attackerID, *a, **k):
    if attackerID != BigWorld.player().playerVehicleID:
      return
    
    if not self.preserveOnShot:
      return
    
    if self.showServerCircle:
      drawer.createLine(points=self.serverCircle.points, color=SERVER_COLOR, backColor=SERVER_BACK_COLOR, timeout=5.0)
      if self.showServerTrajectory:
        drawer.createLine(points=self.serverTrajectory.points, color=SERVER_COLOR, backColor=SERVER_BACK_COLOR, timeout=5.0)
        drawer.createLine(points=self.afterServerTrajectory.points, color=AFTER_SERVER_COLOR, backColor=AFTER_SERVER_BACK_COLOR, timeout=5.0)

    if self.showClientCircle:
      drawer.createLine(points=self.clientCircle.points, color=CLIENT_COLOR, backColor=CLIENT_BACK_COLOR, timeout=5.0)
      if self.showClientTrajectory:
        drawer.createLine(points=self.clientTrajectory.points, color=CLIENT_COLOR, backColor=CLIENT_BACK_COLOR, timeout=5.0)
        drawer.createLine(points=self.afterClientTrajectory.points, color=AFTER_CLIENT_COLOR, backColor=AFTER_CLIENT_BACK_COLOR, timeout=5.0)

    

