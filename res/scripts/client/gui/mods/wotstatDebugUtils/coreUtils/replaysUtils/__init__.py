import BigWorld
from gui.debugUtils import ui
from BattleReplay import g_replayCtrl # type: BattleReplay.BattleReplay

from Event import SafeEvent
from Avatar import PlayerAvatar

import typing
if typing.TYPE_CHECKING:
  from ...ui.models.UiModel import Panel

playbackSpeedModifiers = (0.0, 0.0625, 0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0)
playbackSpeedModifiersStr = ('0', '1/16', '1/8', '1/4', '1/2', '1', '2', '4', '8', '16')

extendedPlaybackSpeedModifiers = (0.0, 1/128.0, 1/64.0, 1/32.0, 1/16.0, 1/8.0, 1/4.0, 1/2.0, 1.0, 2.0, 4.0, 8.0, 16.0)
extendedPlaybackSpeedModifiersStr = ('0', '1/128', '1/64', '1/32', '1/16', '1/8', '1/4', '1/2', '1', '2', '4', '8', '16')

onShowTracerEvent = SafeEvent()
oldShowTracer = PlayerAvatar.showTracer
def showTracer(self, *a, **k):
  onShowTracerEvent(self, *a, **k)
  return oldShowTracer(self, *a, **k)
PlayerAvatar.showTracer = showTracer

class ReplaysUtils(object):
  
  def __init__(self):
    global onShowTracerEvent

    self.pauseOnOwnShot = False
    self.pauseOnEnemyShot = False

    self.panel = ui.createPanel('Replays utils')
    self.panel.addCheckboxLine('Extend slow down', isChecked=True, onToggleCallback=self.onSlowDownToggle)
    self.panel.addCheckboxLine('Pause on OWN shot', onToggleCallback=self.onPauseOnOwnShotToggle)
    self.panel.addCheckboxLine('Pause on ANY shot', onToggleCallback=self.onPauseOnEnemyShotToggle)

    self.onSlowDownToggle(True)
    onShowTracerEvent += self.onShowTracer

  def onPauseOnOwnShotToggle(self, isEnabled):
    self.pauseOnOwnShot = isEnabled

  def onPauseOnEnemyShotToggle(self, isEnabled):
    self.pauseOnEnemyShot = isEnabled

  def onSlowDownToggle(self, isEnabled):
    if not g_replayCtrl:
      return
    
    if isEnabled:
      g_replayCtrl._BattleReplay__playbackSpeedModifiers = extendedPlaybackSpeedModifiers
      g_replayCtrl._BattleReplay__playbackSpeedModifiersStr = extendedPlaybackSpeedModifiersStr
    else:
      g_replayCtrl._BattleReplay__playbackSpeedModifiers = playbackSpeedModifiers
      g_replayCtrl._BattleReplay__playbackSpeedModifiersStr = playbackSpeedModifiersStr

  def onShowTracer(self, obj, attackerID, *args, **kwargs):
    if not g_replayCtrl:
      return
    
    if not g_replayCtrl.isPlaying:
      return
    
    if not self.pauseOnEnemyShot and not self.pauseOnOwnShot:
      return
    
    isOwnShoot = attackerID == BigWorld.player().playerVehicleID
    if (isOwnShoot and self.pauseOnOwnShot) or (not isOwnShoot and self.pauseOnEnemyShot):
      g_replayCtrl.setPlaybackSpeedIdx(0)

  