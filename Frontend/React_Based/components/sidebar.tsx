"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import {
  ChevronLeft,
  ChevronRight,
  Workflow,
  FolderOpen,
  Settings,
} from "lucide-react"
import { useSession } from "@/lib/session-context"

const navItems = [
  { name: "Pipeline", href: "/dashboard", icon: Workflow },
  { name: "Sessions", href: "/dashboard/sessions", icon: FolderOpen },
  { name: "Settings", href: "/dashboard/settings", icon: Settings },
]

const sidebarVariants = {
  hidden: { x: -20, opacity: 0 },
  visible: {
    x: 0,
    opacity: 1,
    transition: {
      type: "spring" as const,
      stiffness: 100,
      damping: 20,
      staggerChildren: 0.08,
      delayChildren: 0.2,
    },
  },
}

const navItemVariants = {
  hidden: { x: -16, opacity: 0 },
  visible: {
    x: 0,
    opacity: 1,
    transition: { type: "spring" as const, stiffness: 120, damping: 16 },
  },
}

export function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const pathname = usePathname()
  const { sessionId } = useSession()

  return (
    <motion.aside
      initial="hidden"
      animate="visible"
      variants={sidebarVariants}
      className={`relative h-screen bg-[var(--prussian-blue)] border-r border-[var(--dusk-blue)]/30 transition-all duration-300 flex flex-col ${
        isCollapsed ? "w-20" : "w-64"
      }`}
    >
      {/* Logo area */}
      <div className="flex items-center justify-between p-4 border-b border-[var(--dusk-blue)]/30">
        <AnimatePresence mode="wait">
          {!isCollapsed ? (
            <motion.div
              key="full"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.2 }}
            >
              <Link href="/" className="flex items-center gap-2">
                <span className="text-2xl font-black text-[var(--alabaster-grey)] tracking-tighter">
                  EVA
                </span>
              </Link>
            </motion.div>
          ) : (
            <motion.div
              key="mini"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.2 }}
              className="mx-auto"
            >
              <Link href="/">
                <span className="text-xl font-black text-[var(--alabaster-grey)] tracking-tighter">
                  E
                </span>
              </Link>
            </motion.div>
          )}
        </AnimatePresence>
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => setIsCollapsed(!isCollapsed)}
          className={`p-1.5 rounded-lg hover:bg-[var(--dusk-blue)]/30 text-[var(--dusty-denim)] hover:text-[var(--alabaster-grey)] transition-colors ${
            isCollapsed
              ? "absolute -right-4 top-5 bg-[var(--prussian-blue)] border border-[var(--dusk-blue)]/30 shadow-lg"
              : ""
          }`}
        >
          {isCollapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <ChevronLeft className="w-4 h-4" />
          )}
        </motion.button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-6 px-3 space-y-1.5 overflow-y-auto custom-scrollbar">
        {navItems.map((item, index) => {
          const isActive = pathname === item.href
          const Icon = item.icon

          return (
            <motion.div key={item.name} variants={navItemVariants}>
              <Link
                href={item.href}
                className={`relative flex items-center ${
                  isCollapsed ? "justify-center" : "justify-start"
                } gap-3 px-3 py-3 rounded-xl transition-all duration-200 group cursor-pointer ${
                  isActive
                    ? "bg-[var(--cta-orange)]/10 text-[var(--alabaster-grey)]"
                    : "text-[var(--dusty-denim)] hover:bg-[var(--dusk-blue)]/15 hover:text-[var(--alabaster-grey)]"
                }`}
                title={isCollapsed ? item.name : undefined}
              >
                {/* Active indicator bar */}
                {isActive && (
                  <motion.div
                    layoutId="sidebar-active"
                    className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-6 rounded-r-full bg-[var(--cta-orange)]"
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}

                <motion.div
                  whileHover={{ scale: 1.1, rotate: isActive ? 0 : 5 }}
                  transition={{ type: "spring", stiffness: 400, damping: 15 }}
                >
                  <Icon
                    className={`w-5 h-5 transition-colors ${
                      isActive ? "text-[var(--cta-orange)]" : ""
                    }`}
                  />
                </motion.div>

                <AnimatePresence>
                  {!isCollapsed && (
                    <motion.span
                      initial={{ opacity: 0, width: 0 }}
                      animate={{ opacity: 1, width: "auto" }}
                      exit={{ opacity: 0, width: 0 }}
                      transition={{ duration: 0.2 }}
                      className="font-medium whitespace-nowrap overflow-hidden"
                    >
                      {item.name}
                    </motion.span>
                  )}
                </AnimatePresence>
              </Link>
            </motion.div>
          )
        })}
      </nav>

      {/* Session info footer */}
      <AnimatePresence>
        {!isCollapsed && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ type: "spring", stiffness: 100, damping: 16 }}
            className="p-4 border-t border-[var(--dusk-blue)]/30"
          >
            {sessionId ? (
              <div className="flex flex-col gap-1">
                <span className="text-xs uppercase tracking-wider text-[var(--dusty-denim)] font-mono">
                  Active Session
                </span>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-emerald-400 animate-breathe" />
                  <span className="text-sm font-mono text-[var(--alabaster-grey)] truncate">
                    {sessionId.slice(0, 12)}...
                  </span>
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-xl bg-[var(--dusk-blue)]/20 flex items-center justify-center text-xs font-bold text-[var(--dusty-denim)]">
                  U
                </div>
                <div className="flex flex-col">
                  <span className="text-sm font-medium text-[var(--alabaster-grey)]">
                    User
                  </span>
                  <span className="text-xs text-[var(--dusty-denim)]">
                    Local Environment
                  </span>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.aside>
  )
}
