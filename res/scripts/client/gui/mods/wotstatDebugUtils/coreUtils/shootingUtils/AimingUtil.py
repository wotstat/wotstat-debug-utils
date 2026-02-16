import math, Math, BigWorld

from Avatar import PlayerAvatar
from Event import SafeEvent
from Math import Vector3
from VehicleGunRotator import VehicleGunRotator
from gui.debugUtils import gizmos, drawer, NiceColors, NiceColorsHex
from ...utils import cssToHexColor

from ...Logger import Logger

try:
  from projectile_trajectory import computeProjectileTrajectoryWithEnd
except ImportError:
  def computeProjectileTrajectoryWithEnd(beginPoint, endPoint, velocity, gravity, epsilon):
    checkPoints = []
    stack = [(velocity, beginPoint, endPoint)]
    while len(stack) > 0:
      lastIdx = len(stack) - 1
      v1, p1, p2 = stack[lastIdx]
      del stack[lastIdx]
      delta = p2 - p1
      xzNormal = Math.Vector3(-delta.z, 0.0, delta.x)
      normal = xzNormal * delta
      if abs(normal.y) < epsilon:
        checkPoints.append(p2)
        continue
      normal.normalise()
      extremeTime = normal.dot(v1) / (-gravity.y * normal.y)
      extremePoint = v1.scale(extremeTime) + gravity.scale(extremeTime * extremeTime * 0.5)
      dist = abs(normal.dot(extremePoint))
      if dist > epsilon:
        extremeVelocity = v1 + gravity.scale(extremeTime)
        stack.append((extremeVelocity, p1 + extremePoint, p2))
        stack.append((v1, p1, p1 + extremePoint))
      else:
        checkPoints.append(p2)

    return checkPoints


SHELL_TRAJECTORY_EPSILON_CAMERA = 0.03

import typing
if typing.TYPE_CHECKING:
  from VehicleGunRotator import GunMarkerInfo
  from ...ui.models.UiModel import Panel
  from ...gizmos.Marker import Marker
  from typing import Tuple, Optional

logger = Logger.instance()


SERVER_COLOR = cssToHexColor("#64D2FF")
SERVER_BACK_COLOR = cssToHexColor("#6490a2")

CLIENT_COLOR = cssToHexColor("#D37CFF")
CLIENT_BACK_COLOR = cssToHexColor("#8f6e9c")


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

def getGunLines(gunRotator, shotPos, shotVec, dispersionAngles, gravity):
  # type: (VehicleGunRotator, Vector3, Vector3, list[float], float) -> Tuple[list[Vector3], Optional[list[Vector3]], Optional[Vector3], Optional[Vector3]]

  if hasattr(gunRotator, '_VehicleGunRotator__getGunMarkerPosition'):
    endPos, endDir, size, _, _, _, _ = gunRotator._VehicleGunRotator__getGunMarkerPosition(shotPos, shotVec, dispersionAngles)
  else:
    marker = gunRotator._VehicleGunRotator__getGunMarkerInfo(shotPos, shotVec, dispersionAngles, gunRotator._VehicleGunRotator__gunIndex) # type: GunMarkerInfo
    endPos = marker.position
    endDir = marker.direction
    size = marker.size

  acceleration = Vector3(0, -gravity, 0)
  trajectoryPoints = computeProjectileTrajectoryWithEnd(endPos, shotPos, -shotVec, acceleration, SHELL_TRAJECTORY_EPSILON_CAMERA)
  trajectoryPoints.insert(0, endPos)

  diskPoints, tangent, bitangent = calculateLineDiskPoints(endPos, endDir, size, 64)

  return trajectoryPoints, diskPoints, tangent, bitangent

class AimingUtil(object):
  
  def __init__(self, panel):
    # type: (Panel) -> None
    global updateGunMarkerEvent, updateGunMarkerClientEvent, onShowTracerEvent

    self.serverTrajectory = drawer.createLine(points=[], color=SERVER_COLOR, backColor=SERVER_BACK_COLOR)
    self.serverCircle = drawer.createLine(points=[], color=SERVER_COLOR, backColor=SERVER_BACK_COLOR)
    self.clientTrajectory = drawer.createLine(points=[], color=CLIENT_COLOR, backColor=CLIENT_BACK_COLOR)
    self.clientCircle = drawer.createLine(points=[], color=CLIENT_COLOR, backColor=CLIENT_BACK_COLOR)

    self.showServerCircle = False
    self.showServerTrajectory = True
    self.showClientCircle = False
    self.showClientTrajectory = True
    self.preserveOnShot = False
    
    self.panel = panel
    self.header = self.panel.addHeaderLine('Aiming')
    self.panel.addCheckboxLine('Server aiming circle', self.showServerCircle, self.onShowServerCircleChanged)
    self.panel.addCheckboxLine('  Trajectory', self.showServerTrajectory, self.onShowServerTrajectoryChanged)
    self.panel.addCheckboxLine('Client aiming circle', self.showClientCircle, self.onShowClientCircleChanged)
    self.panel.addCheckboxLine('  Trajectory', self.showClientTrajectory, self.onShowClientTrajectoryChanged)
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

  def onUpdateGunMarker(self, obj, vehicleID, shotPos, shotVec, dispersionAngle, *a, **k):
    # type: (PlayerAvatar, int, Vector3, Vector3, float, Tuple, dict) -> None

    if not obj.gunRotator: return

    gravity = obj.getVehicleDescriptor().shot.gravity
    trajectoryPoints, diskPoints, tangent, bitangent = getGunLines(
      obj.gunRotator, shotPos, shotVec, [dispersionAngle, dispersionAngle, dispersionAngle, dispersionAngle], gravity)

    self.serverTrajectory.points = trajectoryPoints if self.showServerTrajectory else []
    self.serverCircle.points = diskPoints if self.showServerTrajectory and self.showServerCircle else []

  def onUpdateGunMarkerClient(self, obj, *a, **k):
    # type: (VehicleGunRotator, Tuple, dict) -> None

    shotPos, shotVec = obj.getCurShotPosition()
    dispersionAngles = obj._VehicleGunRotator__dispersionAngles
    gravity = obj._avatar.getVehicleDescriptor().shot.gravity

    trajectoryPoints, diskPoints, tangent, bitangent = getGunLines(obj, shotPos, shotVec, dispersionAngles, gravity)

    self.clientTrajectory.points = trajectoryPoints if self.showClientTrajectory else []
    self.clientCircle.points = diskPoints if self.showClientTrajectory and self.showClientCircle else []

  def onShowTracerEvent(self, obj, attackerID, *a, **k):
    if attackerID != BigWorld.player().playerVehicleID:
      return
    
    if not self.preserveOnShot:
      return
    
    if self.showServerTrajectory:
      drawer.createLine(points=self.serverTrajectory.points, color=SERVER_COLOR, backColor=SERVER_BACK_COLOR, timeout=5.0)
    
    if self.showServerCircle:
      drawer.createLine(points=self.serverCircle.points, color=SERVER_COLOR, backColor=SERVER_BACK_COLOR, timeout=5.0)

    if self.showClientTrajectory:
      drawer.createLine(points=self.clientTrajectory.points, color=CLIENT_COLOR, backColor=CLIENT_BACK_COLOR, timeout=5.0)

    if self.showClientCircle:
      drawer.createLine(points=self.clientCircle.points, color=CLIENT_COLOR, backColor=CLIENT_BACK_COLOR, timeout=5.0)

    

