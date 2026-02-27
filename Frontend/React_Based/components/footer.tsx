import Link from "next/link"

export function Footer() {
  return (
    <footer id="footer" className="bg-[var(--ink-black)] border-t border-[var(--dusk-blue)]/20 py-12">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-8">
            <Link href="/" className="text-[var(--alabaster-grey)] text-xl font-bold">
              EVA
            </Link>
            <p className="text-sm text-[var(--dusty-denim)]">
              Autonomous Data Science. Localized.
            </p>
          </div>
          
          <div className="flex items-center gap-6">
            <Link href="#" className="text-sm text-[var(--dusty-denim)] hover:text-[var(--alabaster-grey)] transition-colors">
              Privacy
            </Link>
            <Link href="#" className="text-sm text-[var(--dusty-denim)] hover:text-[var(--alabaster-grey)] transition-colors">
              Terms
            </Link>
            <Link href="#" className="text-sm text-[var(--dusty-denim)] hover:text-[var(--alabaster-grey)] transition-colors">
              Contact
            </Link>
          </div>
        </div>
        
        <div className="mt-8 pt-8 border-t border-[var(--dusk-blue)]/20 text-center">
          <p className="text-sm text-[var(--dusty-denim)]">
            © 2026 EVA. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  )
}
