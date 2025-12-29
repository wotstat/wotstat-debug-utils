
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

export type TextInputLineModel = {
  type: 'text-input',
  label: string,
  value: string,
  onInputChange: (args: { value: string }) => void
}

export type NumberInputLineModel = {
  type: 'number-input',
  label: string,
  value: number,
  onInputChange: (args: { value: number }) => void
}

export type CheckboxLineModel = {
  type: 'checkbox',
  label: string,
  isChecked: boolean,
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
  TextInputLineModel |
  NumberInputLineModel |
  CheckboxLineModel |
  ValueLineModel |
  SeparatorLineModel

export abstract class BaseLine {
  abstract readonly type: LineModel['type']
  abstract update(model: LineModel): void

  protected applyLabelPadding(element: HTMLElement) {
    const startWhiteSpace = element.textContent?.match(/^\s*/)?.[0].length ?? 0
    element.style.paddingLeft = `${startWhiteSpace / 4}em`
  }
}
