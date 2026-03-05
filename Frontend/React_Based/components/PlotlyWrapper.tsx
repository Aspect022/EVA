"use client"

import { useEffect, useRef, useState } from "react"

// Extend window type for Plotly
declare global {
  interface Window {
    Plotly?: {
      react: (el: HTMLElement, data: unknown[], layout?: unknown, config?: unknown) => void
      purge: (el: HTMLElement) => void
    }
  }
}

let plotlyLoaded = false
let plotlyLoading = false
const callbacks: Array<() => void> = []

function loadPlotlyCDN(): Promise<void> {
  if (plotlyLoaded && window.Plotly) return Promise.resolve()
  return new Promise((resolve) => {
    if (plotlyLoading) {
      callbacks.push(resolve)
      return
    }
    plotlyLoading = true
    const script = document.createElement("script")
    script.src = "https://cdn.plot.ly/plotly-2.35.2.min.js"
    script.async = true
    script.onload = () => {
      plotlyLoaded = true
      plotlyLoading = false
      resolve()
      callbacks.forEach(cb => cb())
      callbacks.length = 0
    }
    document.head.appendChild(script)
  })
}

interface PlotlyChartProps {
  data: unknown[]
  layout?: Record<string, unknown>
  config?: Record<string, unknown>
  style?: React.CSSProperties
  className?: string
}

export function PlotlyChart({ data, layout, config, style, className }: PlotlyChartProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    loadPlotlyCDN().then(() => setReady(true))
  }, [])

  useEffect(() => {
    if (!ready || !containerRef.current || !window.Plotly) return

    const mergedLayout = {
      autosize: true,
      margin: { l: 40, r: 20, t: 50, b: 40 },
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      font: { color: "rgba(255,255,255,0.7)", family: "Inter, sans-serif", size: 11 },
      ...layout,
    }

    const mergedConfig = {
      responsive: true,
      displayModeBar: false,
      ...config,
    }

    window.Plotly.react(containerRef.current, data as unknown[], mergedLayout, mergedConfig)

    return () => {
      if (containerRef.current && window.Plotly) {
        window.Plotly.purge(containerRef.current)
      }
    }
  }, [ready, data, layout, config])

  return (
    <div
      ref={containerRef}
      className={className}
      style={{ width: "100%", height: "320px", ...style }}
    >
      {!ready && (
        <div className="flex items-center justify-center h-full text-white/30 text-xs font-mono">
          Loading chart...
        </div>
      )}
    </div>
  )
}
