import { Header } from "@/components/header"
import { Hero } from "@/components/hero"
import { ParticleBackground } from "@/components/particle-background"
import { ScrollDock } from "@/components/scroll-dock"
import { Features } from "@/components/features"
import { Footer } from "@/components/footer"

export default function Home() {
  return (
    <main className="min-h-screen">
      <ParticleBackground />
      <div className="relative z-10">
        <Header />
        <Hero />
        <Features />
        <Footer />
      </div>
      <ScrollDock items={[]} />
    </main>
  )
}
