import BigWorld, GUI, Math, math
import Keys
from gui import InputHandler
from AvatarInputHandler import cameras
from gui.debugUtils import ui, gizmos, NiceColors, LineEnd

from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
from shared_utils.vehicle_utils import getMatinfo
from Vehicle import Vehicle
from Event import SafeEvent
from ProjectileMover import EntityCollisionData
import typing
if typing.TYPE_CHECKING:
  from ...gizmos.PolyLine import PolyLine
  from ...gizmos.Marker import Marker
  from ...ui.models.UiModel import Panel


onStaticCollisionEvent = SafeEvent()
oldOnStaticCollision = Vehicle.onStaticCollision
def onStaticCollision(*a, **k):
  onStaticCollisionEvent(*a, **k)
  return oldOnStaticCollision(*a, **k)

Vehicle.onStaticCollision = onStaticCollision


# collideSegment = BigWorld.wg_collideSegment if hasattr(BigWorld, 'wg_collideSegment') else BigWorld.collideSegment
class PhysicsUtil(object):
  hangarSpace = dependency.descriptor(IHangarSpace)
  
  def __init__(self, panel):
    # type: (Panel) -> None
    global onStaticCollisionEvent
    self.panel = panel
    self.header = self.panel.addHeaderLine('Physics')
    self.panel.addCheckboxLine('Static collision events', onToggleCallback=self.onStaticCollisionToggle)
    self.panel.addCheckboxLine('  Info text', onToggleCallback=self.onInfoTextToggle)
    self.panel.addCheckboxLine('  From all', onToggleCallback=self.onFromAllToggle)
    onStaticCollisionEvent += self.handleStaticCollisionEvent
    
    self.showStaticCollisionEvents = False
    
  def dispose(self):
    global onStaticCollisionEvent
    onStaticCollisionEvent -= self.handleStaticCollisionEvent
    
  def onStaticCollisionToggle(self, value):
    self.showStaticCollisionEvents = value
    
  def onInfoTextToggle(self, value):
    self.showInfoText = value
    
  def onFromAllToggle(self, value):
    self.showFromAll = value
    
  def handleStaticCollisionEvent(self, vehicle, energy, point, normal, miscFlags, damage, destrEffectIdx, destrMaxHealth):
    
    if not self.showStaticCollisionEvents: return
    
    if not self.showFromAll:
      isMy = vehicle == BigWorld.player().vehicle
      if not isMy: return
    
    label = ''
    
    if self.showInfoText:
      label += 'Energy: {:.2f}\n'.format(energy)
      label += 'Damage: {:.2f}\n'.format(damage)
      label += 'Misc flags: {}\n'.format(format(miscFlags, '04b'))
    
    gizmos.createLine(p1=point, p2=point - normal, color=NiceColors.GREEN, timeout=10.0, end2=LineEnd.ARROW)
    gizmos.createMarker(position=point, color=NiceColors.GREEN, size=5, timeout=10.0, text=label)
    
