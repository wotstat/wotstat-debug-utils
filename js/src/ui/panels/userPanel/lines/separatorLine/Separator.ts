import { BaseLine, type SeparatorLineModel } from '..'
import type { BasePanel } from '../../../panelController/PanelController'

export class SeparatorLine extends BaseLine {
  type = 'separator' as const

  constructor(protected readonly userPanel: BasePanel) {
    super()
    this.userPanel.createSeparator()
  }

  update(model: SeparatorLineModel): void {
  }
}