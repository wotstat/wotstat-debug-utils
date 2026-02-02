import './styles.scss'
import DropDown from './assets/dropdown.svg?raw'

export interface IPanel {
  addToRoot(root: HTMLElement): void
  removeFromRoot(): void
}

export class BasePanel implements IPanel {
  protected readonly panelElement: HTMLElement = document.createElement('div')
  protected readonly headerElement: HTMLElement = document.createElement('div')
  protected readonly contentElement: HTMLElement = document.createElement('div')
  protected readonly headerContentContainer: HTMLElement = document.createElement('div')

  constructor(name: string) {
    this.panelElement.classList.add('panel')
    this.panelElement.classList.add('collapsed')

    this.headerElement.classList.add('panel-header')
    this.panelElement.appendChild(this.headerElement)

    const headerTitle = document.createElement('div')
    headerTitle.classList.add('panel-header-title')
    this.headerElement.appendChild(headerTitle)
    headerTitle.textContent = name

    this.headerElement.appendChild(this.headerContentContainer)
    this.headerContentContainer.classList.add('panel-header-content-container')

    const collapseButton = document.createElement('div')
    collapseButton.classList.add('panel-collapse-button')
    collapseButton.addEventListener('click', () => {
      this.panelElement.classList.toggle('collapsed')
    })
    collapseButton.addEventListener('mousedown', e => e.stopPropagation())
    this.headerElement.appendChild(collapseButton)

    collapseButton.innerHTML = DropDown

    this.contentElement.classList.add('panel-content')
    this.panelElement.appendChild(this.contentElement)
  }

  addToRoot(root: HTMLElement): void {
    root.appendChild(this.panelElement)
  }

  removeFromRoot(): void {
    if (this.panelElement.parentElement) {
      this.panelElement.parentElement.removeChild(this.panelElement)
    }
  }

  createLineContainer(): HTMLElement {
    const line = document.createElement('div')
    line.classList.add('panel-line')
    this.contentElement.appendChild(line)
    return line
  }

  createLine(name: string, value?: string) {
    const line = this.createLineContainer()

    const nameElement = document.createElement('div')
    nameElement.textContent = name
    nameElement.classList.add('panel-line-name')
    line.appendChild(nameElement)

    const valueContainer = document.createElement('div')
    valueContainer.classList.add('panel-line-value')
    line.appendChild(valueContainer)

    if (value !== undefined) {
      valueContainer.textContent = value
    }

    return {
      line,
      nameElement,
      valueContainer
    }
  }

  createSeparator(): void {
    const separator = document.createElement('div')
    separator.classList.add('panel-separator')
    this.contentElement.appendChild(separator)
  }

  createHeader(text: string): HTMLElement {
    const header = document.createElement('div')
    header.classList.add('panel-header-line')
    header.textContent = text

    const isFirstChild = this.contentElement.children.length === 0
    if (isFirstChild) header.classList.add('first-child')
    this.contentElement.appendChild(header)
    return header
  }

  removeLineContainer(line: HTMLElement): void {
    if (line.parentElement === this.contentElement) {
      this.contentElement.removeChild(line)
    }
  }
}

export class PanelController {

  private readonly container: HTMLElement = document.createElement('div')

  constructor(private readonly root: HTMLElement) {
    this.container.classList.add('panel-controller')
    root.appendChild(this.container)
  }

  addPanel(panel: IPanel) {
    panel.addToRoot(this.container)
  }

  removePanel(panel: IPanel) {
    panel.removeFromRoot()
  }

}