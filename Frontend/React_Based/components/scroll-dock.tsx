"use client"

import { useState, useEffect } from "react"
import FloatingDock from "@/components/floating-dock"
import type { DockItemData } from "@/components/floating-dock"

interface ScrollDockProps {
  items: DockItemData[]
}

export function ScrollDock({ items }: ScrollDockProps) {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setIsVisible(window.scrollY > 50)
    }

    handleScroll()

    window.addEventListener("scroll", handleScroll, { passive: true })
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  return (
    <div
      className={`fixed bottom-0 left-0 right-0 z-40 flex justify-center transition-all duration-500 ease-in-out ${
        isVisible
          ? "translate-y-0 opacity-100 pointer-events-auto"
          : "translate-y-full opacity-0 pointer-events-none"
      }`}
    >
      <FloatingDock items={items} />
    </div>
  )
}
