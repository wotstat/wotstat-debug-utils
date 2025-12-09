import { BaseLine, type ButtonLineModel } from '..'
import type { BasePanel } from '../../../panelController/PanelController'
import './style.scss'

export class ButtonLine extends BaseLine {
  type = 'button' as const

  private readonly labelElement: HTMLElement
  private readonly buttonElement: HTMLButtonElement

  private model: ButtonLineModel | null = null
  private label: string = ''
  private buttonText: string = ''

  constructor(protected readonly userPanel: BasePanel) {
    super()

    const container = this.userPanel.createLineContainer()
    container.classList.add('user-panel-button-line-container')

    this.labelElement = document.createElement('div')
    this.labelElement.classList.add('user-panel-button-line-text')
    container.appendChild(this.labelElement)

    this.buttonElement = document.createElement('button')
    this.buttonElement.classList.add('user-panel-button-line-button')
    container.appendChild(this.buttonElement)

    this.buttonElement.addEventListener('mousedown', e => e.stopPropagation())
    this.buttonElement.addEventListener('click', (e) => {
      this.model?.onButtonClick()
    })

    this.setButtonFullWidth(true)
  }

  private setButtonFullWidth(fullWidth: boolean) {
    if (fullWidth) {
      this.labelElement.classList.add('hide')
      this.buttonElement.classList.add('user-panel-full-width-button')
    } else {
      this.labelElement.classList.remove('hide')
      this.buttonElement.classList.remove('user-panel-full-width-button')
    }
  }

  update(model: ButtonLineModel): void {
    const newLabel = model.label
    const newButtonText = model.buttonText
    this.model = model

    if (this.label !== newLabel) {
      this.label = newLabel
      this.labelElement.textContent = this.label
      this.setButtonFullWidth(this.label === '')
    }

    if (this.buttonText !== newButtonText) {
      this.buttonText = newButtonText
      this.buttonElement.textContent = this.buttonText
    }
  }
}
