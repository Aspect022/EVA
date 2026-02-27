"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import Image from "next/image"

export function Header() {
  const [isScrolled, setIsScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50)
    }
    
    handleScroll()
    
    window.addEventListener("scroll", handleScroll, { passive: true })
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  return (
    <header 
      className={`fixed top-0 left-0 right-0 z-50 w-full transition-all duration-300 ease-in-out ${
        isScrolled
          ? "bg-[rgba(1,22,30,0.9)] backdrop-blur-[12px] border-b border-[rgba(89,131,146,0.2)]"
          : "bg-transparent border-b border-transparent"
      }`}
    >
      <div className="max-w-[1280px] mx-auto px-[24px]">
        <div className="flex items-center justify-between h-[64px] md:h-[72px]">
          {/* Brand Logo */}
          <Link href="/" className="flex items-center">
            <Image
              src="/logo.jpg"
              alt="EVA"
              width={72}
              height={32}
              className="h-[28px] md:h-[32px] w-auto object-contain"
              priority
            />
          </Link>
          
          {/* Empty spacer since we removed navigation for landing page */}
          <div />
        </div>
      </div>
    </header>
  )
}
