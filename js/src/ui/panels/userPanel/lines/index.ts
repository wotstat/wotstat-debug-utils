
export type TextLineModel = {
  type: 'text',
  text: string
}

export type ButtonLineModel = {
  type: 'button',
  text: string,
  buttonLabel: string
  onButtonClick: () => void
}

export type LineModel = TextLineModel | ButtonLineModel

export abstract class BaseLine {
  abstract readonly type: string
  abstract update(model: LineModel): void
}
