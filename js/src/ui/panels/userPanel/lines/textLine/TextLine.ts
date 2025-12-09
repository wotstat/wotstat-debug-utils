import { BaseLine, type TextLineModel } from '..'
import type { BasePanel } from '../../../panelController/PanelController'
import './style.scss'

export class TextLine extends BaseLine {
  type = 'text' as const

  private readonly textElement: HTMLElement
  private text: string = ''

  constructor(protected readonly userPanel: BasePanel) {
    super()

    const container = this.userPanel.createLineContainer()
    container.classList.add('user-panel-text-line-container')

    this.textElement = document.createElement('div')
    this.textElement.classList.add('user-panel-text-line')
    container.appendChild(this.textElement)
  }

  update(model: TextLineModel): void {
    const newText = model.text

    if (this.text == newText) return
    this.text = newText
    this.textElement.textContent = this.text
  }
}