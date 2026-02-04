import BigWorld
from gui.debugUtils import ui, gizmos, NiceColors, LineEnd, drawer, NiceColorsHex

from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from Vehicle import Vehicle
from Event import SafeEvent
from ProjectileMover import ProjectileMover
from Avatar import PlayerAvatar
import Math

import typing
if typing.TYPE_CHECKING:
  from ...ui.models.UiModel import Panel


onAddProjectileEvent = SafeEvent()
oldAddProjectile = ProjectileMover.add
def onAddProjectile(self, *a, **k):
  onAddProjectileEvent(self, *a, **k)
  return oldAddProjectile(self, *a, **k)
ProjectileMover.add = onAddProjectile


onShowTracerEvent = SafeEvent()
oldShowTracer = PlayerAvatar.showTracer
def showTracer(self, *a, **k):
  onShowTracerEvent(self, *a, **k)
  return oldShowTracer(self, *a, **k)
PlayerAvatar.showTracer = showTracer

def calculateProjectileTrajectory(beginPoint, velocity, acceleration, duration, timeStep=0.05):
  points = []
  time = 0.0
  while time < duration:
    point = beginPoint + velocity.scale(time) + acceleration.scale(0.5 * time * time)
    points.append(point)
    time += timeStep
  return points


class ProjectileUtil(object):
  hangarSpace = dependency.descriptor(IHangarSpace)
  
  def __init__(self, panel):
    # type: (Panel) -> None
    global onShowTracerEvent

    self.trajectoryEnabled = False
    self.trajectoryFromAll = False
    self.trajectoryLine3D = True
    self.trajectoryDuration = 5.0

    self.bulletsMarker = True
    self.bulletsInfoText = False
    self.bulletsSphere3D = False


    self.panel = panel
    self.header = self.panel.addHeaderLine('Projectile')
    self.panel.addCheckboxLine('Trajectory', onToggleCallback=self.onTrajectoryToggle)
    self.panel.addCheckboxLine('  From all', onToggleCallback=self.onFromAllToggle)
    self.panel.addCheckboxLine('  Line 3D', isChecked=True, onToggleCallback=self.onLine3DToggle)
    self.durationLine = self.panel.addNumberInputLine('  Duration', value=self.trajectoryDuration, onChangeCallback=self.onDurationChange)

    self.panel.addTextLine('Bullets')
    self.panel.addCheckboxLine('  Marker', isChecked=self.bulletsMarker, onToggleCallback=None)
    self.panel.addCheckboxLine('  Info text', onToggleCallback=None)
    self.panel.addCheckboxLine('  Sphere 3D', onToggleCallback=None)
    onShowTracerEvent += self.handleShowTracerEvent
    
    self.showStaticCollisionEvents = False

  def onTrajectoryToggle(self, isEnabled):
    self.trajectoryEnabled = isEnabled

  def onFromAllToggle(self, isEnabled):
    self.trajectoryFromAll = isEnabled

  def onLine3DToggle(self, isEnabled):
    self.trajectoryLine3D = isEnabled

  def onDurationChange(self, value):
    clampedValue = max(0.1, min(20.0, value))
    if clampedValue != value: self.durationLine.value = clampedValue
    self.trajectoryDuration = clampedValue
    
  def dispose(self):
    global onShowTracerEvent
    onShowTracerEvent -= self.handleShowTracerEvent


  def handleShowTracerEvent(self, obj, *a, **k):
    
    if len(a) == 13:
      attackerID, shotID, isRicochet, effectsIndex, prefabEffIndex, shellTypeIdx, shellCaliber, refStartPoint, refVelocity, gravity, maxShotDist, gunIndex, gunInstallationIndex = a
      acceleration = Math.Vector3(0.0, -gravity, 0.0)
    elif len(a) == 9:
      attackerID, shotID, isRicochet, effectsIndex, refStartPoint, refVelocity, gravityOrAcceleration, maxShotDist, gunIndex = a
      prefabEffIndex = shellTypeIdx = shellCaliber = None
      acceleration = gravityOrAcceleration
      gravity = -acceleration.y


    vehicle = BigWorld.entity(attackerID) # type: Vehicle

    points = calculateProjectileTrajectory(refStartPoint, refVelocity, acceleration, self.trajectoryDuration)
    if self.trajectoryEnabled:
      if self.trajectoryLine3D:
        drawer.createLine(points=points, color=NiceColorsHex.GREEN, backColor=NiceColorsHex.YELLOW, timeout=self.trajectoryDuration)
      else:
        gizmos.createPolyLine(points=points, color=NiceColors.GREEN, timeout=self.trajectoryDuration)