import { BaseLine, type ButtonLineModel } from '..'
import type { UserPanel } from '../../UserPanel'
import './style.scss'

export class ButtonLine extends BaseLine {
  type = 'button'

  private readonly textElement: HTMLElement
  private readonly buttonElement: HTMLButtonElement

  private model: ButtonLineModel | null = null
  private text: string = ''
  private buttonLabel: string = ''

  constructor(protected readonly userPanel: UserPanel) {
    super()

    const container = this.userPanel.createLineContainer()
    container.classList.add('user-panel-button-line-container')

    this.textElement = document.createElement('div')
    this.textElement.classList.add('user-panel-button-line-text')
    container.appendChild(this.textElement)

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
      this.textElement.classList.add('hide')
      this.buttonElement.classList.add('user-panel-full-width-button')
    } else {
      this.textElement.classList.remove('hide')
      this.buttonElement.classList.remove('user-panel-full-width-button')
    }
  }

  update(model: ButtonLineModel): void {
    const newText = model.text
    const newButtonLabel = model.buttonLabel
    this.model = model

    if (this.text !== newText) {
      this.text = newText
      this.textElement.textContent = this.text
      this.setButtonFullWidth(this.text === '')
    }

    if (this.buttonLabel !== newButtonLabel) {
      this.buttonLabel = newButtonLabel
      this.buttonElement.textContent = this.buttonLabel
    }
  }
}
