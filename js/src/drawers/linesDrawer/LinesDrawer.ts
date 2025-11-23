
const enum LineEnd {
  None = 0,
  Arrow = 1,
}

export type LineData = {
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
  end1: LineEnd
  end2: LineEnd
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

          if (lineData.end1 == LineEnd.None && lineData.end2 == LineEnd.None) continue

          function drawArrowAtPoint(p1: { x: number, y: number }, p2: { x: number, y: number }) {
            const vec = {
              x: p1.x - p2.x,
              y: p1.y - p2.y
            }

            const length = Math.sqrt(vec.x * vec.x + vec.y * vec.y)
            if (length === 0) return

            const unitVec = {
              x: vec.x / length,
              y: vec.y / length
            }

            const arrowSize = 5 * (1 + group.width / 2 - 0.5)
            const arrowAngle = Math.PI / 6 // 30 degrees

            const leftArrowVec = {
              x: unitVec.x * Math.cos(arrowAngle) - unitVec.y * Math.sin(arrowAngle),
              y: unitVec.x * Math.sin(arrowAngle) + unitVec.y * Math.cos(arrowAngle)
            }

            const rightArrowVec = {
              x: unitVec.x * Math.cos(-arrowAngle) - unitVec.y * Math.sin(-arrowAngle),
              y: unitVec.x * Math.sin(-arrowAngle) + unitVec.y * Math.cos(-arrowAngle)
            }

            ctx.moveTo(p1.x - leftArrowVec.x * arrowSize, p1.y - leftArrowVec.y * arrowSize)
            ctx.lineTo(p1.x, p1.y)
            ctx.lineTo(p1.x - rightArrowVec.x * arrowSize, p1.y - rightArrowVec.y * arrowSize)
          }


          if (lineData.end1 === LineEnd.Arrow) {
            drawArrowAtPoint(
              { x: lineData.p1.posx, y: lineData.p1.posy },
              { x: lineData.p2.posx, y: lineData.p2.posy }
            )
          }

          if (lineData.end2 === LineEnd.Arrow) {
            drawArrowAtPoint(
              { x: lineData.p2.posx, y: lineData.p2.posy },
              { x: lineData.p1.posx, y: lineData.p1.posy }
            )
          }
        }
      }

      ctx.lineWidth = group.width
      ctx.strokeStyle = group.color
      ctx.stroke()
    }
  }
}