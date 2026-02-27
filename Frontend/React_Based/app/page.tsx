import { Header } from "@/components/header"
import { Hero } from "@/components/hero"
import FloatingDock from "@/components/floating-dock"
import { Features } from "@/components/features"
import { Footer } from "@/components/footer"

export default function Home() {
  return (
    <main className="min-h-screen bg-[var(--ink-black)]">
      <Header />
      <Hero />
      <Features />
      <Footer />
      <FloatingDock items={[]} />
    </main>
  )
}
