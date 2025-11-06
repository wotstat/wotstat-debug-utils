import { ReactiveModel } from './utils/ReactiveModel'

console.warn('WotStat Debug Utils Mod - main.ts loaded')

type Model = {
  foo: string,
  demoPosition: {
    posx: number, posy: number, scale: number, isVisible: boolean
  },
}
// const model = new ReactiveModel<Model>()

// const marker = document.createElement('div')
// marker.classList.add('wotstat-debug-utils-marker')
// document.body.appendChild(marker)

// model.watch((data) => {
//   // console.warn('Model data changed:', JSON.stringify(data))
//   if (!window.model) return
//   const model = window.model as Model
//   marker.style.top = `${model.demoPosition.posy}px`
//   marker.style.left = `${model.demoPosition.posx}px`
//   // marker.style.transform = `translateX(${model.demoPosition.posx}px) translateY(${model.demoPosition.posy}px) translateX(-50%) translateY(-50%)`
// }, { immediate: true })

// function updateLoop() {
//   requestAnimationFrame(() => updateLoop())
// }

// model.subscribe('model.demoPosition')

// updateLoop()

// function onDataChanged() {
//   if (!window.model) return
//   const model = window.model as Model
//   marker.style.transform = `translateX(${model.demoPosition.posx}px) translateY(${model.demoPosition.posy}px) translateX(-50%) translateY(-50%)`
// }

const marker = document.querySelector('.wotstat-debug-utils-marker') as HTMLElement
const fps = document.querySelector('.fps') as HTMLElement

function updateMarkerPosition() {
  if (!window.model) return
  const model = window.model as Model
  marker.style.transform = `translateX(${model.demoPosition.posx}rem) translateY(${model.demoPosition.posy}rem) translateX(-50%) translateY(-50%)`
}

let lastFpsUpdate = performance.now()
let history: number[] = []
function updateLoop() {
  requestAnimationFrame(() => updateLoop())
  const now = performance.now()
  const delta = now - lastFpsUpdate
  const frames = 1000 / delta
  history.push(frames)
  if (history.length > 10) history.shift()
  const min = Math.min(...history)
  const max = Math.max(...history)
  const avg = history.reduce((a, b) => a + b, 0) / history.length

  fps.textContent = `FPS: ${frames.toFixed(0)} (avg: ${avg.toFixed(0)}, min: ${min.toFixed(0)}, max: ${max.toFixed(0)})`
  lastFpsUpdate = now
}
updateLoop()


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

  engine.on('viewEnv.onDataChanged', updateMarkerPosition)
  viewEnv.addDataChangedCallback('model.demoPosition', 0, false)
})
