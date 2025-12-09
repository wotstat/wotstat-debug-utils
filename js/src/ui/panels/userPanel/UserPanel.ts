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
const lineFactory: { [K in LineType]?: (panel: BasePanel) => BaseLine } = {
  'text': panel => new TextLine(panel),
  'button': panel => new ButtonLine(panel),
  'separator': panel => new SeparatorLine(panel),
  'value': panel => new ValueLine(panel),
  'checkbox': panel => new CheckboxLine(panel),
  'text-input': panel => new TextInputLine(panel),
  'number-input': panel => new NumberInputLine(panel),
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