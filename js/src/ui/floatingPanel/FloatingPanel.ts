import './styles.scss'

const X_POSITION_KEY = 'WOTSTAT_DEBUG_UTILS_FLOATING_PANEL_X_POSITION'
const Y_POSITION_KEY = 'WOTSTAT_DEBUG_UTILS_FLOATING_PANEL_Y_POSITION'

export class FloatingPanel {

  public readonly panel = document.createElement('div')

  private dragDelta = { x: 0, y: 0 }
  private isDragging = false

  constructor(private readonly root: HTMLElement) {
    this.panel.classList.add('floating-panel')
    this.root.appendChild(this.panel)
    this.panel.addEventListener('mousedown', this.onPointerDown)

    const panelHoverHeader = document.createElement('div')
    panelHoverHeader.classList.add('floating-panel-hover-header')
    this.panel.appendChild(panelHoverHeader)
    panelHoverHeader.textContent = 'WotStat Debug Utils'

    const observer = new ResizeObserver((entries) => {
      if (entries.length === 0) return
      const { height, width } = viewEnv.getClientSizePx()
      this.updatePaddings(height, width)
    })
    observer.observe(this.panel)

    const savedX = localStorage.getItem(X_POSITION_KEY)
    const savedY = localStorage.getItem(Y_POSITION_KEY)
    if (savedX && savedY) {
      this.panel.style.left = savedX
      this.panel.style.top = savedY
    }
  }

  private onPointerUp = (e: MouseEvent) => {
    e.stopPropagation()
    this.root.removeEventListener('mousemove', this.onPointerMove)
    this.root.removeEventListener('mouseup', this.onPointerUp)
    this.root.removeEventListener('mouseleave', this.onPointerUp)
    this.isDragging = false

    const { height, width } = viewEnv.getClientSizePx()
    requestAnimationFrame(() => requestAnimationFrame(() => this.updatePaddings(height, width)))

    localStorage.setItem(X_POSITION_KEY, this.panel.style.left)
    localStorage.setItem(Y_POSITION_KEY, this.panel.style.top)
  }

  private onPointerDown = (e: MouseEvent) => {
    e.stopPropagation()
    const rect = this.panel.getBoundingClientRect()
    this.dragDelta = { x: e.clientX - rect.left, y: e.clientY - rect.top }
    this.isDragging = true
    viewEnv.setHitAreaPaddingsRem(0, 0, 0, 0, 15)
    this.root.addEventListener('mousemove', this.onPointerMove)
    this.root.addEventListener('mouseup', this.onPointerUp)
    this.root.addEventListener('mouseleave', this.onPointerUp)
  }

  private onPointerMove = (e: MouseEvent) => {
    e.stopPropagation()
    let targetX = e.clientX - this.dragDelta.x
    let targetY = e.clientY - this.dragDelta.y

    const { height, width } = viewEnv.getClientSizePx()
    const rect = this.panel.getBoundingClientRect()

    const PADDING = 10
    targetX = Math.min(Math.max(targetX, PADDING), width - rect.width - PADDING)
    targetY = Math.min(Math.max(targetY, PADDING), height - rect.height - PADDING)

    this.panel.style.left = `${targetX}px`
    this.panel.style.top = `${targetY}px`
  }

  private updatePaddings(height: number, width: number) {
    const rect = this.panel.getBoundingClientRect()

    const top = rect.top
    const bottom = height - rect.bottom
    const left = rect.left
    const right = width - rect.right

    const remTop = viewEnv.pxToRem(top)
    const remBottom = viewEnv.pxToRem(bottom)
    const remLeft = viewEnv.pxToRem(left)
    const remRight = viewEnv.pxToRem(right)

    viewEnv.setHitAreaPaddingsRem(remTop, remRight, remBottom, remLeft, 15)
  }

  public onScreenResize(height: number, width: number) {
    if (this.isDragging) return
    this.updatePaddings(height, width)
  }

}