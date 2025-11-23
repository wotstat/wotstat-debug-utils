/// <reference types="wot-gameface-types" />
/// <reference types="wot-gameface-types/types/gameface-libs.d.ts" />


import { LinesDrawer, type LineData } from './drawers/linesDrawer/LinesDrawer'
import { MarkerDrawer, type MarkerData } from './drawers/markersDrawer/MarkersDrawer'
import { ReactiveModel } from './utils/ReactiveModel'

console.warn('WotStat Debug Utils Mod - main.ts loaded')

type Model = {
  foo: string
  markers: Array<{
    value: MarkerData
    id: string
  }>
  lines: Array<{
    value: LineData
    id: string
  }>
}


const root = document.getElementById('root') as HTMLElement
const markerDrawer = new MarkerDrawer(root)
const linesDrawer = new LinesDrawer()

const canvas = document.createElement('canvas')
root.appendChild(canvas)
const ctx = canvas.getContext('2d') as CanvasRenderingContext2D

let screenWidth = 0
let screenHeight = 0
let screenScale = 1

function updateLoop() {
  requestAnimationFrame(() => updateLoop())

  const model = window.model as Model | undefined
  if (!model) return

  markerDrawer.draw(model.markers.map(m => m.value))

  ctx.clearRect(0, 0, screenWidth, screenHeight)
  ctx.save()
  ctx.scale(screenScale, screenScale)

  linesDrawer.draw(model.lines.map(l => l.value), ctx)

  ctx.restore()
}


function updateSize() {
  const { height, width } = viewEnv.getClientSizePx()
  screenWidth = width || 100
  screenHeight = height || 100
  screenScale = viewEnv.getScale() || 1

  viewEnv.resizeViewPx(screenWidth, screenHeight)
  requestAnimationFrame(() => viewEnv.setHitAreaPaddingsRem(screenHeight, 0, 0, 0, 15))

  canvas.width = screenWidth
  canvas.height = screenHeight
  canvas.style.width = `${screenWidth}px`
  canvas.style.height = `${screenHeight}px`
}

engine.whenReady.then(() => {
  requestAnimationFrame(() => requestAnimationFrame(() => updateSize()))
  engine.on('clientResized', () => updateSize())
  engine.on('self.onScaleUpdated', () => updateSize())
  updateLoop()
})
