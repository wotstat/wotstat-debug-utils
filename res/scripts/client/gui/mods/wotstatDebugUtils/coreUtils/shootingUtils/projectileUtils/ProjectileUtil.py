import BigWorld
import BattleReplay
from gui.debugUtils import gizmos, NiceColors
from visual_script_client.vehicle_common import TriggerListener
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from Vehicle import Vehicle
from helpers.CallbackDelayer import CallbackDelayer
from Event import SafeEvent
from Avatar import PlayerAvatar, getVehicleShootingPositions
from items import vehicles
import Math

from ....Logger import Logger
from .utils import Shot

import typing
if typing.TYPE_CHECKING:
  from ....ui.models.UiModel import Panel
  from ....gizmos.Marker import Marker
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
    self.showStartMarker = True

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
    global onShowTracerEvent, onStopTracerEvent, onExplodeProjectileEvent, onShotTriggeredEvent
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

    marker = gizmos.createMarker(position=gunPos, color=NiceColors.BLUE, size=3.0, text='Shoot 0.000s') if self.showStartMarker and self.trajectoryEnabled else None
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
