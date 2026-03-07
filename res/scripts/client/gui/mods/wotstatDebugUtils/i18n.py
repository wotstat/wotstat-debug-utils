# -*- coding: utf-8 -*-
from helpers import getClientLanguage
from Singleton import Singleton


EN = {
  'section.mainUtils': 'Main utils',
  'mainUtils.raycast.serverTime': 'Server time',
  'mainUtils.raycast.raycast': 'Raycast',
  'mainUtils.raycast.cursorDistance': 'Cursor distance',
  'mainUtils.raycast.raycastLine': 'Raycast line (MMB)',
  'mainUtils.raycast.materialInfo': '  Mat info',

  'mainUtils.physics.physics': 'Physics',
  'mainUtils.physics.staticCollisionEvents': 'Static collision events',
  'mainUtils.physics.staticCollisionInfoText': '  Info text',
  'mainUtils.physics.staticCollisionFromAll': '  From all',

  'mainUtils.bbox.bbox': 'BBox',
  'mainUtils.bbox.showOwn': 'Show OWN bbox',
  'mainUtils.bbox.showAny': 'Show ANY bbox',
  'mainUtils.bbox.backfaceVisibility': 'Backface visibility',

  'section.shootingUtils': 'Shooting utils',
  'shootingUtils.aiming.aiming': 'Aiming',
  'shootingUtils.aiming.serverAimingCircle': 'Server aiming circle',
  'shootingUtils.aiming.clientAimingCircle': 'Client aiming circle',
  'shootingUtils.aiming.trajectory': '  Trajectory',
  'shootingUtils.aiming.continuousTrajectory': 'Continuous trajectory',
  'shootingUtils.aiming.preserveOnShot': 'Preserve on shot',

  'shootingUtils.projectile.projectile': 'Projectile',
  'shootingUtils.projectile.trajectory': 'Trajectory',
  'shootingUtils.projectile.oneTickInterval': '  1Tick interval',
  'shootingUtils.projectile.continuousTrajectory': '  Continuous trajectory',
  'shootingUtils.projectile.shootMarker': '  Shoot marker',
  'shootingUtils.projectile.endMarker': '  End marker',
  'shootingUtils.projectile.bulletMarker': '  Bullet marker',
  'shootingUtils.projectile.compensateTicks': 'Compensate ticks',
  'shootingUtils.projectile.duration': 'Duration',


  'section.spottingUtils': 'Spotting utils',
  'spottingUtils.visibilityCheckpoints': 'Visibility checkpoints',
  'spottingUtils.viewRangePorts': 'View range ports',
  'spottingUtils.showBBox': 'Show BBox',
  'spottingUtils.bboxAlign': '  BBox align',
  'spottingUtils.rays': 'Rays',
  'spottingUtils.ownSpotRays': 'OWN spot rays',
  'spottingUtils.ownMaskRays': 'OWN mask rays',
  'spottingUtils.allSpotRays': 'ALL spot rays',
  'spottingUtils.allMaskRays': 'ALL mask rays',
  'spottingUtils.minDistanceText': 'Min distance text',
  'spottingUtils.nearestOnly': 'Nearest only',
  'spottingUtils.showNonDirect': 'Show non direct',


  'section.replaysUtils': 'Replays utils',
  'replaysUtils.extendSlowDown': 'Extend slow down',
  'replaysUtils.pauseOnOwnShot': 'Pause on OWN shot',
  'replaysUtils.pauseOnEnemyShot': 'Pause on ANY shot',


  'section.freeCameraUtils': 'Free camera utils',
  'freeCamera.enable': 'Enable',
  'freeCamera.allowShooting': 'Allow shooting',
  'freeCamera.controls': 'Controls',
  'freeCamera.controls.info': 'WASD/Space/Shift – Move/Up/Down',
  'freeCamera.controls.info2': 'Z – zoom, 1-9 – set speed',
}

RU = {
  'section.mainUtils': 'Основное',
  'mainUtils.raycast.serverTime': 'Серверное время',
  'mainUtils.raycast.raycast': 'Raycast',
  'mainUtils.raycast.cursorDistance': 'Дистанция до курсора',
  'mainUtils.raycast.raycastLine': 'Создавать линию (СКМ)',
  'mainUtils.raycast.materialInfo': '  Информация поверхности',

  'mainUtils.physics.physics': 'Физика',
  'mainUtils.physics.staticCollisionEvents': 'Столкновения со статикой',
  'mainUtils.physics.staticCollisionInfoText': '  Инфо текст',
  'mainUtils.physics.staticCollisionFromAll': '  Для всех танков',

  'mainUtils.bbox.bbox': 'bbox',
  'mainUtils.bbox.showOwn': 'Для своего танка',
  'mainUtils.bbox.showAny': 'Для всех танков',
  'mainUtils.bbox.backfaceVisibility': 'Сквозная видимость',

  'section.shootingUtils': 'Стрельба',
  'shootingUtils.aiming.aiming': 'Прицеливание',
  'shootingUtils.aiming.serverAimingCircle': 'Серверный маркер',
  'shootingUtils.aiming.clientAimingCircle': 'Клиентский маркер',
  'shootingUtils.aiming.trajectory': '  Траектория',
  'shootingUtils.aiming.continuousTrajectory': 'Продолжать траекторию',
  'shootingUtils.aiming.preserveOnShot': 'Сохранять после выстрела',

  'shootingUtils.projectile.projectile': 'Выстрел',
  'shootingUtils.projectile.trajectory': 'Траектория',
  'shootingUtils.projectile.oneTickInterval': '  Шаг в 1 тик',
  'shootingUtils.projectile.continuousTrajectory': '  Продолжать траекторию',
  'shootingUtils.projectile.shootMarker': '  Маркер выстрела',
  'shootingUtils.projectile.endMarker': '  Маркер попадания',
  'shootingUtils.projectile.bulletMarker': '  Маркер снаряда',
  'shootingUtils.projectile.compensateTicks': 'Сдвиг тиков',
  'shootingUtils.projectile.duration': 'Длительность',

  'section.spottingUtils': 'Засвет',
  'spottingUtils.visibilityCheckpoints': 'Габартиные точки',
  'spottingUtils.viewRangePorts': 'Обзорные точки',
  'spottingUtils.showBBox': 'Отображать BBox',
  'spottingUtils.bboxAlign': '  Привязка центров',
  'spottingUtils.rays': 'Лучи',
  'spottingUtils.ownSpotRays': 'Засвета СВОЕГО танка',
  'spottingUtils.ownMaskRays': 'Маскировки СВОЕГО танка',
  'spottingUtils.allSpotRays': 'Засвета ВСЕХ танков',
  'spottingUtils.allMaskRays': 'Маскировки ВСЕХ танков',
  'spottingUtils.minDistanceText': 'Текст мин. дистанции',
  'spottingUtils.nearestOnly': 'Только кратчайшие лучи',
  'spottingUtils.showNonDirect': 'Отображать непрямые',

  'section.replaysUtils': 'Реплеи',
  'replaysUtils.extendSlowDown': 'Расширенное замедление',
  'replaysUtils.pauseOnOwnShot': 'Пауза на СВОЙ выстрел',
  'replaysUtils.pauseOnEnemyShot': 'Пауза на ЛЮБОЙ выстрел',

  'section.freeCameraUtils': 'Свободная камера',
  'freeCamera.enable': 'Включить',
  'freeCamera.allowShooting': 'Разрешить стрельбу',
  'freeCamera.controls': 'Управление',
  'freeCamera.controls.info': 'WASD/Пробел/Shift – движение/вверх/вниз',
  'freeCamera.controls.info2': 'Z – приближение, 1-9 – скорость',
}


class I18n(Singleton):
  @staticmethod
  def instance():
      return I18n()

  def __init__(self):
    language = getClientLanguage()

    if language == 'ru':
      self.current_localizations = RU
    else:
      self.current_localizations = EN

  def t(self, key):
    if key in self.current_localizations:
      return self.current_localizations[key]
    return key
  
  def has(self, key):
    return key in self.current_localizations
  
  def translate(self, key):
    return self.t(key)
  
def t(key):
  return I18n.instance().t(key)

def prefix(prefix):
  return lambda key: t(prefix + '.' + key)

def has(key):
  return I18n.instance().has(key)
