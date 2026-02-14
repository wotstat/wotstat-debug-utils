/// <reference types="wot-gameface-types" />
/// <reference types="wot-gameface-types/types/gameface-libs.d.ts" />


import { LinesDrawer, type BoxData, type PolyLineData, type SimpleLineData } from './drawers/linesDrawer/LinesDrawer'
import { MarkerDrawer, type MarkerData } from './drawers/markersDrawer/MarkersDrawer'
import { FloatingPanel } from './ui/floatingPanel/FloatingPanel'
import { PanelController } from './ui/panels/panelController/PanelController'
import { UserPanelsController } from './ui/panels/panelController/UserPanelsController'
import { StatisticsPanel } from './ui/panels/StatisticsPanel'
import { ReactiveModel } from './utils/ReactiveModel'
import type { ModelValue } from './utils/types'
import './utils/ResizeObserverPolyfill'

console.warn('WotStat Debug Utils Mod - main.ts loaded')

type Model = {
  game: 'wot' | 'mt'
  visible: boolean
  markers: Array<ModelValue<MarkerData>>
  lines: Array<ModelValue<SimpleLineData>>
  polyLines: Array<ModelValue<PolyLineData>>
  boxes: Array<ModelValue<BoxData>>
}


const root = document.getElementById('root') as HTMLElement
const markerDrawer = new MarkerDrawer(root)
const linesDrawer = new LinesDrawer()
const panel = new FloatingPanel(root)
const panelController = new PanelController(panel.panel)
const statisticsPanel = new StatisticsPanel({
  onShowDebugPositionsChange: (value) => displayDebugPositions = value,
  onDebugColorizedLinesChange: (value) => debugColorizedLines = value
})
panelController.addPanel(statisticsPanel)

const model = new ReactiveModel<Model>()
model.subscribe('model')
model.watch(m => {
  panel.setVisible(m?.visible ?? false)
  if (m) root.classList.add(`game-${m.game}`)
}, { immediate: true })

const userPanelsController = new UserPanelsController(panelController)

const canvas = document.createElement('canvas')
root.appendChild(canvas)
const ctx = canvas.getContext('2d') as CanvasRenderingContext2D

let screenWidth = 0
let screenHeight = 0
let screenScale = 1
let displayDebugPositions = false
let debugColorizedLines = false

function getAllPointsFromModel(model: Model): Array<MarkerData> {
  const additionalPoints: Array<MarkerData> = []

  for (let i = 0; i < model.boxes.length; i++) {
    const box = model.boxes[i]
    const points = [box.value.p0, box.value.p1, box.value.p2, box.value.p3, box.value.p4, box.value.p5, box.value.p6, box.value.p7]
    additionalPoints.push(...points.map((pt, idx) => ({
      ...pt, scale: 0, size: 4, color: box.value.color, text: `${idx}`
    })))
  }

  for (let i = 0; i < model.polyLines.length; i++) {
    const polyline = model.polyLines[i]
    additionalPoints.push(...polyline.value.points.map((pt, idx) => ({
      ...pt.value, scale: 0, size: 4, color: polyline.value.color, text: `${idx}`
    })))
  }

  for (let i = 0; i < model.lines.length; i++) {
    const line = model.lines[i]
    additionalPoints.push(...[line.value.p1, line.value.p2].map((pt, idx) => ({
      ...pt, scale: 0, size: 4, color: line.value.color, text: `${idx}`
    })))
  }

  return additionalPoints
}

const colors = [
  '#ff0000', '#00ff00', '#0000ff',
  '#ffff00', '#00ffff', '#ff00ff',
  '#880000', '#008800', '#000088',
]

function updateLoop() {
  requestAnimationFrame(() => updateLoop())

  const startTime = performance.now()

  const model = window.model as Model | undefined
  if (!model) return

  const additionalPoints: Array<MarkerData> = displayDebugPositions ? getAllPointsFromModel(model) : []

  const renderMarkerTimeStart = performance.now()
  markerDrawer.draw([
    ...model.markers.map(m => m.value),
    ...additionalPoints
  ])
  const renderMarkerTimeMs = performance.now() - renderMarkerTimeStart


  let colorIndex = 0

  const prepareStartTime = performance.now()
  if (!debugColorizedLines) {
    linesDrawer.prepareSimpleLine(model.lines.map(l => l.value))
    linesDrawer.preparePolyLine(model.polyLines.map(p => p.value))
  } else {
    linesDrawer.prepareSimpleLine(model.lines.map(l => ({ ...l.value, color: colors[colorIndex++ % colors.length] })))
    linesDrawer.preparePolyLine(model.polyLines.map(p => ({ ...p.value, color: colors[colorIndex++ % colors.length] })))
  }

  linesDrawer.prepareBoxes(model.boxes.map(b => b.value))
  const prepareLinesTimeMs = performance.now() - prepareStartTime

  const renderStartTime = performance.now()
  ctx.clearRect(0, 0, screenWidth, screenHeight)
  ctx.save()
  ctx.scale(screenScale, screenScale)

  linesDrawer.draw(ctx)

  ctx.restore()
  const renderLinesTimeMs = performance.now() - renderStartTime
  const totalTimeMs = performance.now() - startTime

  statisticsPanel.updateStatistics({
    totalTimeMs,
    renderMarkerTimeMs,
    renderLinesTimeMs,
    prepareLinesTimeMs,
    markersCount: model.markers.length + additionalPoints.length,
    simpleLinesCount: model.lines.length,
    polyLinesCount: model.polyLines.length,
    boxesCount: model.boxes.length
  })
}

function updateSize() {
  const { height, width } = viewEnv.getClientSizePx()
  screenWidth = width || 100
  screenHeight = height || 100
  screenScale = viewEnv.getScale() || 1

  viewEnv.resizeViewPx(screenWidth, screenHeight)

  canvas.width = screenWidth
  canvas.height = screenHeight
  canvas.style.width = `${screenWidth}px`
  canvas.style.height = `${screenHeight}px`

  panel.onScreenResize(screenHeight, screenWidth)
}

const doubleFrameDelay = (callback: () => void) => requestAnimationFrame(() => requestAnimationFrame(() => callback()))
engine.whenReady.then(() => {
  doubleFrameDelay(() => updateSize())
  engine.on('clientResized', () => doubleFrameDelay(() => updateSize()))
  engine.on('self.onScaleUpdated', () => doubleFrameDelay(() => updateSize()))
  updateLoop()
})
