
export function requestDoubleFrame(callback: () => void) {
  requestAnimationFrame(() => requestAnimationFrame(() => callback()))
}

export function waitDoubleFrame(): Promise<void> {
  return new Promise(resolve => requestDoubleFrame(() => resolve()))
}