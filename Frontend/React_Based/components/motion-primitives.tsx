"use client"

import { motion, useInView, type Variants } from "framer-motion"
import { useRef, type ReactNode } from "react"

const springTransition = {
  type: "spring" as const,
  stiffness: 100,
  damping: 15,
  mass: 0.8,
}

const fadeUpVariants: Variants = {
  hidden: { opacity: 0, y: 40, filter: "blur(4px)" },
  visible: { opacity: 1, y: 0, filter: "blur(0px)" },
}

const fadeInVariants: Variants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: { opacity: 1, scale: 1 },
}

const slideInLeftVariants: Variants = {
  hidden: { opacity: 0, x: -60 },
  visible: { opacity: 1, x: 0 },
}

const slideInRightVariants: Variants = {
  hidden: { opacity: 0, x: 60 },
  visible: { opacity: 1, x: 0 },
}

const scaleInVariants: Variants = {
  hidden: { opacity: 0, scale: 0.8, filter: "blur(6px)" },
  visible: { opacity: 1, scale: 1, filter: "blur(0px)" },
}

type AnimationType = "fadeUp" | "fadeIn" | "slideLeft" | "slideRight" | "scaleIn"

const variantMap: Record<AnimationType, Variants> = {
  fadeUp: fadeUpVariants,
  fadeIn: fadeInVariants,
  slideLeft: slideInLeftVariants,
  slideRight: slideInRightVariants,
  scaleIn: scaleInVariants,
}

interface RevealProps {
  children: ReactNode
  animation?: AnimationType
  delay?: number
  duration?: number
  className?: string
  once?: boolean
  threshold?: number
}

export function Reveal({
  children,
  animation = "fadeUp",
  delay = 0,
  duration = 0.6,
  className,
  once = true,
  threshold = 0.2,
}: RevealProps) {
  const ref = useRef<HTMLDivElement>(null)
  const isInView = useInView(ref, { once, amount: threshold })

  return (
    <motion.div
      ref={ref}
      initial="hidden"
      animate={isInView ? "visible" : "hidden"}
      variants={variantMap[animation]}
      transition={{ ...springTransition, delay, duration }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

interface StaggerContainerProps {
  children: ReactNode
  staggerDelay?: number
  className?: string
  once?: boolean
  threshold?: number
}

export function StaggerContainer({
  children,
  staggerDelay = 0.1,
  className,
  once = true,
  threshold = 0.15,
}: StaggerContainerProps) {
  const ref = useRef<HTMLDivElement>(null)
  const isInView = useInView(ref, { once, amount: threshold })

  const containerVariants: Variants = {
    hidden: {},
    visible: {
      transition: {
        staggerChildren: staggerDelay,
        delayChildren: 0.1,
      },
    },
  }

  return (
    <motion.div
      ref={ref}
      initial="hidden"
      animate={isInView ? "visible" : "hidden"}
      variants={containerVariants}
      className={className}
    >
      {children}
    </motion.div>
  )
}

interface StaggerItemProps {
  children: ReactNode
  animation?: AnimationType
  className?: string
}

export function StaggerItem({
  children,
  animation = "fadeUp",
  className,
}: StaggerItemProps) {
  return (
    <motion.div
      variants={variantMap[animation]}
      transition={springTransition}
      className={className}
    >
      {children}
    </motion.div>
  )
}

interface FloatingElementProps {
  children: ReactNode
  amplitude?: number
  duration?: number
  delay?: number
  className?: string
}

export function FloatingElement({
  children,
  amplitude = 10,
  duration = 4,
  delay = 0,
  className,
}: FloatingElementProps) {
  return (
    <motion.div
      animate={{
        y: [-amplitude, amplitude, -amplitude],
      }}
      transition={{
        duration,
        repeat: Infinity,
        ease: "easeInOut",
        delay,
      }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

interface GlowPulseProps {
  children: ReactNode
  color?: string
  className?: string
}

export function GlowPulse({
  children,
  color = "rgba(249, 115, 22, 0.4)",
  className,
}: GlowPulseProps) {
  return (
    <motion.div
      animate={{
        boxShadow: [
          `0 0 20px ${color}`,
          `0 0 40px ${color}`,
          `0 0 20px ${color}`,
        ],
      }}
      transition={{
        duration: 2.5,
        repeat: Infinity,
        ease: "easeInOut",
      }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

export function TextReveal({
  text,
  className,
  delay = 0,
}: {
  text: string
  className?: string
  delay?: number
}) {
  const ref = useRef<HTMLSpanElement>(null)
  const isInView = useInView(ref, { once: true, amount: 0.5 })

  const words = text.split(" ")

  return (
    <span ref={ref} className={className}>
      {words.map((word, i) => (
        <motion.span
          key={i}
          initial={{ opacity: 0, y: 20, filter: "blur(4px)" }}
          animate={isInView ? { opacity: 1, y: 0, filter: "blur(0px)" } : {}}
          transition={{
            ...springTransition,
            delay: delay + i * 0.06,
          }}
          className="inline-block mr-[0.25em]"
        >
          {word}
        </motion.span>
      ))}
    </span>
  )
}

interface CountUpProps {
  target: number
  duration?: number
  suffix?: string
  prefix?: string
  className?: string
}

export function CountUp({
  target,
  duration = 2,
  suffix = "",
  prefix = "",
  className,
}: CountUpProps) {
  const ref = useRef<HTMLSpanElement>(null)
  const isInView = useInView(ref, { once: true })

  return (
    <span ref={ref} className={className}>
      {isInView ? (
        <motion.span
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          {prefix}
          <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            {target}
          </motion.span>
          {suffix}
        </motion.span>
      ) : (
        <span className="opacity-0">{prefix}0{suffix}</span>
      )}
    </span>
  )
}

export const magneticHover = {
  whileHover: { scale: 1.05, y: -2 },
  whileTap: { scale: 0.97 },
  transition: springTransition,
}

export const cardHover = {
  whileHover: {
    y: -6,
    boxShadow: "0 20px 40px rgba(0, 0, 0, 0.3), 0 0 30px rgba(249, 115, 22, 0.15)",
  },
  transition: { type: "spring", stiffness: 300, damping: 20 },
}
