import math
import BigWorld
from gui.debugUtils import ui, gizmos, NiceColors, LineEnd, drawer, NiceColorsHex
from visual_script_client.vehicle_common import TriggerListener
import BattleReplay

from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from Vehicle import Vehicle
from Event import SafeEvent
from ProjectileMover import ProjectileMover
from Avatar import PlayerAvatar, getVehicleShootingPositions
from items import vehicles
from constants import SERVER_TICK_LENGTH
import Math

from ...Logger import Logger

from helpers.CallbackDelayer import CallbackDelayer, TimeDeltaMeter
from projectile_trajectory import computeProjectileTrajectory
SHELL_TRAJECTORY_EPSILON = 0.02

import typing
if typing.TYPE_CHECKING:
  from ...ui.models.UiModel import Panel
  from ...gizmos.Line import Line
  from ...gizmos.Marker import Marker
  from ...drawer.DrawerController import LineModel
  from typing import Tuple, Optional

logger = Logger.instance()

onShowTracerEvent = SafeEvent()
oldShowTracer = PlayerAvatar.showTracer
def showTracer(self, *a, **k):
  onShowTracerEvent(self, *a, **k)
  return oldShowTracer(self, *a, **k)
PlayerAvatar.showTracer = showTracer

onStopTracerEvent = SafeEvent()
oldStopTracer = PlayerAvatar.stopTracer
def stopTracer(self, *a, **k):
  onStopTracerEvent(self, *a, **k)
  return oldStopTracer(self, *a, **k)
PlayerAvatar.stopTracer = stopTracer

onExplodeProjectileEvent = SafeEvent()
oldExplodeProjectile = PlayerAvatar.explodeProjectile
def explodeProjectile(self, *a, **k):
  onExplodeProjectileEvent(self, *a, **k)
  return oldExplodeProjectile(self, *a, **k)
PlayerAvatar.explodeProjectile = explodeProjectile

onShotTriggeredEvent = SafeEvent()
class ShotTriggerListener(TriggerListener):

  def __init__(self, *args, **kwargs):
    super(ShotTriggerListener, self).__init__(*args, **kwargs)
    BigWorld.callback(1, self.subscribe)

  def onPlayerDiscreteShoot(self, *args, **kwargs):
    onShotTriggeredEvent()
    
  def onPlayerShoot(self, *args, **kwargs):
    onShotTriggeredEvent()
  
shotTriggerListener = ShotTriggerListener()

def estimateShotDuration(velocity, acceleration, D=1000.0):
  vx, vy, vz = velocity
  ax, ay, az = acceleration

  # horizontal direction from initial velocity
  vh = math.sqrt(vx*vx + vz*vz)
  if vh < 1e-9:
    return None

  if ax*ax + az*az < 1e-9:
    return D / vh

  dirx = vx / vh
  dirz = vz / vh

  v_par = vx*dirx + vz*dirz          # == vh
  a_par = ax*dirx + az*dirz          # horizontal accel along that direction

  # Solve: 0.5*a_par*t^2 + v_par*t - D = 0
  if abs(a_par) < 1e-12:
    return D / v_par  # back to linear

  A = 0.5 * a_par
  B = v_par
  C = -D
  disc = B*B - 4.0*A*C
  if disc < 0.0:
    return None

  sqrt_disc = math.sqrt(disc)
  t1 = (-B + sqrt_disc) / (2.0*A)
  t2 = (-B - sqrt_disc) / (2.0*A)

  # smallest positive time
  candidates = [t for t in (t1, t2) if t > 0.0]
  return min(candidates) if candidates else None

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
      # if we already have a trajectory, it means ricochet happened during the flight, so we need to estimate time offset for the ricochet trajectory
      time, distance = self.trajectory.estimateTimeAtPoint(startPoint)
      if time and distance < 0.5:
        timeOffset = time
        distanceOffset = self.trajectory.evaluateTrajectoryDistance(time)
    
    self.ricochetTrajectory = ProjectileTrajectory(self.projectileUtil, startPoint, startVelocity, acceleration, shotStartTime=self.startTime, timeOffset=timeOffset, distanceOffset=distanceOffset)

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

    trajectoryTime = self.trajectory.estimateTimeAtPoint(position) if self.trajectory is not None else None
    ricochetTime = self.ricochetTrajectory.estimateTimeAtPoint(position) if self.ricochetTrajectory is not None else None

    if not trajectoryTime and not ricochetTime:
      return None

    if trajectoryTime and not ricochetTime:
      bestTrajectory = self.trajectory

    elif ricochetTime and not trajectoryTime:
      bestTrajectory = self.ricochetTrajectory

    else:
      bestTrajectory = self.ricochetTrajectory if self.trajectory.endPoint else self.trajectory

    bestEstimate = trajectoryTime if bestTrajectory == self.trajectory else ricochetTime
    if bestEstimate[1] > 0.5:
      return None
    
    return bestTrajectory.setEnd(position, bestEstimate[0])

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
    
    self.trajectoryDrawer = TrajectoryDrawer(startPoint, startVelocity, acceleration, color=NiceColorsHex.GREEN, backColor=NiceColorsHex.YELLOW)
    self.intervalTrajectoryDrawer = TrajectoryDrawer(startPoint, startVelocity, acceleration, color=NiceColorsHex.RED, backColor=NiceColorsHex.ORANGE)
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

  def estimateTimeAtPoint(self, point, maxTime=None, samples=40):
    if maxTime is None:
      dx = point.x - self.startPoint.x
      dz = point.z - self.startPoint.z
      horizontalDistance = math.sqrt(dx*dx + dz*dz)
      maxTime = estimateShotDuration(self.startVelocity, self.acceleration, horizontalDistance)
      if maxTime is None:
        maxTime = self.projectileUtil.trajectoryDuration

    if maxTime is None or maxTime <= 0.0:
      return None, None

    bestTime = 0.0
    bestDistSq = None
    step = maxTime / float(samples)
    t = 0.0
    for _ in range(samples + 1):
      distSq = self.__distanceSquaredAtTime(point, t)
      if bestDistSq is None or distSq < bestDistSq:
        bestDistSq = distSq
        bestTime = t
      t += step

    # local refinement around bestTime
    window = step
    for _ in range(6):
      left = max(0.0, bestTime - window)
      right = min(maxTime, bestTime + window)
      for j in range(1, 5):
        t = left + (right - left) * (j / 5.0)
        distSq = self.__distanceSquaredAtTime(point, t)
        if distSq < bestDistSq:
          bestDistSq = distSq
          bestTime = t
      window *= 0.5

    return bestTime, math.sqrt(bestDistSq) if bestDistSq is not None else None

  def setEnd(self, point, time):
    self.endTime = time
    self.endPoint = point
    self.endDistance = self.evaluateTrajectoryDistance(time)
    self.updateTrajectoryLine()

    timeOffset = time + self.timeOffset if self.timeOffset else None
    distanceOffset = self.distanceOffset + self.endDistance if self.distanceOffset else None
    return time, self.endDistance, timeOffset, distanceOffset
  
  def evaluateTrajectoryDistance(self, time, eps=1e-12):
    """
    Arc length from time 0 to time t for constant-acceleration 3D motion.
    Python 2.7, no external libs.

    start_velocity: (vx, vy, vz)
    acceleration:   (ax, ay, az)
    returns: float (>= 0)
    """
    vx, vy, vz = self.startVelocity
    ax, ay, az = self.acceleration
    t = float(time)

    def dot(u1,u2,u3, v1,v2,v3): return u1*v1 + u2*v2 + u3*v3

    # A = |a|^2, B = 2 v0·a, C = |v0|^2
    A = float(dot(ax,ay,az, ax,ay,az))
    if A < eps:
      # ~zero acceleration => constant speed
      C = float(dot(vx,vy,vz, vx,vy,vz))
      return math.sqrt(C) * abs(t)

    B = float(2.0 * dot(vx,vy,vz, ax,ay,az))
    C = float(dot(vx,vy,vz, vx,vy,vz))

    # D = 4AC - B^2
    D = 4.0*A*C - B*B

    # Handle perfect-square case to avoid 0*log(0) issues
    if abs(D) < 1e-10:
      # sqrt(A t^2 + B t + C) = sqrt(A) * |t - t0|, t0 = -B/(2A)
      t0 = -B / (2.0*A)
      sqrtA = math.sqrt(A)

      # integrate |tau - t0| from 0..t (works for t>=0; for t<0 swap)
      def integral_abs_linear(u):
        # returns ∫_0^u |x - t0| dx for u>=0
        if t0 <= 0.0: return 0.5*u*u - t0*u
        elif u <= t0: return t0*u - 0.5*u*u
        else: return 0.5*t0*t0 + 0.5*(u - t0)*(u - t0)

      if t >= 0.0: return sqrtA * integral_abs_linear(t)
      else: return sqrtA * integral_abs_linear(-t)

    sqrtA = math.sqrt(A)
    A32 = A * sqrtA

    def F(x):
      # Antiderivative of sqrt(Ax^2 + Bx + C)
      S = math.sqrt(A*x*x + B*x + C)
      term1 = ((2.0*A*x + B) * S) / (4.0*A)
      arg = 2.0*sqrtA*S + 2.0*A*x + B
      term2 = (D / (8.0*A32)) * math.log(abs(arg))
      return term1 + term2

    L = F(t) - F(0.0)
    return abs(L)

  def updateTrajectoryLine(self):
    if self.projectileUtil.trajectoryEnabled:

      if not self.projectileUtil.oneTickInterval:
        if not self.projectileUtil.continuousTrajectory and self.endTime:
          self.trajectoryDrawer.draw(timeTo=self.endTime)
        else:
          endTime = estimateShotDuration(self.startVelocity, self.acceleration, 1000.0)
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
  
  def __evaluatePosition(self, time=None):
    if time is None:
      time = self.__getCurrentTime()

    return self.startPoint + self.startVelocity.scale(time) + self.acceleration.scale(0.5 * time * time)

  def __distanceSquaredAtTime(self, point, time):
    pos = self.__evaluatePosition(time)
    dx = pos.x - point.x
    dy = pos.y - point.y
    dz = pos.z - point.z
    return dx*dx + dy*dy + dz*dz
  
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
    marker.position = self.__evaluatePosition()
    distance = self.evaluateTrajectoryDistance(time)
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
  def __init__(self, startPoint, startVelocity, acceleration, color, backColor):
    self.startPoint = startPoint
    self.startVelocity = startVelocity
    self.acceleration = acceleration
    self.color = color
    self.backColor = backColor

    self.trajectoryLine = drawer.createLine(points=[], color=color, backColor=backColor)

  def draw(self, timeFrom=0.0, timeTo=5.0):
    if not self.trajectoryLine: return

    if timeFrom > timeTo:
      self.trajectoryLine.points = []
      return

    startPos = self.__evaluatePosition(timeFrom)
    startVel = self.__evaluateVelocity(timeFrom)

    points = computeProjectileTrajectory(startPos, startVel, self.acceleration, timeTo - timeFrom, SHELL_TRAJECTORY_EPSILON)
    points.insert(0, startPos)

    self.trajectoryLine.points = points

  def dispose(self):
    if self.trajectoryLine is not None:
      self.trajectoryLine.destroy()
      self.trajectoryLine = None

  def __evaluatePosition(self, time):
    return self.startPoint + self.startVelocity.scale(time) + self.acceleration.scale(0.5 * time * time)
  
  def __evaluateVelocity(self, time):
    return self.startVelocity + self.acceleration.scale(time)

class ProjectileUtil(CallbackDelayer):
  hangarSpace = dependency.descriptor(IHangarSpace)
  
  def __init__(self, panel):
    # type: (Panel) -> None
    global onShowTracerEvent, onStopTracerEvent, onExplodeProjectileEvent, onShotTriggeredEvent
    CallbackDelayer.__init__(self)

    self.shots = {} # type: dict[int, Shot]
    self.lastStartShootMarker = None # type: Optional[Tuple[int, Math.Vector3, Marker]]

    self.trajectoryEnabled = False
    self.trajectoryDuration = 5.0
    self.compensatedTicks = 0.0
    self.oneTickInterval = False
    self.continuousTrajectory = False

    self.showBulletMarker = True
    self.showEndMarker = True
    self.showStartMarker = False

    self.panel = panel
    self.header = self.panel.addHeaderLine('Projectile')
    self.panel.addCheckboxLine('Trajectory', self.trajectoryEnabled, self.onTrajectoryToggle)

    self.panel.addCheckboxLine('  1Tick interval', self.oneTickInterval, self.onOneTickIntervalToggle)
    self.panel.addCheckboxLine('  Continuous trajectory', self.continuousTrajectory, self.onContinuousTrajectoryToggle)
    if not BattleReplay.isPlaying():
      self.panel.addCheckboxLine('  Shoot marker', self.showStartMarker, self.onStartMarkerToggle)
    self.panel.addCheckboxLine('  End marker', self.showEndMarker, self.onEndMarkerToggle)

    self.panel.addCheckboxLine('  Bullet marker', self.showBulletMarker, self.onShowBulletMarkerToggle)
    self.compensatedTicksLine = self.panel.addNumberInputLine('  Compensate ticks', value=self.compensatedTicks, onChangeCallback=self.onCompensatedTicksChange)

    self.durationLine = self.panel.addNumberInputLine('Duration', value=self.trajectoryDuration, onChangeCallback=self.onDurationChange)
    
    onShowTracerEvent += self.handleShowTracerEvent
    onStopTracerEvent += self.handleStopTracerEvent
    onExplodeProjectileEvent += self.handleExplodeProjectileEvent
    onShotTriggeredEvent += self.handleTriggerShootEvent

    self.showStaticCollisionEvents = False
    self.delayCallback(0, self.update)

  def onTrajectoryToggle(self, isEnabled):
    self.trajectoryEnabled = isEnabled
    self.updateAllShotsTrajectoryLine()
    self.updateAllShotsEndMarkersVisibility()
    self.updateAllShotsShootMarkerVisibility()

  def onContinuousTrajectoryToggle(self, isEnabled):
    self.continuousTrajectory = isEnabled
    self.updateAllShotsTrajectoryLine()

  def onCompensatedTicksChange(self, value):
    clampedValue = max(0, min(3, int(value)))
    if clampedValue != value: self.compensatedTicksLine.value = clampedValue
    self.compensatedTicks = clampedValue

  def onDurationChange(self, value):
    clampedValue = max(0.1, min(20.0, value))
    if clampedValue != value: self.durationLine.value = clampedValue
    self.trajectoryDuration = clampedValue
  
  def onOneTickIntervalToggle(self, isEnabled):
    self.oneTickInterval = isEnabled
    self.updateAllShotsTrajectoryLine()
  
  def onShowBulletMarkerToggle(self, isEnabled):
    self.showBulletMarker = isEnabled

  def onStartMarkerToggle(self, isEnabled):
    self.showStartMarker = isEnabled
    self.updateAllShotsShootMarkerVisibility()

  def onEndMarkerToggle(self, isEnabled):
    self.showEndMarker = isEnabled
    self.updateAllShotsEndMarkersVisibility()

  def dispose(self):
    global onShowTracerEvent
    onShowTracerEvent -= self.handleShowTracerEvent
    onStopTracerEvent -= self.handleStopTracerEvent
    onExplodeProjectileEvent -= self.handleExplodeProjectileEvent
    onShotTriggeredEvent -= self.handleTriggerShootEvent

    self.clearCallbacks()
    for shot in self.shots.values():
      shot.dispose()
    self.shots.clear()

  def update(self):
    for shotID, shot in list(self.shots.items()):
      shot.update()

    if self.lastStartShootMarker is not None:
      startTime, pos, marker = self.lastStartShootMarker
      elapsed = BigWorld.time() - startTime
      if elapsed > self.trajectoryDuration:
        if marker: marker.destroy()
        self.lastStartShootMarker = None
      else:
        if marker:
          marker.text = 'Shoot -%.3fs' % elapsed

    return 0
  
  def updateAllShotsTrajectoryLine(self):
    for shot in self.shots.values():
      shot.updateTrajectoryLine()

  def updateAllShotsEndMarkersVisibility(self):
    for shot in self.shots.values():
      shot.updateEndMarkersVisibility()

  def updateAllShotsShootMarkerVisibility(self):
    for shot in self.shots.values():
      shot.updateShootMarkerVisibility()

  def disposeShot(self, shotID):
    shot = self.shots.pop(shotID, None)
    if shot is not None:
      shot.dispose()

  def handleTriggerShootEvent(self, *a, **k):
    vehicle = BigWorld.entity(BigWorld.player().playerVehicleID) # type: Vehicle
    gunPos, _ = getVehicleShootingPositions(vehicle)
    if self.lastStartShootMarker:
      _, pos, marker = self.lastStartShootMarker
      if marker: marker.destroy()

    marker = gizmos.createMarker(position=gunPos, color=NiceColors.BLUE, size=3.0, text='Shoot 0.000s') if self.showStartMarker else None
    self.lastStartShootMarker = (BigWorld.time(), gunPos, marker)

  def handleShowTracerEvent(self, obj, *a, **k):
    if not self.trajectoryEnabled and not self.showBulletMarker:
      return
    
    if len(a) == 13:
      attackerID, shotID, isRicochet, effectsIndex, prefabEffIndex, shellTypeIdx, shellCaliber, refStartPoint, refVelocity, gravity, maxShotDist, gunIndex, gunInstallationIndex = a
      acceleration = Math.Vector3(0.0, -gravity, 0.0)
    elif len(a) == 9:
      attackerID, shotID, isRicochet, effectsIndex, refStartPoint, refVelocity, gravityOrAcceleration, maxShotDist, gunIndex = a
      prefabEffIndex = shellTypeIdx = shellCaliber = None
      acceleration = gravityOrAcceleration
      gravity = -acceleration.y

    logger.info('ProjectileUtil: showTracerEvent: attackerID=%d, shotID=%d, isRicochet=%s, effectsIndex=%d, prefabEffIndex=%s, shellTypeIdx=%s, shellCaliber=%s, refStartPoint=%s, refVelocity=%s, gravity=%s, maxShotDist=%s, gunIndex=%d' % (attackerID, shotID, isRicochet, effectsIndex, prefabEffIndex, shellTypeIdx, shellCaliber, refStartPoint, refVelocity, gravity, maxShotDist, gunIndex))

    vehicle = BigWorld.entity(attackerID) # type: Vehicle
    shot = self.shots.get(shotID, Shot(self))
    self.shots[shotID] = shot

    projectileSpeedFactor = vehicles.g_cache.commonConfig['miscParams']['projectileSpeedFactor']
    if isRicochet:
      shot.addRicochet(refStartPoint, refVelocity / projectileSpeedFactor, acceleration / (projectileSpeedFactor ** 2))
    else:
      if self.lastStartShootMarker:
        startTime, pos, marker = self.lastStartShootMarker
        if marker: marker.destroy()
        self.lastStartShootMarker = None
        shot.addShootMarker(startTime, pos)

      shot.addProjectile(refStartPoint, refVelocity / projectileSpeedFactor, acceleration / (projectileSpeedFactor ** 2))

    BigWorld.callback(self.trajectoryDuration, lambda: self.disposeShot(shotID))

  def handleStopTracerEvent(self, obj, shotID, endPoint):
    logger.info('ProjectileUtil: stopTracerEvent: shotID=%d, endPoint=%s' % (shotID, endPoint))
    shot = self.shots.get(shotID)
    if shot is not None:
      shot.addEndPoint(endPoint)

  def handleExplodeProjectileEvent(self, obj, *a, **k):
    if len(a) == 10:
      shotID, effectsIndex, prefabEffIndex, effectMaterialIndex, shellTypeIdx, shellCaliber, endPoint, velocityDir, speed, damagedDestructibles = a
    elif len(a) == 6:
      shotID, effectsIndex, effectMaterialIndex, endPoint, velocityDir, damagedDestructibles = a
      prefabEffIndex = shellTypeIdx = shellCaliber = None
      
    logger.info('ProjectileUtil: explodeProjectileEvent: shotID=%d, effectsIndex=%d, prefabEffIndex=%s, effectMaterialIndex=%d, shellTypeIdx=%s, shellCaliber=%s, endPoint=%s, velocityDir=%s' % (shotID, effectsIndex, prefabEffIndex, effectMaterialIndex, shellTypeIdx, shellCaliber, endPoint, velocityDir))

    shot = self.shots.get(shotID)
    if shot is not None:
      shot.addExplosion(endPoint)
