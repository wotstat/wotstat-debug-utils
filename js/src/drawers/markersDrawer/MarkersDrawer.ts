import { Marker } from './Marker'
import './style.scss'


export type MarkerData = {
  posx: number
  posy: number
  scale: number
  isVisible: boolean
  size: number
  color: string
  text: string
}

export class MarkerDrawer {

  private readonly container: HTMLElement
  private readonly markers: Marker[] = []

  constructor(root: HTMLElement) {
    this.container = document.createElement('div')
    this.container.classList.add('markers-drawer-container')
    root.appendChild(this.container)
  }

  draw(data: MarkerData[]) {
    for (let i = 0; i < data.length; i++) {
      const markerData = data[i]
      if (i >= this.markers.length) {
        this.markers.push(new Marker(this.container))
      }
      this.markers[i].setup({
        x: markerData.posx,
        y: markerData.posy,
        text: markerData.text,
        color: markerData.color,
        size: markerData.size,
        display: markerData.isVisible
      })
    }

    for (let i = data.length; i < this.markers.length; i++) {
      this.markers[i].dispose()
    }

    this.markers.length = data.length
  }
}