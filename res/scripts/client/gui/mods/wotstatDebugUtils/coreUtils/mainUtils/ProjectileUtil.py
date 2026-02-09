import math
import BigWorld
from gui.debugUtils import ui, gizmos, NiceColors, LineEnd, drawer, NiceColorsHex

from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from Vehicle import Vehicle
from Event import SafeEvent
from ProjectileMover import ProjectileMover
from Avatar import PlayerAvatar
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


class Shot(object):
  def __init__(self, projectileUtil):
    # type: (ProjectileUtil) -> None
    self.projectileUtil = projectileUtil
    self.startTime = BigWorld.time()

    self.trajectory = None # type: ProjectileTrajectory
    self.ricochetTrajectory = None # type: ProjectileTrajectory

    self.markers = [] # type: list[Marker]

  def addProjectile(self, startPoint, startVelocity, acceleration):
    self.trajectory = ProjectileTrajectory(self.projectileUtil, startPoint, startVelocity, acceleration)
    
  def addRicochet(self, startPoint, startVelocity, acceleration):
    self.ricochetTrajectory = ProjectileTrajectory(self.projectileUtil, startPoint, startVelocity, acceleration, shotStartTime=self.startTime)

  def addEndPoint(self, position):
    self.addEndMarker(position, 'Hit')

  def addExplosion(self, position):
    self.addEndMarker(position, 'Explosion')

  def addEndMarker(self, position, kind):
    addedTime = BigWorld.time() - self.startTime
    pos = self.__assignTrajectoryEnd(position)
    if pos:
      time, distance = pos
      self.markers.append(gizmos.createMarker(position=position, color=NiceColors.GREEN, size=3.0, text='%s %.1fm/%.3fs (%.3fs)' % (kind, distance, time, addedTime)))
    else:
      self.markers.append(gizmos.createMarker(position=position, color=NiceColors.RED, size=3.0, text='%s (%.3fs)' % (kind, addedTime)))

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
  def __init__(self, projectileUtil, startPoint, startVelocity, acceleration, shotStartTime=None):
    # type: (ProjectileUtil, Math.Vector3, Math.Vector3, Math.Vector3, str) -> None
    self.projectileUtil = projectileUtil
    self.startPoint = startPoint
    self.startVelocity = startVelocity
    self.acceleration = acceleration
    self.startTime = BigWorld.time()
    self.shotStartTime = shotStartTime
    self.trajectoryLine = None # type: Line | LineModel | None
    self.endTime = None
    self.endPoint = None
    self.endDistance = None

    self.marker = gizmos.createMarker(position=startPoint, color=NiceColors.GREEN, size=5.0)
    self.__setupTrajectoryLine()

  def __setupTrajectoryLine(self):
    if self.trajectoryLine is not None:
      self.trajectoryLine.destroy()

    if self.projectileUtil.trajectoryEnabled:
      points = self.computeTrajectory(duration=self.endTime)
      if self.projectileUtil.trajectoryLine3D:
        self.trajectoryLine = drawer.createLine(points=points, color=NiceColorsHex.GREEN, backColor=NiceColorsHex.YELLOW)
      else:
        self.trajectoryLine = gizmos.createPolyLine(points=points, color=NiceColors.GREEN)

  def dispose(self):
    if self.marker is not None:
      self.marker.destroy()
      self.marker = None

    if self.trajectoryLine is not None:
      self.trajectoryLine.destroy()
      self.trajectoryLine = None

  def computeTrajectory(self, distance=1000.0, duration=None):
    duration = estimateShotDuration(self.startVelocity, self.acceleration, distance) if duration is None else duration
    points = computeProjectileTrajectory(self.startPoint, self.startVelocity, self.acceleration, duration, SHELL_TRAJECTORY_EPSILON)
    points.insert(0, self.startPoint)
    return points

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
    self.__setupTrajectoryLine()
    return time, self.endDistance
  
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

  def __getCurrentTime(self):
    time = BigWorld.time() - self.startTime
    if self.projectileUtil.compensateTickrate:
      time += SERVER_TICK_LENGTH
    return time

  def evaluatePosition(self, time=None):
    if time is None:
      time = self.__getCurrentTime()

    return self.startPoint + self.startVelocity.scale(time) + self.acceleration.scale(0.5 * time * time)

  def __distanceSquaredAtTime(self, point, time):
    pos = self.evaluatePosition(time)
    dx = pos.x - point.x
    dy = pos.y - point.y
    dz = pos.z - point.z
    return dx*dx + dy*dy + dz*dz
  
  def update(self):
    if self.marker is not None:
      self.marker.position = self.evaluatePosition()
      time = self.__getCurrentTime()
      if self.shotStartTime:
        totalTime = BigWorld.time() - self.shotStartTime
        text = '%.1fm/%.3fs/%.3fs' % (self.evaluateTrajectoryDistance(time), time, totalTime)
      else:
        text = '%.1fm/%.3fs' % (self.evaluateTrajectoryDistance(time), time)

      self.marker.text = text


class ProjectileUtil(CallbackDelayer):
  hangarSpace = dependency.descriptor(IHangarSpace)
  
  def __init__(self, panel):
    # type: (Panel) -> None
    global onShowTracerEvent, onStopTracerEvent, onExplodeProjectileEvent
    CallbackDelayer.__init__(self)

    self.shots = {} # type: dict[int, Shot]

    self.trajectoryEnabled = False
    self.compensateTickrate = False
    self.compensateSpeedFactor = False
    self.trajectoryLine3D = True
    self.trajectoryDuration = 5.0

    self.bulletsMarker = True
    self.bulletsInfoText = False
    self.bulletsSphere3D = False

    self.panel = panel
    self.header = self.panel.addHeaderLine('Projectile')
    self.panel.addCheckboxLine('Trajectory', onToggleCallback=self.onTrajectoryToggle)
    self.panel.addCheckboxLine('  Compensate Tickrate', onToggleCallback=self.onCompensateTickrateToggle)
    self.panel.addCheckboxLine('  Apply speed factor (x0.8)', onToggleCallback=self.onCompensateSpeedFactorToggle)
    self.panel.addCheckboxLine('  Line 3D', isChecked=True, onToggleCallback=self.onLine3DToggle)
    self.durationLine = self.panel.addNumberInputLine('  Duration', value=self.trajectoryDuration, onChangeCallback=self.onDurationChange)

    self.panel.addTextLine('Bullets')
    self.panel.addCheckboxLine('  Marker', isChecked=self.bulletsMarker, onToggleCallback=None)
    self.panel.addCheckboxLine('  Info text', onToggleCallback=None)
    self.panel.addCheckboxLine('  Sphere 3D', onToggleCallback=None)
    onShowTracerEvent += self.handleShowTracerEvent
    onStopTracerEvent += self.handleStopTracerEvent
    onExplodeProjectileEvent += self.handleExplodeProjectileEvent
    
    self.showStaticCollisionEvents = False
    self.delayCallback(0, self.update)

  def onTrajectoryToggle(self, isEnabled):
    self.trajectoryEnabled = isEnabled

  def onCompensateTickrateToggle(self, isEnabled):
    self.compensateTickrate = isEnabled

  def onLine3DToggle(self, isEnabled):
    self.trajectoryLine3D = isEnabled

  def onCompensateSpeedFactorToggle(self, isEnabled):
    self.compensateSpeedFactor = isEnabled

  def onDurationChange(self, value):
    clampedValue = max(0.1, min(20.0, value))
    if clampedValue != value: self.durationLine.value = clampedValue
    self.trajectoryDuration = clampedValue
    
  def dispose(self):
    global onShowTracerEvent
    onShowTracerEvent -= self.handleShowTracerEvent
    onStopTracerEvent -= self.handleStopTracerEvent
    onExplodeProjectileEvent -= self.handleExplodeProjectileEvent
    self.clearCallbacks()
    for shot in self.shots.values():
      shot.dispose()
    self.shots.clear()

  def update(self):
    for shotID, shot in list(self.shots.items()):
      shot.update()

    return 0
  
  def disposeShot(self, shotID):
    shot = self.shots.pop(shotID, None)
    if shot is not None:
      shot.dispose()

  def handleShowTracerEvent(self, obj, *a, **k):
    if not self.trajectoryEnabled and not self.bulletsMarker and not self.bulletsInfoText and not self.bulletsSphere3D:
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

    projectileSpeedFactor = vehicles.g_cache.commonConfig['miscParams']['projectileSpeedFactor'] if not self.compensateSpeedFactor else 1.0
    if isRicochet:
      shot.addRicochet(refStartPoint, refVelocity / projectileSpeedFactor, acceleration / (projectileSpeedFactor ** 2))
    else:
      shot.addProjectile(refStartPoint, refVelocity / projectileSpeedFactor, acceleration / (projectileSpeedFactor ** 2))

    BigWorld.callback(self.trajectoryDuration, lambda: self.disposeShot(shotID))

  def handleStopTracerEvent(self, obj, shotID, endPoint):
    logger.info('ProjectileUtil: stopTracerEvent: shotID=%d, endPoint=%s' % (shotID, endPoint))
    shot = self.shots.get(shotID)
    if shot is not None:
      shot.addEndPoint(endPoint)

  def handleExplodeProjectileEvent(self, obj, *a, **k):
    if len(a) == 8:
      shotID, effectsIndex, prefabEffIndex, effectMaterialIndex, shellTypeIdx, shellCaliber, endPoint, velocityDir = a
    elif len(a) == 6:
      shotID, effectsIndex, effectMaterialIndex, endPoint, velocityDir, damagedDestructibles = a
      prefabEffIndex = shellTypeIdx = shellCaliber = None
      
    logger.info('ProjectileUtil: explodeProjectileEvent: shotID=%d, effectsIndex=%d, prefabEffIndex=%s, effectMaterialIndex=%d, shellTypeIdx=%s, shellCaliber=%s, endPoint=%s, velocityDir=%s' % (shotID, effectsIndex, prefabEffIndex, effectMaterialIndex, shellTypeIdx, shellCaliber, endPoint, velocityDir))

    shot = self.shots.get(shotID)
    if shot is not None:
      shot.addExplosion(endPoint)
