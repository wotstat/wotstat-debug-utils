export { }

type SubView = {
  uid: number
  path: string
  model: Object | null
}

declare global {
  interface SubViews {
    ids: number[];
    get: (id: number) => SubView | null;
  }

  interface Window {
    subViews: SubViews
  }

  const engine: SubViews
}