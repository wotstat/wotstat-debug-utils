
export class ReactiveModel<T> {

  private _data: T | null = null
  private callbacks: Set<(data: T | null) => void> = new Set()
  private callbackId = new Set<number>()

  constructor() {
    this.copyModel()
    engine.whenReady.then(() => {
      this.copyModel()
      engine.on('viewEnv.onDataChanged', this.onDataChanged)
    })
  }

  dispose() {
    for (const id of this.callbackId) viewEnv.removeDataChangedCallback(id, 0)
    this.callbackId.clear()
    engine.off('viewEnv.onDataChanged', this.onDataChanged)
    this.callbacks.clear()
  }

  get data(): T | null {
    return this._data
  }

  watch(callback: (data: T | null) => void, options?: { immediate: boolean }): () => void {
    this.callbacks.add(callback)
    if (options?.immediate && this.callbackId.size > 0) callback(this.data)
    return () => this.callbacks.delete(callback)
  }

  subscribe(path: string) {
    this.callbackId.add(viewEnv.addDataChangedCallback(path, 0, true))
  }

  private onDataChanged = () => {
    this.copyModel()
    for (const callback of this.callbacks) callback(this.data)
  }

  private copyModel() {
    this._data = window.model as any as T
  }
}