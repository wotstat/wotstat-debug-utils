import type { ModelValue } from '../../../utils/types'
import { BasePanel } from '../panelController/PanelController'
import { type BaseLine, type LineModel } from './lines'
import { ButtonLine } from './lines/buttonLine/ButtonLine'
import { CheckboxLine } from './lines/checkboxLine/CheckboxLine'
import { NumberInputLine } from './lines/numberInoutLine/NumberInputLine'
import { SeparatorLine } from './lines/separatorLine/Separator'
import { TextInputLine } from './lines/textInoutLine/TextInputLine'
import { TextLine } from './lines/textLine/TextLine'
import { ValueLine } from './lines/valueLine/ValueLine'


export type PanelModel = {
  name: string
  lines: Array<ModelValue<LineModel>>
}

type LineType = LineModel['type']
const lineFactory: { [K in LineType]?: (userPanel: UserPanel) => BaseLine } = {
  'text': userPanel => new TextLine(userPanel),
  'button': userPanel => new ButtonLine(userPanel),
  'separator': userPanel => new SeparatorLine(userPanel),
  'value': userPanel => new ValueLine(userPanel),
  'checkbox': userPanel => new CheckboxLine(userPanel),
  'text-input': userPanel => new TextInputLine(userPanel),
  'number-input': userPanel => new NumberInputLine(userPanel),
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

        const line: BaseLine = lineFactory[type]!(this)
        this.lines.set(model.lines[i].id, line)
        line.update(lineModel)

      } else {
        const line = this.lines.get(model.lines[i].id)!
        line.update(lineModel)
      }
    }
  }
}