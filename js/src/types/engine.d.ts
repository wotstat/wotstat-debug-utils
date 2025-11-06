export { }

type Event =
  'viewEnv.onDataChanged' |
  'clientResized' |
  'self.onScaleUpdated' |
  'Ready' |
  'subView:destroy' |
  (string & {});

declare global {
  interface Engine {
    whenReady: Promise<void>;
    call: (method: string, ...args) => Promise<any>;
    on: (event: Event, callback: (...args) => void) => void;
    off: (event: Event, callback: (...args) => void) => void;
  }

  interface Window {
    engine: Engine
    model: unknown
  }

  const engine: Engine
  const model: unknown
}