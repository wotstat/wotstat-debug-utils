import BigWorld
from gui.debugUtils import gizmos, NiceColors, drawer, NiceColorsHex
from constants import SERVER_TICK_LENGTH
import Math
from ..BallisticTrajectory import BallisticTrajectory

SHELL_TRAJECTORY_EPSILON = 0.02

import typing
if typing.TYPE_CHECKING:
  from ....gizmos.Marker import Marker
  from .ProjectileUtil import ProjectileUtil
  from typing import Tuple, Optional

def clamp(minValue, maxValue, value):
  return max(minValue, min(maxValue, value))

class Shot(object):
  def __init__(self, projectileUtil):
    # type: (ProjectileUtil) -> None
    self.projectileUtil = projectileUtil
    self.startTime = BigWorld.time()

    self.shootTime = None
    self.shootPosition = None # type: Optional[Math.Vector3]
    self.shootMarker = None # type: Optional[Marker]

    self.trajectory = None # type: ProjectileTrajectory
    self.ricochetTrajectory = None # type: ProjectileTrajectory

    self.endMarkersData = [] # type: list[Tuple[Math.Vector3, int, str]]
    self.markers = [] # type: list[Marker]

  def addShootMarker(self, shootTime, position):
    self.shootTime = shootTime
    self.shootPosition = position
    self.updateShootMarkerVisibility()

  def addProjectile(self, startPoint, startVelocity, acceleration):
    self.trajectory = ProjectileTrajectory(self.projectileUtil, startPoint, startVelocity, acceleration)
    
  def addRicochet(self, startPoint, startVelocity, acceleration):
    timeOffset = 0.0
    distanceOffset = 0.0

    if self.trajectory:
      calc = self.trajectory.trajectoryCalc
      _, time, distance = calc.getNearestPoint(startPoint, timeFrom=0.0)
      if time and distance < 0.5:
        timeOffset = time
        distanceOffset = calc.getTrajectoryDistance(time)
    
    self.ricochetTrajectory = ProjectileTrajectory(
      self.projectileUtil, 
      startPoint, startVelocity, acceleration, 
      shotStartTime=self.startTime, 
      timeOffset=timeOffset, distanceOffset=distanceOffset)

  def addEndPoint(self, position):
    self.addEndMarker(position, 'Hit')

  def addExplosion(self, position):
    self.addEndMarker(position, 'Explosion')

  def addEndMarker(self, position, kind):
    addedTime = BigWorld.time() - self.startTime
    pos = self.__assignTrajectoryEnd(position)
    
    endMarker = None
    if pos:
      time, distance, timeOffset, distanceOffset = pos
      if timeOffset and distanceOffset:
        text = '%s %.1fm/%.3fs (%.1fm/%.3fs) (%.3fs)' % (kind, distance, time, distanceOffset, timeOffset, addedTime)
        endMarker = (position, NiceColors.GREEN, text)
      else:
        endMarker = (position, NiceColors.GREEN, '%s %.1fm/%.3fs (%.3fs)' % (kind, distance, time, addedTime))
    else:
      endMarker = (position, NiceColors.RED, '%s (%.3fs)' % (kind, addedTime))

    if endMarker:
      self.endMarkersData.append(endMarker)
      if self.projectileUtil.showEndMarker and self.projectileUtil.trajectoryEnabled:
        position, color, text = endMarker
        self.markers.append(gizmos.createMarker(position=position, color=color, size=3.0, text=text))

  def dispose(self):
    if self.trajectory is not None:
      self.trajectory.dispose()
      self.trajectory = None

    if self.ricochetTrajectory is not None:
      self.ricochetTrajectory.dispose()
      self.ricochetTrajectory = None

    for marker in self.markers:
      marker.destroy()
    self.markers = []

    if self.shootMarker is not None:
      self.shootMarker.destroy()
      self.shootMarker = None
    
  def updateTrajectoryLine(self):
    if self.trajectory is not None:
      self.trajectory.updateTrajectoryLine()

    if self.ricochetTrajectory is not None:
      self.ricochetTrajectory.updateTrajectoryLine()

  def updateEndMarkersVisibility(self):
    visible = self.projectileUtil.showEndMarker and self.projectileUtil.trajectoryEnabled
    if not visible and len(self.markers) > 0:
      for marker in self.markers: marker.destroy()
      self.markers = []
    elif visible and len(self.markers) == 0:
      for (position, color, text) in self.endMarkersData:
        self.markers.append(gizmos.createMarker(position=position, color=color, size=3.0, text=text))

  def updateShootMarkerVisibility(self):
    visible = self.projectileUtil.showStartMarker and self.projectileUtil.trajectoryEnabled

    if not visible:
      if self.shootMarker:
        self.shootMarker.destroy()
        self.shootMarker = None
    elif visible:
      if self.shootTime:
        if self.shootMarker: self.shootMarker.destroy()
        self.shootMarker = gizmos.createMarker(position=self.shootPosition, color=NiceColors.BLUE, size=5.0, text='Shoot -%.3fs' % (self.startTime - self.shootTime))

  def update(self):
    if self.trajectory is not None:
      self.trajectory.update()

    if self.ricochetTrajectory is not None:
      self.ricochetTrajectory.update()

  def __assignTrajectoryEnd(self, position):
    bestTrajectory = None

    trajectoryTime = self.trajectory.trajectoryCalc.getNearestPoint(position) if self.trajectory is not None else None
    ricochetTime = self.ricochetTrajectory.trajectoryCalc.getNearestPoint(position) if self.ricochetTrajectory is not None else None

    if not trajectoryTime and not ricochetTime:
      return None

    if trajectoryTime and not ricochetTime:
      bestTrajectory = self.trajectory

    elif ricochetTime and not trajectoryTime:
      bestTrajectory = self.ricochetTrajectory

    else:
      bestTrajectory = self.ricochetTrajectory if self.trajectory.endPoint else self.trajectory

    bestEstimate = trajectoryTime if bestTrajectory == self.trajectory else ricochetTime
    if bestEstimate[2] > 0.5:
      return None
    
    return bestTrajectory.setEnd(position, bestEstimate[1])

class ProjectileTrajectory():
  def __init__(self, projectileUtil, startPoint, startVelocity, acceleration, shotStartTime=None, timeOffset=0.0, distanceOffset=0.0):
    # type: (ProjectileUtil, Math.Vector3, Math.Vector3, Math.Vector3, float, float, float) -> None
    self.projectileUtil = projectileUtil
    self.startPoint = startPoint
    self.startVelocity = startVelocity
    self.acceleration = acceleration

    self.shotStartTime = shotStartTime if shotStartTime else BigWorld.time()
    self.timeOffset = timeOffset
    self.distanceOffset = distanceOffset
    
    self.trajectoryCalc = BallisticTrajectory(startPoint, startVelocity, acceleration)
    self.trajectoryDrawer = TrajectoryDrawer(self.trajectoryCalc, color=NiceColorsHex.GREEN, backColor=NiceColorsHex.YELLOW)
    self.intervalTrajectoryDrawer = TrajectoryDrawer(self.trajectoryCalc, color=NiceColorsHex.RED, backColor=NiceColorsHex.ORANGE)
    self.endTime = None
    self.endPoint = None
    self.endDistance = None
    self.marker = None # type: Marker | None

    self.updateTrajectoryLine()

  def dispose(self):
    if self.marker is not None:
      self.marker.destroy()
      self.marker = None

    self.trajectoryDrawer.dispose()
    self.intervalTrajectoryDrawer.dispose()

  def setEnd(self, point, time):
    self.endTime = time
    self.endPoint = point
    self.endDistance = self.trajectoryCalc.getTrajectoryDistance(time)
    self.updateTrajectoryLine()

    timeOffset = time + self.timeOffset if self.timeOffset else None
    distanceOffset = self.distanceOffset + self.endDistance if self.distanceOffset else None
    return time, self.endDistance, timeOffset, distanceOffset

  def updateTrajectoryLine(self):
    if self.projectileUtil.trajectoryEnabled:

      if not self.projectileUtil.oneTickInterval:
        if not self.projectileUtil.continuousTrajectory and self.endTime:
          self.trajectoryDrawer.draw(timeTo=self.endTime)
        else:
          endTime = self.trajectoryCalc.getTimeAtDistance(1000) or 5.0
          self.trajectoryDrawer.draw(timeTo=endTime)
      else:
        self.trajectoryDrawer.draw(timeTo=-1)

    else:
      self.trajectoryDrawer.draw(timeTo=-1)
      self.intervalTrajectoryDrawer.draw(timeTo=-1)
      
  def __getCurrentTime(self):
    time = BigWorld.time() - self.shotStartTime - self.timeOffset
    time += SERVER_TICK_LENGTH * self.projectileUtil.compensatedTicks
    return time
  
  def __getBulletMarker(self):
    if self.marker:
      return self.marker
    
    self.marker = gizmos.createMarker(position=self.startPoint, color=NiceColors.GREEN, size=5.0)
    return self.marker
  
  def __destroyBulletMarker(self):
    if self.marker:
      self.marker.destroy()
      self.marker = None

  def __updateBulletMarker(self):
    time = self.__getCurrentTime()

    if time < 0.0 or (self.endTime and time > self.endTime and not self.projectileUtil.continuousTrajectory) or not self.projectileUtil.showBulletMarker or not self.projectileUtil.trajectoryEnabled:
      self.__destroyBulletMarker()
      return
    
    marker = self.__getBulletMarker()
    marker.position = self.trajectoryCalc.getPoint(time)
    distance = self.trajectoryCalc.getTrajectoryDistance(time)
    if self.distanceOffset:
      text = '%.1fm/%.3fs (%.1fm/%.3fs)' % (distance, time, distance + self.distanceOffset, time + self.timeOffset)
    else:
      text = '%.1fm/%.3fs' % (distance, time)

    if self.endTime and time > self.endTime:
      text += ' (past end)'

    marker.text = text

  def __updateOneTickInterval(self):
    maxTime = self.endTime if self.endTime and not self.projectileUtil.continuousTrajectory else 100
    time = self.__getCurrentTime()
    startTime = max(0, time)
    endTime = clamp(0, maxTime, time + SERVER_TICK_LENGTH)

    if endTime < 0.0 or not self.projectileUtil.oneTickInterval or not self.projectileUtil.trajectoryEnabled:
      self.intervalTrajectoryDrawer.draw(timeTo=-1)
      return

    self.intervalTrajectoryDrawer.draw(timeFrom=startTime, timeTo=endTime)

  def update(self):
    self.__updateBulletMarker()
    self.__updateOneTickInterval()

class TrajectoryDrawer(object):
  def __init__(self, trajectoryCalc, color, backColor):
    # type: (int, int, BallisticTrajectory) -> None
    self.color = color
    self.backColor = backColor
    self.trajectoryCalc = trajectoryCalc

    self.trajectoryLine = drawer.createLine(points=[], color=color, backColor=backColor)

  def draw(self, timeFrom=0.0, timeTo=5.0):
    if not self.trajectoryLine: return

    if timeFrom > timeTo:
      self.trajectoryLine.points = []
      return

    self.trajectoryLine.points = self.trajectoryCalc.getTrajectoryPoints(timeFrom, timeTo, SHELL_TRAJECTORY_EPSILON)

  def dispose(self):
    if self.trajectoryLine is not None:
      self.trajectoryLine.destroy()
      self.trajectoryLine = None
