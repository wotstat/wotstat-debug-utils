import { BaseLine, type SeparatorLineModel } from '..'
import type { UserPanel } from '../../UserPanel'

export class SeparatorLine extends BaseLine {
  type = 'separator' as const

  constructor(protected readonly userPanel: UserPanel) {
    super()
    this.userPanel.createSeparator()
  }

  update(model: SeparatorLineModel): void {
  }
}