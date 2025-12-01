import { BaseLine, type TextInputLineModel, type TextLineModel, type ValueLineModel } from '..'
import type { UserPanel } from '../../UserPanel'
import './style.scss'

export class TextInputLine extends BaseLine {
  type = 'text-input' as const

  private readonly nameElement: HTMLElement
  private readonly inputElement: HTMLInputElement
  private label: string = ''
  private value: string = ''
  private model: TextInputLineModel | null = null

  constructor(protected readonly userPanel: UserPanel) {
    super()

    const container = this.userPanel.createLineContainer()
    container.classList.add('user-panel-text-input-line-container')

    this.nameElement = document.createElement('div')
    this.nameElement.classList.add('user-panel-text-input-line-label')
    container.appendChild(this.nameElement)

    this.inputElement = document.createElement('input')
    this.inputElement.classList.add('user-panel-text-input-line-value')
    this.inputElement.type = 'text'
    this.inputElement.value = this.value

    this.inputElement.addEventListener('mousedown', e => e.stopPropagation())
    container.appendChild(this.inputElement)

    this.inputElement.addEventListener('input', () => {
      this.value = this.inputElement.value
      this.model?.onInputChange({ value: this.value })
    })
  }

  update(model: TextInputLineModel): void {
    const newLabel = model.label
    const newValue = model.value
    this.model = model

    if (this.label !== newLabel) {
      this.label = newLabel
      this.nameElement.textContent = this.label
    }

    if (this.value !== newValue) {
      this.value = newValue
      this.inputElement.value = this.value
    }
  }
}