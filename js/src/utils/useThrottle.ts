
export function useThrottle<T extends (...args: any[]) => void>(func: T, delay: number): T {
  let lastCall = 0
  let timeoutId: ReturnType<typeof setTimeout> | null = null
  let lastArgs: any[] | null = null

  const throttledFunction = function (...args: any[]) {
    const now = Date.now()
    const remainingTime = delay - (now - lastCall)

    if (remainingTime <= 0) {
      if (timeoutId) {
        clearTimeout(timeoutId)
        timeoutId = null
      }
      lastCall = now
      func(...args)
    } else {
      lastArgs = args
      if (!timeoutId) {
        timeoutId = setTimeout(() => {
          lastCall = Date.now()
          timeoutId = null
          if (lastArgs) {
            func(...lastArgs)
            lastArgs = null
          }
        }, remainingTime)
      }
    }
  }

  return throttledFunction as T
}