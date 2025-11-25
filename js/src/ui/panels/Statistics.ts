import { BasePanel } from './panelController/PanelController'

type StatisticsLine = {
  line: HTMLElement
  nameElement: HTMLElement
  valueContainer: HTMLElement
}

export class StatisticsPanel extends BasePanel {

  private readonly totalTime: StatisticsLine
  private readonly renderMarkerTime: StatisticsLine
  private readonly renderLinesTime: StatisticsLine
  private readonly prepareLinesTime: StatisticsLine
  private readonly markersCount: StatisticsLine
  private readonly simpleLinesCount: StatisticsLine
  private readonly polyLinesCount: StatisticsLine
  private readonly boxesCount: StatisticsLine

  constructor() {
    super('Statistics')

    this.totalTime = this.createLine('Total time', '0 ms')
    this.renderMarkerTime = this.createLine('Render markers', '0 ms')
    this.renderLinesTime = this.createLine('Render lines', '0 ms')
    this.prepareLinesTime = this.createLine('Prepare lines', '0 ms')
    this.createSeparator()
    this.markersCount = this.createLine('Markers count', '0')
    this.simpleLinesCount = this.createLine('Simple lines count', '0')
    this.polyLinesCount = this.createLine('Poly lines count', '0')
    this.boxesCount = this.createLine('Boxes count', '0')
  }


  updateStatistics(stats: {
    totalTimeMs: number
    renderMarkerTimeMs: number
    renderLinesTimeMs: number
    prepareLinesTimeMs: number
    markersCount: number
    simpleLinesCount: number
    polyLinesCount: number
    boxesCount: number
  }) {
    this.totalTime.valueContainer.textContent = `${stats.totalTimeMs.toFixed(2)} ms`
    this.renderMarkerTime.valueContainer.textContent = `${stats.renderMarkerTimeMs.toFixed(2)} ms`
    this.renderLinesTime.valueContainer.textContent = `${stats.renderLinesTimeMs.toFixed(2)} ms`
    this.prepareLinesTime.valueContainer.textContent = `${stats.prepareLinesTimeMs.toFixed(2)} ms`
    this.markersCount.valueContainer.textContent = `${stats.markersCount}`
    this.simpleLinesCount.valueContainer.textContent = `${stats.simpleLinesCount}`
    this.polyLinesCount.valueContainer.textContent = `${stats.polyLinesCount}`
    this.boxesCount.valueContainer.textContent = `${stats.boxesCount}`
  }
}