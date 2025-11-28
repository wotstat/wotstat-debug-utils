
export type TextLineModel = {
  type: 'text',
  text: string
}

export type ButtonLineModel = {
  type: 'button',
  label: string,
  buttonText: string
  onButtonClick: () => void
}

export type InputLineModel = {
  type: 'input',
  label: string,
  value: string,
  inputType: 'numeric' | 'text',
  onInputChange: (args: { value: string }) => void
}

export type CheckboxLineModel = {
  type: 'checkbox',
  label: string,
  isChecked: boolean,
  checkboxType: 'default' | 'switch',
  onCheckboxToggle: (args: { value: boolean }) => void
}

export type ValueLineModel = {
  type: 'value',
  label: string,
  value: string
}

export type SeparatorLineModel = {
  type: 'separator'
}

export type LineModel = TextLineModel |
  ButtonLineModel |
  InputLineModel |
  CheckboxLineModel |
  ValueLineModel |
  SeparatorLineModel

export abstract class BaseLine {
  abstract readonly type: LineModel['type']
  abstract update(model: LineModel): void
}
