import { BaseLine, type HeaderLineModel } from '..'
import type { BasePanel } from '../../../panelController/PanelController'

export class HeaderLine extends BaseLine {
  type = 'header' as const

  private readonly header: HTMLElement

  constructor(protected readonly userPanel: BasePanel) {
    super()
    this.header = this.userPanel.createHeader('')
  }

  update(model: HeaderLineModel): void {
    this.header.textContent = model.text
  }
}