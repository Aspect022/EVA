"use client"

import { useEffect, useRef } from "react"

interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  size: number
  opacity: number
  color: string
}

export function ParticleBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const particlesRef = useRef<Particle[]>([])
  const animationIdRef = useRef<number | undefined>(undefined)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const resizeCanvas = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }
    resizeCanvas()
    window.addEventListener("resize", resizeCanvas)

    const colors = ["#00d4ff", "#a78bfa", "#10b981"]
    const particleCount = 50

    particlesRef.current = Array.from({ length: particleCount }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 2,
      vy: (Math.random() - 0.5) * 2,
      size: Math.random() * 3 + 1,
      opacity: Math.random() * 0.5 + 0.3,
      color: colors[Math.floor(Math.random() * colors.length)],
    }))

    const animate = () => {
      ctx.fillStyle = "rgba(15, 15, 30, 0.1)"
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      particlesRef.current.forEach((particle, i) => {
        particle.x += particle.vx
        particle.y += particle.vy

        if (particle.x - particle.size < 0 || particle.x + particle.size > canvas.width) {
          particle.vx *= -1
          particle.x = Math.max(particle.size, Math.min(canvas.width - particle.size, particle.x))
        }
        if (particle.y - particle.size < 0 || particle.y + particle.size > canvas.height) {
          particle.vy *= -1
          particle.y = Math.max(particle.size, Math.min(canvas.height - particle.size, particle.y))
        }

        ctx.fillStyle = particle.color
        ctx.globalAlpha = particle.opacity
        ctx.beginPath()
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
        ctx.fill()

        for (let j = i + 1; j < particlesRef.current.length; j++) {
          const other = particlesRef.current[j]
          const dx = particle.x - other.x
          const dy = particle.y - other.y
          const distance = Math.sqrt(dx * dx + dy * dy)

          if (distance < 150) {
            ctx.strokeStyle = particle.color
            ctx.globalAlpha = (1 - distance / 150) * 0.3
            ctx.lineWidth = 1
            ctx.beginPath()
            ctx.moveTo(particle.x, particle.y)
            ctx.lineTo(other.x, other.y)
            ctx.stroke()
          }
        }
      })

      ctx.globalAlpha = 1
      animationIdRef.current = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      window.removeEventListener("resize", resizeCanvas)
      if (animationIdRef.current) {
        cancelAnimationFrame(animationIdRef.current)
      }
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 -z-10 pointer-events-none"
      style={{ background: "linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 100%)" }}
    />
  )
}
