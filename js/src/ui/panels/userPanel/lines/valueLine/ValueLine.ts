import { BaseLine, type TextLineModel, type ValueLineModel } from '..'
import type { UserPanel } from '../../UserPanel'
import './style.scss'

export class ValueLine extends BaseLine {
  type = 'value' as const

  private readonly nameElement: HTMLElement
  private readonly valueElement: HTMLElement
  private label: string = ''
  private value: string = ''

  constructor(protected readonly userPanel: UserPanel) {
    super()

    const line = this.userPanel.createLine('', '')
    this.nameElement = line.nameElement
    this.valueElement = line.valueContainer
  }

  update(model: ValueLineModel): void {
    const newLabel = model.label
    const newValue = model.value

    if (this.label !== newLabel) {
      this.label = newLabel
      this.nameElement.textContent = this.label
    }

    if (this.value !== newValue) {
      this.value = newValue
      this.valueElement.textContent = this.value
    }
  }
}