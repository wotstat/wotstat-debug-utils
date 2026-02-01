from AvatarInputHandler import AvatarInputHandler
from gui.debugUtils import ui
from account_helpers.settings_core.options import MouseSetting
import BigWorld, game
from aih_constants import CTRL_MODE_NAME
from Event import SafeEvent
from PlayerEvents import g_playerEvents

from .FreeCamera import WotstatFreeCameraController, WotstatFreeCameraHangarController
import typing
from helpers import isPlayerAvatar

if typing.TYPE_CHECKING:
    from typing import Callable, Set

onSetCameraSettings = SafeEvent()
keyListeners = set() # type: Set[Callable[[BigWorld.KeyEvent], bool]]
mouseListeners = set() # type: Set[Callable[[BigWorld.MouseEvent], bool]]

class FreeCameraUtils(object):
  
  def __init__(self):
    global onSetCameraSettings
    
    self.panel = ui.createPanel('Free Camera')
    self.enabledCheckbox = self.panel.addCheckboxLine('Enable', False, self.onEnableChanged)
    self.panel.addHeaderLine('CONTROLS')
    self.panel.addTextLine('WASD/Space/Shift – Move/Up/Down')
    self.panel.addTextLine('Z – zoom, 1-9 – set speed')

    onSetCameraSettings += self.onSetCameraSettings
    self.gameCameraController = WotstatFreeCameraController()
    self.hangarCameraController = WotstatFreeCameraHangarController()

    g_playerEvents.onAvatarBecomeNonPlayer += self.onAvatarBecomeNonPlayer
    self.enabled = False
    self.activeController = None

  def onSetCameraSettings(self, setting, value):
    self.gameCameraController.camera.setUserConfigValue(setting, value)
    self.hangarCameraController.camera.setUserConfigValue(setting, value)
    
  def onEnableChanged(self, isEnabled):
    self.enabled = isEnabled

    if isPlayerAvatar(): self.enableGameCamera(isEnabled)
    else: self.enableHangarCamera(isEnabled)

  def handleKeyEvent(self, event):
    # type: (BigWorld.KeyEvent) -> bool
    if self.enabled and self.activeController is self.hangarCameraController:
      if self.hangarCameraController.handleKeyEvent(event):
        return True
    return False
  
  def handleMouseEvent(self, event):
    # type: (BigWorld.MouseEvent) -> bool
    if self.enabled and self.activeController is self.hangarCameraController:
      if self.hangarCameraController.handleMouseEvent(event):
        return True
    return False

  def enableGameCamera(self, enable):
    player = BigWorld.player()
    if not hasattr(player, 'inputHandler'): return

    inputHandler = BigWorld.player().inputHandler # type: AvatarInputHandler

    if not inputHandler:
      return

    if enable:
      self.oldGameCameraVideoController = inputHandler._AvatarInputHandler__ctrls[CTRL_MODE_NAME.VIDEO]
      inputHandler._AvatarInputHandler__ctrls[CTRL_MODE_NAME.VIDEO] = self.gameCameraController
      inputHandler.onControlModeChanged(CTRL_MODE_NAME.VIDEO)
      self.activeController = self.gameCameraController
    else:
      inputHandler._AvatarInputHandler__ctrls[CTRL_MODE_NAME.VIDEO] = self.oldGameCameraVideoController
      inputHandler.onControlModeChanged(CTRL_MODE_NAME.ARCADE)
      self.activeController = None

  def enableHangarCamera(self, enable):
    self.enabledCheckbox.isChecked = enable
    
    if enable: 
      keyListeners.add(self.handleKeyEvent)
      mouseListeners.add(self.handleMouseEvent)
      self.activeController = self.hangarCameraController
    else: 
      keyListeners.discard(self.handleKeyEvent)
      mouseListeners.discard(self.handleMouseEvent)
      self.activeController = None

    self.hangarCameraController.setFreeCameraEnabled(enable)

    if enable: self.cameraListener()

  def cameraListener(self):
    if not self.enabled or self.activeController is not self.hangarCameraController:
      return
    
    if BigWorld.camera() is not self.hangarCameraController.camera.camera:
      self.enableHangarCamera(False)
      return

    BigWorld.callback(0, self.cameraListener)

  def onAvatarBecomeNonPlayer(self):
    if self.enabled: 
      self.enableGameCamera(False)
      self.enabledCheckbox.isChecked = False

oldSetCameraSettings = MouseSetting._set
def setCameraSettings(obj, value):
  if obj.mode == CTRL_MODE_NAME.ARCADE:
    onSetCameraSettings(obj.setting, value)
  return oldSetCameraSettings(obj, value)
MouseSetting._set = setCameraSettings

oldHandleKey = game.handleKeyEvent
def handleKeyEvent(event):
  for listener in keyListeners:
    if listener(event):
      return True
  return oldHandleKey(event)
game.handleKeyEvent = handleKeyEvent

oldHandleMouse = game.handleMouseEvent
def handleMouseEvent(event):
  for listener in mouseListeners:
    if listener(event):
      return True
  return oldHandleMouse(event)
game.handleMouseEvent = handleMouseEvent
