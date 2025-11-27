import type { ModelValue } from '../../../utils/types'
import { BasePanel } from '../panelController/PanelController'
import { type BaseLine, type LineModel } from './lines'
import { ButtonLine } from './lines/buttonLine/ButtonLine'
import { TextLine } from './lines/textLine/TextLine'


export type PanelModel = {
  name: string
  lines: Array<ModelValue<LineModel>>
}

const lineFactory = {
  'text': (userPanel: UserPanel) => new TextLine(userPanel),
  'button': (userPanel: UserPanel) => new ButtonLine(userPanel)
}

export class UserPanel extends BasePanel {

  private readonly lines = new Map<string, BaseLine>()

  constructor(name: string, public readonly modelId: string) {
    super(name)
  }

  updateModel(model: PanelModel) {
    for (let i = 0; i < model.lines.length; i++) {
      const lineModel = model.lines[i].value
      if (!this.lines.has(model.lines[i].id)) {

        const type = lineModel.type
        if (!(type in lineFactory)) {
          console.warn('UserPanel: Unsupported line model type:', lineModel)
          continue
        }

        const line: BaseLine = lineFactory[type](this)
        this.lines.set(model.lines[i].id, line)
        line.update(lineModel)

      } else {
        const line = this.lines.get(model.lines[i].id)!
        line.update(lineModel)
      }
    }
  }
}