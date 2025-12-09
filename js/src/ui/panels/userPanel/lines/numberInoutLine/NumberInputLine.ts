import { BaseLine, type NumberInputLineModel } from '..'
import type { BasePanel } from '../../../panelController/PanelController'
import './style.scss'

export class NumberInputLine extends BaseLine {
  type = 'number-input' as const

  private readonly nameElement: HTMLElement
  private readonly inputElement: HTMLInputElement
  private label: string = ''
  private value: number = 0
  private model: NumberInputLineModel | null = null

  constructor(protected readonly userPanel: BasePanel) {
    super()

    const container = this.userPanel.createLineContainer()
    container.classList.add('user-panel-number-input-line-container')

    this.nameElement = document.createElement('div')
    this.nameElement.classList.add('user-panel-number-input-line-label')
    container.appendChild(this.nameElement)

    const stepper = document.createElement('div')
    stepper.classList.add('user-panel-number-input-line-stepper')
    container.appendChild(stepper)

    const plus = document.createElement('div')
    plus.classList.add('user-panel-number-input-line-stepper-plus')
    const plusIcon = document.createElement('div')
    plusIcon.textContent = '+'
    plus.appendChild(plusIcon)

    const minus = document.createElement('div')
    minus.classList.add('user-panel-number-input-line-stepper-minus')
    const minusIcon = document.createElement('div')
    minusIcon.textContent = '-'
    minus.appendChild(minusIcon)

    this.inputElement = document.createElement('input')
    this.inputElement.classList.add('user-panel-number-input-line-value')
    this.inputElement.type = 'number'
    this.inputElement.value = String(this.value)

    stepper.addEventListener('mousedown', e => e.stopPropagation())

    stepper.appendChild(minus)
    stepper.appendChild(this.inputElement)
    stepper.appendChild(plus)

    this.inputElement.addEventListener('input', () => {
      const numericValue = Number(this.inputElement.value)

      if (!isNaN(numericValue)) {
        this.value = numericValue
        this.model?.onInputChange({ value: numericValue })
      } else {
        this.updateInputValue()
      }
    })

    this.inputElement.addEventListener('blur', () => this.updateInputValue())

    plus.addEventListener('click', e => {
      this.value += e.shiftKey ? 10 : 1
      this.updateInputValue(true)
    })

    minus.addEventListener('click', e => {
      this.value -= e.shiftKey ? 10 : 1
      this.updateInputValue(true)
    })

    stepper.addEventListener('wheel', e => {
      e.preventDefault()
      const delta = Math.sign(e.deltaY)
      const step = e.shiftKey ? 10 : 1
      this.value += delta * step
      this.updateInputValue(true)
    })
  }

  private updateInputValue(send: boolean = false) {
    if (send) this.model?.onInputChange({ value: this.value })
    this.inputElement.value = String(this.value)
  }

  update(model: NumberInputLineModel): void {
    const newLabel = model.label
    const newValue = model.value
    this.model = model

    if (this.label !== newLabel) {
      this.label = newLabel
      this.nameElement.textContent = this.label
    }

    if (this.value !== newValue) {
      this.value = newValue
      this.inputElement.value = String(this.value)
    }
  }
}