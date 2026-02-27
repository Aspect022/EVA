"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Menu, X } from "lucide-react";

const navItems = [
  { label: "Features", href: "#features" },
  { label: "How It Works", href: "#how-it-works" },
  { label: "Pricing", href: "#pricing" },
  { label: "Docs", href: "#docs" },
];

export function Header() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [activeLink, setActiveLink] = useState("");

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    // Check on mount as well
    handleScroll();

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <>
      <header
        className={`fixed top-0 left-0 right-0 z-50 w-full transition-all duration-300 ease-in-out ${
          isScrolled || isMobileMenuOpen
            ? "bg-[rgba(1,22,30,0.9)] backdrop-blur-[12px] border-b border-[rgba(89,131,146,0.2)]"
            : "bg-transparent border-b border-transparent"
        }`}
      >
        <div className="max-w-[1280px] mx-auto px-[24px]">
          <div className="flex items-center justify-between h-[64px] md:h-[72px]">
            {/* Left: Brand */}
            <Link
              href="/"
              className="relative text-[24px] font-[800] text-[#FFFFFF] tracking-tight flex items-start"
            >
              EVA
              <span className="w-[6px] h-[6px] rounded-full bg-[#F97316] absolute top-[4px] -right-[10px]" />
            </Link>

            {/* Center: Desktop Nav */}
            <nav className="hidden md:flex items-center gap-8 h-full">
              {navItems.map((item) => (
                <Link
                  key={item.label}
                  href={item.href}
                  onClick={() => setActiveLink(item.href)}
                  className={`relative flex items-center h-full text-[14px] font-[500] transition-colors duration-150 ${
                    activeLink === item.href
                      ? "text-[#FFFFFF]"
                      : "text-[#A0AEC0] hover:text-[#FFFFFF]"
                  }`}
                >
                  {item.label}
                  {activeLink === item.href && (
                    <span className="absolute bottom-0 left-0 right-0 h-[2px] bg-[#F97316]" />
                  )}
                </Link>
              ))}
            </nav>

            {/* Right: Actions */}
            <div className="hidden md:flex items-center gap-[12px]">
              <Link
                href="/signin"
                className="text-[#A0AEC0] hover:text-[#FFFFFF] transition-colors text-[14px] font-[500] px-3 py-2"
              >
                Sign In
              </Link>
              <Link
                href="/signup"
                className="bg-[#F97316] text-[#FFFFFF] px-[20px] py-[10px] rounded text-[14px] font-[600] transition-all duration-300 hover:shadow-[0_0_15px_rgba(249,115,22,0.5)]"
              >
                Start Free Trial
              </Link>
            </div>

            {/* Mobile Menu Toggle */}
            <button
              className="md:hidden text-[#598392] p-2 -mr-2 flex items-center justify-center transition-colors hover:text-[#FFFFFF]"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              aria-label={isMobileMenuOpen ? "Close menu" : "Open menu"}
            >
              {isMobileMenuOpen ? (
                <X className="w-[20px] h-[20px]" />
              ) : (
                <Menu className="w-[20px] h-[20px]" />
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Mobile Drawer */}
      <div
        className={`fixed top-[64px] left-0 right-0 bottom-0 z-40 bg-[#01161E] transform transition-transform duration-300 ease-in-out md:hidden ${
          isMobileMenuOpen
            ? "translate-y-0 opacity-100 pointer-events-auto"
            : "-translate-y-full opacity-0 pointer-events-none"
        }`}
      >
        <div className="flex flex-col p-[24px] h-full overflow-y-auto">
          <nav className="flex flex-col mb-8">
            {navItems.map((item) => (
              <Link
                key={item.label}
                href={item.href}
                onClick={() => {
                  setActiveLink(item.href);
                  setIsMobileMenuOpen(false);
                }}
                className={`flex items-center h-[48px] text-[16px] font-[500] border-b border-[rgba(89,131,146,0.1)] transition-colors ${
                  activeLink === item.href ? "text-[#FFFFFF]" : "text-[#A0AEC0]"
                }`}
              >
                {item.label}
              </Link>
            ))}
            <Link
              href="/signin"
              onClick={() => setIsMobileMenuOpen(false)}
              className="flex items-center h-[48px] text-[16px] font-[500] border-b border-[rgba(89,131,146,0.1)] text-[#A0AEC0] hover:text-[#FFFFFF] transition-colors"
            >
              Sign In
            </Link>
          </nav>

          <div className="mt-auto pb-8">
            <Link
              href="/signup"
              onClick={() => setIsMobileMenuOpen(false)}
              className="flex flex-col items-center justify-center w-full bg-[#F97316] text-[#FFFFFF] h-[48px] rounded text-[16px] font-[600] transition-all duration-300 hover:shadow-[0_0_15px_rgba(249,115,22,0.5)]"
            >
              Start Free Trial
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}
