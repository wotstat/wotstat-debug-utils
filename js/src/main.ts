/// <reference types="wot-gameface-types" />
/// <reference types="wot-gameface-types/types/gameface-libs.d.ts" />


import { MarkerDrawer } from './drawers/markersDrawer/MarkersDrawer'
import { ReactiveModel } from './utils/ReactiveModel'

console.warn('WotStat Debug Utils Mod - main.ts loaded')

type Model = {
  foo: string
  markers: Array<{
    value: {
      posx: number
      posy: number
      scale: number
      isVisible: boolean
      size: number
      color: string
      text: string
    }
    id: string
  }>
}

const root = document.getElementById('root') as HTMLElement
const markerDrawer = new MarkerDrawer(root)

function updateLoop() {
  requestAnimationFrame(() => updateLoop())

  const model = window.model as Model | undefined
  if (!model) return

  markerDrawer.draw(model.markers.map(m => m.value))
}


function updateSize() {
  const { height, width } = viewEnv.getClientSizePx()
  const targetWidth = width || 100
  const targetHeight = height || 100

  viewEnv.resizeViewPx(targetWidth, targetHeight)
  requestAnimationFrame(() => viewEnv.setHitAreaPaddingsRem(targetHeight, 0, 0, 0, 15))
}

engine.whenReady.then(() => {
  requestAnimationFrame(() => requestAnimationFrame(() => updateSize()))
  engine.on('clientResized', () => updateSize())
  engine.on('self.onScaleUpdated', () => updateSize())
  updateLoop()
})
