import BigWorld, Settings
import Math, math
import Keys
import time
import GUI
from AvatarInputHandler.control_modes import IControlMode
from gui.Scaleform.daapi.view.lobby.LobbyMenu import LobbyMenu
from helpers import dependency
import math_utils
from AvatarInputHandler.cameras import ICamera
from helpers.CallbackDelayer import CallbackDelayer, TimeDeltaMeter
from AvatarInputHandler.cameras import readFloat, readBool, FovExtended
from AvatarInputHandler.DynamicCameras.arcade_camera_helper import EScrollDir
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared.utils import IHangarSpace
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates
from Event import SafeEvent
import ResMgr
from helpers import isPlayerAccount

@staticmethod
def clampFov(fov): return math_utils.clamp(0.0001, 3.12, fov)
FovExtended.clampFov = clampFov

lobbyMenuOnPopulate = SafeEvent()
lobbyMenuOnDispose = SafeEvent()

CAMERA_CONTROLS_KEYS = set([
  Keys.KEY_W,
  Keys.KEY_S,
  Keys.KEY_A,
  Keys.KEY_D,
  Keys.KEY_Z,
  Keys.KEY_LSHIFT,
  Keys.KEY_RSHIFT,
  Keys.KEY_SPACE
])

SPEED_KEYS = [Keys.KEY_1, Keys.KEY_2, Keys.KEY_3, Keys.KEY_4, Keys.KEY_5, Keys.KEY_6, Keys.KEY_7, Keys.KEY_8, Keys.KEY_9]
SPEED_PRESETS = [1, 2, 5, 10, 15, 20, 30, 50, 75, 100]

EPSILON = 0.0001
MAX_ZOOM_LEVEL = 2000.0
MIN_ZOOM_LEVEL = 1.0
ZOOM_LEVEL_RAMP_TIME = 0.1


class WotstatFreeCamera(ICamera, CallbackDelayer, TimeDeltaMeter):

  def __init__(self):
    super(WotstatFreeCamera, self).__init__()
    CallbackDelayer.__init__(self)
    TimeDeltaMeter.__init__(self, time.clock)

    self.pressedKeys = set() # type: set[int]

    self.camera = BigWorld.FreeCamera() # type: BigWorld.FreeCamera
    self.camera.invViewProvider = Math.MatrixProduct() # type: Math.MatrixProduct

    cameraSec = ResMgr.openSection('gui/avatar_input_handler.xml/arcadeMode/camera/')
    self.xmlSensitivity = readFloat(cameraSec, 'sensitivity', 0.0, 10.0, 1.0)

    userSec = Settings.g_instance.userPrefs[Settings.KEY_CONTROL_MODE]

    self.config = {
      'horzInvert': readBool(userSec, 'arcadeMode/camera/horzInvert', False),
      'vertInvert': readBool(userSec, 'arcadeMode/camera/vertInvert', False),
      'sensitivity': readFloat(userSec, 'arcadeMode/camera/sensitivity', 0.0, 10.0, 1.0)
    }

    self.position = Math.Vector3(0, 0, 0)
    self.ypr = Math.Vector3(0, 0, 0)
    self.zoomLevel = 1.0
    self.lastZoomLevel = 1.0
    self.isInZoomMode = False
    self.maxSpeed = SPEED_PRESETS[4] # Default speed 15

  def enable(self, **args):
    matrix = BigWorld.camera().invViewMatrix
    self.camera.invViewProvider.a = Math.Matrix(matrix)
    self.camera.invViewProvider.b = math_utils.createIdentityMatrix()
    self.camera.speedTreeTarget = self.camera.invViewMatrix

    worldMat = Math.Matrix(matrix)
    self.ypr = Math.Vector3(worldMat.yaw, worldMat.pitch, 0)
    self.position = worldMat.translation
    self.horizontalVelocity = Math.Vector3()
    self.verticalVelocity = Math.Vector3()
    self.yprVelocity = Math.Vector3()
    
    self.delayCallback(0.0, self.update)
    BigWorld.camera(self.camera)
    self.measureDeltaTime()
  
  def disable(self):
    self.stopCallback(self.update)

  def destroy(self):
    CallbackDelayer.destroy(self)

  def setUserConfigValue(self, name, value):
    if name in self.config:
      self.config[name] = value

  def handleKeyEvent(self, isDown, key, mods, event=None):
    if key in CAMERA_CONTROLS_KEYS:
      if isDown: self.pressedKeys.add(key)
      else: self.pressedKeys.discard(key)
      return True
    
    speedIndex = SPEED_KEYS.index(key) if key in SPEED_KEYS else -1
    if key in SPEED_KEYS:
      self.maxSpeed = SPEED_PRESETS[speedIndex]
    return False
  
  def handleMouseEvent(self, dx, dy, dz):
    sensitivity = self.xmlSensitivity * self.config['sensitivity'] / self.zoomLevel
    if self.config['horzInvert']: dx = -dx
    if self.config['vertInvert']: dy = -dy

    if self.isInZoomMode:
      eScrollDirection = EScrollDir.convertDZ(dz)
      if eScrollDirection:
        self.zoomLevel *= 1.1 if eScrollDirection == EScrollDir.IN else 0.9
        self.zoomLevel = max(MIN_ZOOM_LEVEL, min(MAX_ZOOM_LEVEL, self.zoomLevel))
   
    self.ypr.x += dx * sensitivity 
    self.ypr.y += dy * sensitivity 
    GUI.mcursor().position = Math.Vector2(0, 0)
    return True

  def updateCameraMatrix(self):
    self.camera.invViewProvider.a = math_utils.createRTMatrix(self.ypr, self.position)

  def update(self):
    delta = self.measureDeltaTime()
    self.horizontalModeMove(delta)
    self.ypr = self.clampYPR(self.ypr)
    self.handleZoom()

    self.updateCameraMatrix()
    self.updateZoom()

    return 0.0
  
  def handleZoom(self):
    if Keys.KEY_Z in self.pressedKeys and not self.isInZoomMode:
      self.isInZoomMode = True
      self.zoomLevel = 3.0
    elif Keys.KEY_Z not in self.pressedKeys and self.isInZoomMode:
      self.isInZoomMode = False
      self.zoomLevel = 1.0

  def getMaxSpeed(self):
    maxVerticalSpeed = min(max(self.maxSpeed / 2, 5), self.maxSpeed)
    return self.maxSpeed, maxVerticalSpeed
  
  def updateZoom(self):
    if abs(self.zoomLevel - self.lastZoomLevel) > EPSILON:
      self.lastZoomLevel = self.zoomLevel
      FovExtended.instance().setFovByMultiplier(1.0 / self.zoomLevel, rampTime=ZOOM_LEVEL_RAMP_TIME)
  
  def horizontalModeMove(self, dt):
    deltaHorizontalVelocity, deltaVerticalVelocity = self.getHorizontalVelocityDelta(dt)
    maxSpeed, maxVerticalSpeed = self.getMaxSpeed()
    self.horizontalVelocity = self.clampVelocity(self.dampVelocity(self.horizontalVelocity, deltaHorizontalVelocity, dt, 0.985), maxSpeed)
    self.verticalVelocity = self.clampVelocity(self.dampVelocity(self.verticalVelocity, deltaVerticalVelocity, dt, 0.985), maxVerticalSpeed)

    self.position += self.horizontalVelocity * dt + self.verticalVelocity * dt

  def getHorizontalVelocityDelta(self, dt):
    m = math_utils.createRotationMatrix(self.ypr)

    forward = m.applyVector(Math.Vector3(0, 0, 1))
    forward.y = 0
    forward.normalise()

    right = m.applyVector(Math.Vector3(1, 0, 0))
    right.y = 0
    right.normalise()

    deltaHorizontalVelocity = Math.Vector3()
    deltaVerticalVelocity = Math.Vector3()

    maxSpeed, maxVerticalSpeed = self.getMaxSpeed()
    acceleration = maxSpeed * 5

    if Keys.KEY_W in self.pressedKeys:
      deltaHorizontalVelocity += forward * dt * acceleration
    if Keys.KEY_S in self.pressedKeys:
      deltaHorizontalVelocity -= forward * dt * acceleration

    if Keys.KEY_A in self.pressedKeys:
      deltaHorizontalVelocity -= right * dt * acceleration
    if Keys.KEY_D in self.pressedKeys:
      deltaHorizontalVelocity += right * dt * acceleration

    if Keys.KEY_SPACE in self.pressedKeys:
      deltaVerticalVelocity.y += dt * acceleration
    if Keys.KEY_LSHIFT in self.pressedKeys or Keys.KEY_RSHIFT in self.pressedKeys:
      deltaVerticalVelocity.y -= dt * acceleration

    return self.clampVelocity(deltaHorizontalVelocity, maxSpeed), self.clampVelocity(deltaVerticalVelocity, maxVerticalSpeed)

  def clampVelocity(self, velocity, maxLength):
    length = velocity.length
    if length > maxLength:
      velocity.normalise()
      velocity *= maxLength
    return velocity
  
  def dampVelocity(self, velocity, deltaVelocity, dt, dampingPerSecond):

    if velocity.length < EPSILON and deltaVelocity.length < EPSILON:
      return Math.Vector3()

    if deltaVelocity.length < EPSILON:
      damping = dampingPerSecond ** (dt * 1000.0)
      return velocity * damping
    else:
      return velocity + deltaVelocity

  def clampYPR(self, ypr):
    return Math.Vector3(math.fmod(ypr[0], 2 * math.pi), max(-0.9 * math.pi / 2, min(0.9 * math.pi / 2, ypr[1])), math.fmod(ypr[2], 2 * math.pi))

class WotstatFreeCameraController(IControlMode):

  def __init__(self):
    super(WotstatFreeCameraController, self).__init__()
    self.camera = WotstatFreeCamera()

  def enable(self, **args):
    self.camera.enable(**args)

  def disable(self):
    self.camera.disable()
  
  def handleKeyEvent(self, isDown, key, mods, event=None):
    return self.camera.handleKeyEvent(isDown, key, mods, event)
      
  def handleMouseEvent(self, dx, dy, dz):
    return self.camera.handleMouseEvent(dx, dy, dz)

class WotstatFreeCameraHangarController(object):
  appLoader = dependency.descriptor(IAppLoader) # type: IAppLoader
  hangarSpace = dependency.descriptor(IHangarSpace) # type: IHangarSpace

  def __init__(self):
    self.enabled = False
    self.camera = WotstatFreeCamera()
    self.lastCameraName = None
    self.isCursorDisplayed = False
    self.oldCamera = None

  def setFreeCameraEnabled(self, enabled):
    self.enabled = enabled
    if self.enabled: self.__enable()
    else: self.__disable()
    
  def __enable(self):
    global lobbyMenuOnDispose, lobbyMenuOnPopulate

    playerVehicle = self.hangarSpace.space.getVehicleEntity()
    if playerVehicle is not None and playerVehicle.state != CameraMovementStates.ON_OBJECT:
      return

    self.oldCamera = BigWorld.camera()
    self.camera.enable()
    GUI.mcursor().visible = False

    player = BigWorld.player()
    if hasattr(player, 'objectsSelectionEnabled'):
      player.objectsSelectionEnabled(False)
    self.hangarSpace.setSelectionEnabled(False)

    lobbyMenuOnDispose += self.__onLobbyMenuDispose
    lobbyMenuOnPopulate += self.__onLobbyMenuPopulate

  def __disable(self):
    global lobbyMenuOnDispose, lobbyMenuOnPopulate

    lobbyMenuOnDispose -= self.__onLobbyMenuDispose
    lobbyMenuOnPopulate -= self.__onLobbyMenuPopulate

    self.isCursorDisplayed = False

    self.camera.disable()
    GUI.mcursor().visible = True

    if isPlayerAccount():
      BigWorld.player().objectsSelectionEnabled(True)
      BigWorld.camera(self.oldCamera)

    self.oldCamera = None
    if self.hangarSpace is not None:
      self.hangarSpace.setSelectionEnabled(True)

  def __onLobbyMenuPopulate(self):
    if not self.enabled: return
    GUI.mcursor().visible = self.isCursorDisplayed = True

  def __onLobbyMenuDispose(self):
    if not self.enabled: return
    GUI.mcursor().visible = self.isCursorDisplayed = False

  def handleMouseEvent(self, event):
    # type: (BigWorld.MouseEvent) -> None
    if self.enabled and not self.isCursorDisplayed:
      return self.camera.handleMouseEvent(event.dx, event.dy, event.dz)
    return False
  
  def handleKeyEvent(self, event):
    # type: (BigWorld.KeyEvent) -> None
    if self.enabled:
      if event.key == Keys.KEY_LCONTROL:
        GUI.mcursor().visible = self.isCursorDisplayed = event.isKeyDown()
        return True

      return self.camera.handleKeyEvent(event.isKeyDown(), event.key, event.modifiers, event)
    return False


oldPopulate = LobbyMenu._populate
def newPopulate(self):
  oldPopulate(self)
  lobbyMenuOnPopulate()
LobbyMenu._populate = newPopulate

oldDispose = LobbyMenu._dispose
def newDispose(self):
  lobbyMenuOnDispose()
  oldDispose(self)
LobbyMenu._dispose = newDispose