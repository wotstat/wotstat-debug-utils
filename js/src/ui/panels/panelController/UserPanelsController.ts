import { ReactiveModel } from '../../../utils/ReactiveModel'
import type { ModelValue } from '../../../utils/types'
import { UserPanel, type PanelModel } from '../userPanel/UserPanel'
import type { PanelController } from './PanelController'


type Model = {
  ui: {
    panels: Array<ModelValue<PanelModel>>
  }
}

export class UserPanelsController {

  private readonly existingPanels: Map<string, { panel: UserPanel, model: PanelModel }> = new Map()

  constructor(private readonly panelController: PanelController) {
    const model = new ReactiveModel<Model>()
    model.subscribe('model.ui.panels')
    model.watch(this.onModelUpdate.bind(this), { immediate: true })
  }

  private onModelUpdate(model: Model | null): void {
    if (!model) return

    for (let i = 0; i < model.ui.panels.length; i++) {
      const element = model.ui.panels[i]
      if (!this.existingPanels.has(element.id)) {
        const panel = new UserPanel(element.value.name, element.id)
        this.panelController.addPanel(panel)
        this.existingPanels.set(element.id, { panel, model: element.value })
        panel.updateModel(element.value)
      } else {
        const panel = this.existingPanels.get(element.id)!
        panel.panel.updateModel(element.value)
      }

      const targetPanels = new Set<string>(model.ui.panels.map(p => p.id))

      for (const [panelId, panelModel] of this.existingPanels) {
        if (!targetPanels.has(panelId)) {
          this.panelController.removePanel(panelModel.panel)
          this.existingPanels.delete(panelId)
        }
      }
    }

  }
}