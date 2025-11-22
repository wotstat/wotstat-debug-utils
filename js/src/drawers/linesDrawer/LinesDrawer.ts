
type LineData = {
  p1: {
    posx: number
    posy: number
    isVisible: boolean
  }
  p2: {
    posx: number
    posy: number
    isVisible: boolean
  }
  width: number
  color: string
}


export class LinesDrawer {
  draw(data: LineData[], ctx: CanvasRenderingContext2D) {
    if (data.length === 0) return

    const groupedByStyle: { [key: string]: { width: number, color: string, lines: LineData[] } } = {}

    for (let i = 0; i < data.length; i++) {
      const lineData = data[i]
      const styleKey = `${lineData.width}-${lineData.color}`
      if (!groupedByStyle[styleKey]) {
        groupedByStyle[styleKey] = {
          width: lineData.width,
          color: lineData.color,
          lines: []
        }
      }
      groupedByStyle[styleKey].lines.push(lineData)
    }

    for (const styleKey in groupedByStyle) {
      const group = groupedByStyle[styleKey]
      ctx.beginPath()

      for (const lineData of group.lines) {
        if (lineData.p1.isVisible && lineData.p2.isVisible) {
          ctx.moveTo(lineData.p1.posx, lineData.p1.posy)
          ctx.lineTo(lineData.p2.posx, lineData.p2.posy)
        }
      }

      ctx.lineWidth = group.width
      ctx.strokeStyle = group.color
      ctx.stroke()
    }
  }
}