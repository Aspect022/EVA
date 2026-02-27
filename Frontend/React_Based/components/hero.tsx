import Image from "next/image"
import Link from "next/link"

export function Hero() {
  return (
    <section className="relative min-h-screen flex items-center bg-[var(--ink-black)] overflow-hidden pt-16">
      {/* Background subtle pattern */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--prussian-blue)_0%,_var(--ink-black)_70%)] opacity-50" />
      
      {/* Geometric grid pattern overlay */}
      <div 
        className="absolute inset-0 opacity-5"
        style={{
          backgroundImage: `linear-gradient(var(--dusk-blue) 1px, transparent 1px), linear-gradient(90deg, var(--dusk-blue) 1px, transparent 1px)`,
          backgroundSize: '60px 60px'
        }}
      />
      
      <div className="relative max-w-7xl mx-auto px-6 lg:px-8 py-24 lg:py-32">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-8 items-center">
          {/* Left content */}
          <div className="space-y-8">
            <div className="space-y-6">
              <h1 className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-extrabold text-[var(--alabaster-grey)] leading-[1.1] tracking-tight text-balance">
                AUTONOMOUS<br />
                DATA SCIENCE.<br />
                <span className="text-[var(--dusty-denim)]">LOCALIZED.</span>
              </h1>
              
              <p className="text-lg text-[var(--dusty-denim)] max-w-lg leading-relaxed">
                Deploy powerful AI-driven analytics directly in your local environment. 
                Full control, complete privacy, zero compromise.
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-4">
              <Link
                href="#"
                className="inline-flex items-center justify-center bg-[var(--cta-orange)] text-[var(--ink-black)] px-8 py-4 rounded-lg text-base font-bold uppercase tracking-wide hover:bg-[#EA6C0A] transition-all shadow-[0_0_24px_rgba(249,115,22,0.35)] hover:shadow-[0_0_32px_rgba(249,115,22,0.5)]"
              >
                Start Free Trial
              </Link>
              <Link
                href="#"
                className="inline-flex items-center justify-center border border-[var(--dusk-blue)] text-[var(--alabaster-grey)] px-8 py-4 rounded-lg text-base font-semibold hover:bg-[var(--prussian-blue)] transition-colors"
              >
                View Demo
              </Link>
            </div>
            
            <p className="text-sm text-[var(--dusty-denim)]">
              No credit card required.
            </p>
          </div>
          
          {/* Right content - Brain image */}
          <div className="relative flex items-center justify-center lg:justify-end">
            <div className="relative w-full max-w-lg lg:max-w-xl aspect-square">
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--dusk-blue)_0%,_transparent_70%)] opacity-30 blur-3xl" />
              <Image
                src="/images/neural-brain.jpg"
                alt="Neural network brain visualization representing autonomous AI data science"
                fill
                className="object-contain relative z-10"
                priority
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
