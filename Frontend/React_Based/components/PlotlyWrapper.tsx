// Lightweight Plotly wrapper using plotly.js-dist-min to avoid OOM during build
import createPlotlyComponent from "react-plotly.js/factory"
// @ts-expect-error - plotly.js-dist-min has no type declarations
import Plotly from "plotly.js-dist-min"

const Plot = createPlotlyComponent(Plotly)
export default Plot
