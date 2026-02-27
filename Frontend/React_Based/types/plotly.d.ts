declare module "react-plotly.js/factory" {
  import { Component, type ReactElement } from "react"
  import type Plotly from "plotly.js-dist-min"

  interface PlotParams {
    data: Plotly.Data[]
    layout?: Partial<Plotly.Layout>
    config?: Partial<Plotly.Config>
    style?: React.CSSProperties
    useResizeHandler?: boolean
    onInitialized?: (figure: { data: Plotly.Data[]; layout: Partial<Plotly.Layout> }, graphDiv: HTMLElement) => void
    onUpdate?: (figure: { data: Plotly.Data[]; layout: Partial<Plotly.Layout> }, graphDiv: HTMLElement) => void
    [key: string]: unknown
  }

  function createPlotlyComponent(plotly: typeof Plotly): new () => Component<PlotParams>
  export default createPlotlyComponent
}

declare module "plotly.js-dist-min" {
  import Plotly from "plotly.js"
  export default Plotly
}
