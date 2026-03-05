"use client";

import { EvaHero } from "@/components/eva-hero/eva-hero";
import { AgentShowcase } from "@/components/sections/agent-showcase";
import { GalTrace } from "@/components/sections/gal-trace";
import { SecurityPrivacy } from "@/components/sections/security-privacy";
import { FinalCta } from "@/components/sections/final-cta";
import { Footer } from "@/components/footer";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-black">
      <EvaHero />
      <section id="next-section">
        <AgentShowcase />
      </section>
      <GalTrace />
      <SecurityPrivacy />
      <FinalCta />
      <Footer />
    </main>
  );
}
