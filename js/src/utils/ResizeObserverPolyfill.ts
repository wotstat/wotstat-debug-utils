// Simple ResizeObserver polyfill (partial) in TypeScript
// - Polls sizes via requestAnimationFrame
// - Uses getBoundingClientRect() (border-box-ish)
// - Not spec-perfect: no observe(options) box types, limited fields, etc.

(() => {
  if (typeof window === "undefined") return; // SSR guard
  if (typeof (window as any).ResizeObserver !== "undefined") return;

  type RectSnapshot = { w: number; h: number; x: number; y: number };

  // Minimal entry shape most app code uses
  type SimpleResizeObserverEntry = {
    target: Element;
    contentRect: DOMRectReadOnly;
  };

  const observed = new Map<Element, RectSnapshot>(); // element -> last rect
  const observers = new Set<ResizeObserverPolyfill>();
  let rafId = 0;

  const round = (n: number) => Math.round(n);

  function rectOf(el: Element): RectSnapshot {
    const r = el.getBoundingClientRect();
    return { w: round(r.width), h: round(r.height), x: round(r.left), y: round(r.top) };
  }

  function isDifferent(a: RectSnapshot | undefined, b: RectSnapshot): boolean {
    return !a || a.w !== b.w || a.h !== b.h || a.x !== b.x || a.y !== b.y;
  }

  function ensureTicking(): void {
    if (!rafId && observed.size > 0) rafId = window.requestAnimationFrame(tick);
  }

  function stopIfIdle(): void {
    if (rafId && observed.size === 0) {
      window.cancelAnimationFrame(rafId);
      rafId = 0;
    }
  }

  function makeDOMRectReadOnly(width: number, height: number): DOMRectReadOnly {
    // DOMRectReadOnly may not be constructible everywhere; fall back to DOMRect.
    // Types allow DOMRect to be used as DOMRectReadOnly.
    try {
      return new DOMRectReadOnly(0, 0, width, height);
    } catch {
      return {x: 0, y: 0, width, height} as DOMRectReadOnly;
    }
  }

  function tick(): void {
    rafId = 0;

    for (const ro of observers) {
      if (ro._elements.size === 0) continue;

      const entries: SimpleResizeObserverEntry[] = [];

      for (const el of ro._elements) {
        const prev = observed.get(el);
        const next = rectOf(el);

        if (isDifferent(prev, next)) {
          observed.set(el, next);
          entries.push({
            target: el,
            contentRect: makeDOMRectReadOnly(next.w, next.h),
          });
        }
      }

      if (entries.length) {
        try {
          // Cast to official types when invoking callback
          ro._callback(entries as unknown as ResizeObserverEntry[], ro as unknown as ResizeObserver);
        } catch (e) {
          // Don’t break polling if callback throws
          setTimeout(() => {
            throw e;
          }, 0);
        }
      }
    }

    if (observed.size > 0) ensureTicking();
    else stopIfIdle();
  }

  class ResizeObserverPolyfill implements ResizeObserver {
    public _callback: ResizeObserverCallback;
    public _elements: Set<Element>;

    constructor(callback: ResizeObserverCallback) {
      if (typeof callback !== "function") {
        throw new TypeError("ResizeObserver callback must be a function");
      }
      this._callback = callback;
      this._elements = new Set<Element>();
      observers.add(this);
    }

    observe(target: Element): void {
      // ignore non-elements
      if (!(target instanceof Element)) return;

      this._elements.add(target);
      if (!observed.has(target)) observed.set(target, rectOf(target));
      ensureTicking();
    }

    unobserve(target: Element): void {
      this._elements.delete(target);

      // If nobody observes this element anymore, drop it
      let stillUsed = false;
      for (const ro of observers) {
        if (ro._elements.has(target)) {
          stillUsed = true;
          break;
        }
      }
      if (!stillUsed) observed.delete(target);

      stopIfIdle();
    }

    disconnect(): void {
      for (const el of this._elements) this.unobserve(el);
      this._elements.clear();
      observers.delete(this);
      stopIfIdle();
    }
  }

  (window as any).ResizeObserver = ResizeObserverPolyfill;
})();
