

export class Marker {

  private root: HTMLElement
  private circle: HTMLElement
  private text: HTMLElement

  private display: boolean = true
  private textContent: string = ''
  private color: string = ''
  private size: number = 1

  constructor(private readonly container: HTMLElement) {
    this.root = document.createElement('div')
    this.root.classList.add('marker')
    this.container.appendChild(this.root)

    this.circle = document.createElement('div')
    this.circle.classList.add('circle')
    this.root.appendChild(this.circle)

    this.text = document.createElement('div')
    this.text.classList.add('text')
    this.root.appendChild(this.text)
  }

  dispose() {
    this.container.removeChild(this.root)
  }

  setup(data: { x: number, y: number, text: string, color: string, size: number, display: boolean }) {
    if (this.display !== data.display) {
      this.display = data.display
      this.root.style.display = this.display ? 'block' : 'none'
    }

    if (!this.display) return

    this.root.style.transform = `translateX(${data.x}rem) translateY(${data.y}rem)`

    if (this.textContent !== data.text) {
      this.textContent = data.text
      this.text.innerHTML = data.text
    }

    if (this.color !== data.color) {
      this.color = data.color
      this.circle.style.backgroundColor = data.color
    }

    if (this.size !== data.size) {
      this.size = data.size
      this.circle.style.width = `${data.size}rem`
      this.circle.style.height = `${data.size}rem`
      this.text.style.left = `${data.size / 2}rem`
      this.text.style.top = `${-data.size}rem`
    }
  }
}