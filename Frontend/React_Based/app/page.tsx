"use client";

import { EvaHero } from "@/components/eva-hero/eva-hero";
import { AgentOrchestration } from "@/components/sections/agent-orchestration";
import { GalTrace } from "@/components/sections/gal-trace";
import { SecurityPrivacy } from "@/components/sections/security-privacy";
import { FinalCta } from "@/components/sections/final-cta";
import { Footer } from "@/components/footer";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-black">
      <EvaHero />
      <AgentOrchestration />
      <GalTrace />
      <SecurityPrivacy />
      <FinalCta />
      <Footer />
    </main>
  );
}
