import { Cpu, Lock, Zap, BarChart3, Database, Globe } from "lucide-react"

const features = [
  {
    icon: Cpu,
    title: "Autonomous AI Engine",
    description: "Self-learning algorithms that adapt to your data patterns without manual intervention.",
  },
  {
    icon: Lock,
    title: "Complete Privacy",
    description: "All processing happens locally. Your data never leaves your environment.",
  },
  {
    icon: Zap,
    title: "Lightning Fast",
    description: "Optimized for performance with GPU acceleration and parallel processing.",
  },
  {
    icon: BarChart3,
    title: "Advanced Analytics",
    description: "Deep insights with predictive modeling, anomaly detection, and trend analysis.",
  },
  {
    icon: Database,
    title: "Universal Data Support",
    description: "Connect to any data source — SQL, NoSQL, APIs, files, and streaming data.",
  },
  {
    icon: Globe,
    title: "Edge Deployment",
    description: "Deploy models at the edge for real-time inference with minimal latency.",
  },
]

export function Features() {
  return (
    <section id="features" className="relative py-24 lg:py-32 bg-[var(--prussian-blue)]">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="text-center mb-16">
          <span className="inline-block text-xs font-semibold uppercase tracking-[0.08em] text-[var(--cta-orange)] mb-4 font-mono">
            Features
          </span>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-[var(--alabaster-grey)] mb-6 text-balance">
            Everything you need for<br />autonomous data science
          </h2>
          <p className="text-lg text-[var(--dusty-denim)] max-w-2xl mx-auto leading-relaxed">
            Built for data scientists and engineers who demand control, privacy, and performance.
          </p>
        </div>
        
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="group relative bg-[var(--ink-black)] border border-[var(--dusk-blue)]/30 rounded-2xl p-8 hover:border-[var(--dusk-blue)] transition-all hover:shadow-[0_0_20px_rgba(65,90,119,0.25)]"
            >
              <div className="w-12 h-12 flex items-center justify-center rounded-xl bg-[var(--dusk-blue)]/20 mb-6 group-hover:bg-[var(--cta-orange)]/10 transition-colors">
                <feature.icon className="w-6 h-6 text-[var(--dusty-denim)] group-hover:text-[var(--cta-orange)] transition-colors" />
              </div>
              <h3 className="text-xl font-semibold text-[var(--alabaster-grey)] mb-3">
                {feature.title}
              </h3>
              <p className="text-[var(--dusty-denim)] leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
