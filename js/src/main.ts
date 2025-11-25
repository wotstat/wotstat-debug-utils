/// <reference types="wot-gameface-types" />
/// <reference types="wot-gameface-types/types/gameface-libs.d.ts" />


import { LinesDrawer, type BoxData, type PolyLineData, type SimpleLineData } from './drawers/linesDrawer/LinesDrawer'
import { MarkerDrawer, type MarkerData } from './drawers/markersDrawer/MarkersDrawer'
import { FloatingPanel } from './ui/floatingPanel/FloatingPanel'
import { PanelController } from './ui/panels/panelController/PanelController'
import { StatisticsPanel } from './ui/panels/Statistics'
import { ReactiveModel } from './utils/ReactiveModel'
import type { ModelValue } from './utils/types'

console.warn('WotStat Debug Utils Mod - main.ts loaded')

type Model = {
  foo: string
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
const statisticsPanel = new StatisticsPanel()
panelController.addPanel(statisticsPanel)

const canvas = document.createElement('canvas')
root.appendChild(canvas)
const ctx = canvas.getContext('2d') as CanvasRenderingContext2D

let screenWidth = 0
let screenHeight = 0
let screenScale = 1

function updateLoop() {
  requestAnimationFrame(() => updateLoop())

  const startTime = performance.now()

  const model = window.model as Model | undefined
  if (!model) return

  const t = model.boxes.map(box => {
    const points = [box.value.p0, box.value.p1, box.value.p2, box.value.p3, box.value.p4, box.value.p5, box.value.p6, box.value.p7]
    return points.map((point, i) => ({ posx: point.posx, posy: point.posy, scale: 0, isVisible: point.isVisible, size: 5, color: '#FF00FF', text: `${i}` }))
  })

  const renderMarkerTimeStart = performance.now()
  markerDrawer.draw([
    ...model.markers.map(m => m.value),
    ...t.flat()
  ])
  const renderMarkerTimeMs = performance.now() - renderMarkerTimeStart

  const prepareStartTime = performance.now()
  linesDrawer.prepareSimpleLine(model.lines.map(l => l.value))
  linesDrawer.preparePolyLine(model.polyLines.map(p => p.value))
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
    markersCount: model.markers.length + t.length * 8,
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
