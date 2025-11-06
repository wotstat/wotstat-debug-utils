export { }

type GFSize = {
  width: number
  height: number
  __Type: 'GFSize'
}

type GFPoint = {
  x: number
  y: number
  __Type: 'GFPoint'
}

type GFSpaceBox = {
  top: number
  right: number
  bottom: number
  left: number
  __Type: 'GFSpaceBox'
}

type GFFontFace = {
  style: string
  weight: 'light' | 'medium' | 'normal' | 'bold' | 'black' | 'semi_bold' | (string & {})
  sdf: 'auto' | (string & {});
  __Type: 'GFFontFace'
}

type GFFontFamily = {
  name: string
  faces: GFFontFace[]
  __Type: 'GFFontFamily'
}

type GFViewEventProxy = unknown

declare global {
  interface ViewEnv {
    addDataChangedCallback: (source: 'model' | (string & {}), resId: number, b: boolean) => number
    addPreloadTexture: (...args: any) => unknown
    enterUniprofRegion: (...args: any) => unknown
    exitUniprofRegion: (...args: any) => unknown
    forceTriggerMouseMove: (...args: any) => unknown
    freezeTextureBeforeResize: (...args: any) => unknown
    getChildTexturePath: (unknown: unknown, width: number, height: number, unknown: number) => unknown
    getClientSizePx: () => GFSize
    getClientSizeRem: () => GFSize
    getExternalPaddingsRem: () => GFSpaceBox
    getExtraSizeRem: () => GFSize
    getFontsConfig: () => Record<string, GFFontFamily>
    getGraphicsQuality: () => number
    getHitAreaPaddingsRem: () => GFSpaceBox
    getMouseGlobalPositionPx: () => GFPoint
    getMouseGlobalPositionRem: () => GFPoint
    getScale: () => number
    getShowingStatus: () => number
    getViewGlobalPositionRem: () => GFPoint
    getViewSizePx: () => GFSize
    getViewSizeRem: () => GFSize
    getWebBrowserTexturePath: (u, e, t, n: number) => unknown
    handleViewEvent: (event: GFViewEventProxy) => void
    isContinuousRepaint: () => boolean
    isEventHandled: () => boolean
    isFocused: () => boolean
    isWindowShownByViewEvent: (u: number) => unknown
    pxToRem: (px: number) => number
    remToPx: (rem: number) => number
    removeDataChangedCallback: (callbackId: number, resId: number) => boolean
    removePreloadTexture: (...args: any) => unknown
    resizeViewPx: (weight: number, height: number) => null
    resizeViewRem: (weight: number, height: number) => null
    setAnimateWindow: (...args: any) => unknown
    setContentReady: (...args: any) => unknown
    setContinuousRepaint: (...args: any) => unknown
    setEventHandled: (...args: any) => unknown
    setExtraSizeRem: (...args: any) => unknown
    setFullscreenModeSupported: (enabled: boolean) => null
    setHitAreaPaddingsRem: (top: number, right: number, bottom: number, left: number, flags: 15) => unknown
    setInputArea: (left: number, top: number, width: number, height: number) => null
    setSkipFramesAllowed: (enabled: boolean) => null
    setTrackMouseOnStage: (enabled: boolean) => null
    setUniprofMarker: (...args: any) => unknown
    showElementAABBs: (enabled: boolean) => null
    showPaintRectangles: (enabled: boolean) => null
  }

  interface Window {
    viewEnv: ViewEnv
  }

  const viewEnv: ViewEnv
}


