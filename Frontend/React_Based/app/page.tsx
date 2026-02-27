"use client"

import { useRouter } from "next/navigation"
import { Header } from "@/components/header"
import { Hero } from "@/components/hero"
import { ParticleBackground } from "@/components/particle-background"
import { ScrollDock } from "@/components/scroll-dock"
import { Features } from "@/components/features"
import { Footer } from "@/components/footer"
import { Home, Sparkles, BarChart3, Info } from "lucide-react"
import type { DockItemData } from "@/components/floating-dock"

export default function HomePage() {
  const router = useRouter()

  const dockItems: DockItemData[] = [
    {
      icon: <Home className="w-5 h-5 text-[var(--dusty-denim)]" />,
      label: "Home",
      onClick: () => window.scrollTo({ top: 0, behavior: "smooth" }),
    },
    {
      icon: <Sparkles className="w-5 h-5 text-[var(--dusty-denim)]" />,
      label: "Features",
      onClick: () => document.getElementById("features")?.scrollIntoView({ behavior: "smooth" }),
    },
    {
      icon: <BarChart3 className="w-5 h-5 text-[var(--dusty-denim)]" />,
      label: "Analysis",
      onClick: () => router.push("/dashboard"),
    },
    {
      icon: <Info className="w-5 h-5 text-[var(--dusty-denim)]" />,
      label: "About",
      onClick: () => document.getElementById("footer")?.scrollIntoView({ behavior: "smooth" }),
    },
  ]

  return (
    <main className="min-h-screen">
      <ParticleBackground />
      <div className="relative z-10">
        <Header />
        <Hero />
        <Features />
        <Footer />
      </div>
      <ScrollDock items={dockItems} />
    </main>
  )
}
