import Link from "next/link";
import Image from "next/image";
import { Github, Twitter, Linkedin } from "lucide-react";

const linkGroups = [
  {
    title: "Product",
    links: [
      { label: "Documentation", href: "#" },
      { label: "Architecture", href: "#agents" },
      { label: "GAL Trace", href: "#gal-trace" },
    ],
  },
  {
    title: "Legal",
    links: [
      { label: "Privacy Policy", href: "#" },
      { label: "Terms of Service", href: "#" },
      { label: "Security", href: "#security" },
    ],
  },
];

const socials = [
  { icon: Github, href: "#", label: "GitHub" },
  { icon: Twitter, href: "#", label: "X / Twitter" },
  { icon: Linkedin, href: "#", label: "LinkedIn" },
];

export function Footer() {
  return (
    <footer id="footer" className="relative bg-black border-t border-white/[0.06] pt-16 pb-8">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-10 md:gap-8 mb-12">
          {/* Brand Column */}
          <div className="md:col-span-2">
            <Link href="/" className="inline-block mb-4">
              <Image
                src="/logo.png"
                alt="EVA"
                width={80}
                height={36}
                className="h-[30px] w-auto object-contain brightness-0 invert"
              />
            </Link>
            <p className="text-sm text-white/30 max-w-xs leading-relaxed mb-6">
              Autonomous Data Science OS. Session-based analytical reasoning, multi-agent ML pipelines, and
              human-in-the-loop control — running entirely on your hardware.
            </p>

            {/* Social Icons */}
            <div className="flex items-center gap-3">
              {socials.map((social) => (
                <Link
                  key={social.label}
                  href={social.href}
                  aria-label={social.label}
                  className="w-8 h-8 flex items-center justify-center rounded-lg bg-white/[0.04] hover:bg-white/[0.08] transition-colors"
                >
                  <social.icon className="w-4 h-4 text-white/40 hover:text-white/70 transition-colors" />
                </Link>
              ))}
            </div>
          </div>

          {/* Link Columns */}
          {linkGroups.map((group) => (
            <div key={group.title}>
              <h4
                className="text-xs tracking-[0.15em] text-white/50 uppercase mb-4"
                style={{ fontFamily: "var(--font-fira-code, 'Fira Code', monospace)" }}
              >
                {group.title}
              </h4>
              <ul className="space-y-3">
                {group.links.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      className="text-sm text-white/30 hover:text-white/70 transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="pt-8 border-t border-white/[0.04] flex flex-col sm:flex-row items-center justify-between gap-4">
          <p
            className="text-xs text-white/20"
            style={{ fontFamily: "var(--font-fira-code, 'Fira Code', monospace)" }}
          >
            © {new Date().getFullYear()} EVA. All rights reserved.
          </p>
          <p
            className="text-xs text-white/15"
            style={{ fontFamily: "var(--font-fira-code, 'Fira Code', monospace)" }}
          >
            Built with autonomous intelligence.
          </p>
        </div>
      </div>
    </footer>
  );
}
