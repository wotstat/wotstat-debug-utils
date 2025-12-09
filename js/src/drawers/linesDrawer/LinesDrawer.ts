import type { ModelValue } from '../../utils/types'

const enum LineEnd {
  None = 0,
  Arrow = 1,
}

type Point = {
  posx: number
  posy: number
  isVisible: boolean
}

export type SimpleLineData = {
  p1: Point
  p2: Point
  end1: LineEnd
  end2: LineEnd
  width: number
  color: string
}

export type PolyLineData = {
  points: Array<ModelValue<Point>>
  end1: LineEnd
  end2: LineEnd
  width: number
  color: string
  closed: boolean
}

export type BoxData = {
  p0: Point, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point, p6: Point, p7: Point
  width: number
  color: string
}

type Line = {
  points: { x: number, y: number }[]
}

function rotateVector(vec: { x: number, y: number }, angle: number, scale: number = 1): { x: number, y: number } {
  return {
    x: (vec.x * Math.cos(angle) - vec.y * Math.sin(angle)) * scale,
    y: (vec.x * Math.sin(angle) + vec.y * Math.cos(angle)) * scale
  }
}

export class LinesDrawer {

  private linesGroup: Map<string, {
    color: string
    width: number
    lines: Line[]
  }> = new Map()

  private getGroup(color: string, width: number) {
    const styleKey = `${width}-${color}`
    if (!this.linesGroup.has(styleKey)) this.linesGroup.set(styleKey, {
      color,
      width,
      lines: []
    })
    return this.linesGroup.get(styleKey)!
  }

  private arrowAtPoint(p1: [number, number], p2: [number, number], width: number): [number, number][] {
    const vec = {
      x: p1[0] - p2[0],
      y: p1[1] - p2[1]
    }

    const length = Math.sqrt(vec.x * vec.x + vec.y * vec.y)
    if (length === 0) return []

    const unitVec = {
      x: vec.x / length,
      y: vec.y / length
    }

    const arrowSize = 5 * (1 + width / 2 - 0.5)
    const arrowAngle = Math.PI / 6 // 30 degrees

    const leftArrowVec = rotateVector(unitVec, arrowAngle, arrowSize)
    const rightArrowVec = rotateVector(unitVec, -arrowAngle, arrowSize)

    return [
      [p1[0] - leftArrowVec.x, p1[1] - leftArrowVec.y],
      [p1[0], p1[1]],
      [p1[0] - rightArrowVec.x, p1[1] - rightArrowVec.y]
    ]
  }

  private continueAtPoint(p1: { x: number, y: number }, p2: { x: number, y: number }, width: number): { x: number, y: number }[] {
    const vec = {
      x: p1.x - p2.x,
      y: p1.y - p2.y
    }

    const length = Math.sqrt(vec.x * vec.x + vec.y * vec.y)
    if (length === 0) return []

    const unitVec = {
      x: vec.x / length,
      y: vec.y / length
    }

    const arrowSize = 2.5 * (1 + width / 2 - 0.5)
    const arrowAngle = Math.PI / 4 // 45 degrees

    const pos = rotateVector(unitVec, arrowAngle, arrowSize)

    const offset1 = rotateVector(unitVec, Math.PI / 2, arrowSize * 1.2)
    const offset2 = rotateVector(unitVec, -Math.PI / 2, arrowSize * 0.5)

    const r1 = { x: p1.x - offset1.x - unitVec.x * 1.3, y: p1.y - offset1.y - unitVec.y * 1.3 }
    const r2 = { x: p1.x - offset2.x - unitVec.x * 1.3, y: p1.y - offset2.y - unitVec.y * 1.3 }
    return [
      r1,
      { x: r1.x + pos.x, y: r1.y + pos.y },
      r2,
      { x: r2.x + pos.x, y: r2.y + pos.y },
    ]
  }

  prepareSimpleLine(data: SimpleLineData[]) {
    for (const lineData of data) {
      const group = this.getGroup(lineData.color, lineData.width)
      if (lineData.p1.isVisible === false || lineData.p2.isVisible === false) continue
      group.lines.push({
        points: [
          { x: lineData.p1.posx, y: lineData.p1.posy },
          { x: lineData.p2.posx, y: lineData.p2.posy },
        ]
      })

      if (lineData.end1 === LineEnd.Arrow) {
        const arrow = this.arrowAtPoint([lineData.p1.posx, lineData.p1.posy], [lineData.p2.posx, lineData.p2.posy], lineData.width)
        if (arrow.length != 0) group.lines.push({ points: arrow.map(p => ({ x: p[0], y: p[1] })) })
      }

      if (lineData.end2 === LineEnd.Arrow) {
        const arrow = this.arrowAtPoint([lineData.p2.posx, lineData.p2.posy], [lineData.p1.posx, lineData.p1.posy], lineData.width)
        if (arrow.length != 0) group.lines.push({ points: arrow.map(p => ({ x: p[0], y: p[1] })) })
      }
    }
  }

  preparePolyLine(data: PolyLineData[]) {

    for (const lineData of data) {
      const group = this.getGroup(lineData.color, lineData.width)
      const segments: Line[] = []

      let line: Line = { points: [] }
      let nextPointIsConnected = false
      for (let i = 0; i < lineData.points.length; i++) {
        const point = lineData.points[i].value

        if (point.isVisible === false) {
          nextPointIsConnected = true
          if (line.points.length > 1) {
            segments.push(line)
            if (line.points.length >= 2) {
              group.lines.push({
                points: this.continueAtPoint(line.points[line.points.length - 1], line.points[line.points.length - 2], lineData.width)
              })
            }
            line = { points: [] }
          }
          continue
        }

        if (nextPointIsConnected && line.points.length > 0) {
          group.lines.push({
            points: this.continueAtPoint(line.points[line.points.length - 1], { x: point.posx, y: point.posy }, lineData.width)
          })
          nextPointIsConnected = false
        }

        line.points.push({ x: point.posx, y: point.posy })
      }

      if (lineData.closed && line.points.length >= 2 && lineData.points[0].value.isVisible && lineData.points[lineData.points.length - 1].value.isVisible) {
        line.points.push({ x: lineData.points[0].value.posx, y: lineData.points[0].value.posy })
      }

      if (line.points.length > 0) segments.push(line)

      group.lines.push(...segments)

      if (lineData.end1 === LineEnd.Arrow && lineData.points.length >= 2 && lineData.points[0].value.isVisible && lineData.points[1].value.isVisible) {
        const p1 = lineData.points[0].value
        const p2 = lineData.points[1].value
        const arrow = this.arrowAtPoint([p1.posx, p1.posy], [p2.posx, p2.posy], lineData.width)
        if (arrow.length != 0) group.lines.push({ points: arrow.map(p => ({ x: p[0], y: p[1] })) })
      }

      if (lineData.end2 === LineEnd.Arrow) {
        const length = lineData.points.length
        const p0 = lineData.closed ? lineData.points[length - 1].value : lineData.points[length - 2].value
        const p1 = lineData.closed ? lineData.points[0].value : lineData.points[length - 1].value

        if (length >= 2 && p0.isVisible && p1.isVisible) {
          const arrow = this.arrowAtPoint([p1.posx, p1.posy], [p0.posx, p0.posy], lineData.width)
          if (arrow.length != 0) group.lines.push({ points: arrow.map(p => ({ x: p[0], y: p[1] })) })
        }
      }
    }
  }

  prepareBoxes(data: BoxData[]) {
    for (const boxData of data) {

      const l1 = [boxData.p0, boxData.p1, boxData.p2, boxData.p3]
      const l2 = [boxData.p4, boxData.p5, boxData.p6, boxData.p7]
      const connectors = [
        [boxData.p0, boxData.p4],
        [boxData.p1, boxData.p5],
        [boxData.p2, boxData.p6],
        [boxData.p3, boxData.p7]
      ]

      this.preparePolyLine(
        [l1, l2, ...connectors].map(points => ({
          width: boxData.width,
          color: boxData.color,
          closed: true,
          end1: LineEnd.None,
          end2: LineEnd.None,
          points: points.map(p => ({ value: p, id: '' }))
        }))
      )
    }
  }

  draw(ctx: CanvasRenderingContext2D) {
    for (const group of this.linesGroup.values()) {

      ctx.lineWidth = group.width
      ctx.strokeStyle = group.color
      ctx.lineJoin = 'round'

      ctx.beginPath()
      for (const line of group.lines) {
        if (line.points.length === 0) continue
        ctx.moveTo(line.points[0].x, line.points[0].y)

        for (let i = 1; i < line.points.length; i++)
          ctx.lineTo(line.points[i].x, line.points[i].y)
      }
      ctx.stroke()
    }

    this.linesGroup.clear()
  }
}