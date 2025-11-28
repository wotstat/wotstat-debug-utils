import { BaseLine, type CheckboxLineModel, type TextLineModel } from '..'
import type { UserPanel } from '../../UserPanel'
import './style.scss'
import CheckmkBold from './assets/chekmark-bold.svg?raw'

export class CheckboxLine extends BaseLine {
  type = 'checkbox' as const


  private readonly labelElement: HTMLElement
  private readonly buttonElement: HTMLButtonElement
  private readonly checkmarkElement: HTMLElement

  private model: CheckboxLineModel | null = null
  private label: string = ''
  private checked: boolean = false

  constructor(protected readonly userPanel: UserPanel) {
    super()

    const container = this.userPanel.createLineContainer()
    container.classList.add('user-panel-checkbox-line-container')

    this.labelElement = document.createElement('div')
    this.labelElement.classList.add('user-panel-checkbox-line-label')
    container.appendChild(this.labelElement)

    this.buttonElement = document.createElement('button')
    this.buttonElement.classList.add('user-panel-checkbox-line-checkbox')
    container.appendChild(this.buttonElement)

    this.checkmarkElement = document.createElement('div')
    this.checkmarkElement.innerHTML = CheckmkBold
    this.checkmarkElement.classList.add('user-panel-checkbox-line-checkmark')
    this.buttonElement.appendChild(this.checkmarkElement)

    this.buttonElement.addEventListener('mousedown', e => e.stopPropagation())

    this.buttonElement.addEventListener('click', (e) => this.onClick())
    // this.buttonElement.style.backgroundImage = `url(${CheckmkBold})`

    this.updateCheckedClass()
  }

  private updateCheckedClass() {
    if (this.checked) this.buttonElement.classList.add('checked')
    else this.buttonElement.classList.remove('checked')
  }

  private onClick() {
    this.checked = !this.checked
    this.updateCheckedClass()
    this.model?.onCheckboxToggle({ value: this.checked })
  }

  update(model: CheckboxLineModel): void {

    this.model = model

    const newLabel = model.label
    if (this.label !== newLabel) {
      this.label = newLabel
      this.labelElement.textContent = this.label
    }

    const newChecked = model.isChecked
    if (this.checked !== newChecked) {
      this.checked = newChecked
      this.updateCheckedClass()
    }
  }
}