"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { 
  ChevronLeft, 
  ChevronRight, 
  Workflow,
  FolderOpen,
  Settings,
  Home
} from "lucide-react"
import { useSession } from "@/lib/session-context"

export function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const pathname = usePathname()
  const { sessionId } = useSession()

  const navItems = [
    { name: "Pipeline", href: "/dashboard", icon: <Workflow className="w-5 h-5" /> },
    { name: "Sessions", href: "/dashboard/sessions", icon: <FolderOpen className="w-5 h-5" /> },
    { name: "Settings", href: "/dashboard/settings", icon: <Settings className="w-5 h-5" /> },
  ]

  return (
    <aside 
      className={`relative h-screen bg-[var(--prussian-blue)] border-r border-[var(--dusk-blue)] transition-all duration-300 flex flex-col ${
        isCollapsed ? "w-20" : "w-64"
      }`}
    >
      <div className="flex items-center justify-between p-4 border-b border-[var(--dusk-blue)]">
        {!isCollapsed && (
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl font-black text-[var(--alabaster-grey)] tracking-tighter">EVA</span>
          </Link>
        )}
        {isCollapsed && (
          <Link href="/" className="mx-auto">
            <span className="text-xl font-black text-[var(--alabaster-grey)] tracking-tighter">E</span>
          </Link>
        )}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className={`p-1.5 rounded-md hover:bg-[var(--dusk-blue)] text-[var(--dusty-denim)] hover:text-[var(--alabaster-grey)] transition-colors ${
            isCollapsed ? "absolute -right-4 top-5 bg-[var(--prussian-blue)] border border-[var(--dusk-blue)]" : ""
          }`}
        >
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      <nav className="flex-1 py-6 px-3 space-y-2 overflow-y-auto custom-scrollbar">
        {navItems.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center ${isCollapsed ? "justify-center" : "justify-start"} gap-3 px-3 py-3 rounded-md transition-colors ${
                isActive 
                  ? "bg-[var(--dusk-blue)]/30 text-[var(--alabaster-grey)] border border-[var(--dusk-blue)]" 
                  : "text-[var(--dusty-denim)] hover:bg-[var(--dusk-blue)]/20 hover:text-[var(--alabaster-grey)]"
              }`}
              title={isCollapsed ? item.name : undefined}
            >
              {item.icon}
              {!isCollapsed && <span className="font-medium">{item.name}</span>}
            </Link>
          )
        })}
      </nav>
      
      {!isCollapsed && (
        <div className="p-4 border-t border-[var(--dusk-blue)]">
          {sessionId ? (
            <div className="flex flex-col gap-1">
              <span className="text-xs uppercase tracking-wider text-[var(--dusty-denim)] font-mono">Active Session</span>
              <span className="text-sm font-mono text-[var(--alabaster-grey)] truncate">{sessionId.slice(0, 12)}...</span>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-[var(--dusk-blue)]/50 flex items-center justify-center text-xs font-bold text-[var(--dusty-denim)]">
                U
              </div>
              <div className="flex flex-col">
                <span className="text-sm font-medium text-[var(--alabaster-grey)]">User</span>
                <span className="text-xs text-[var(--dusty-denim)]">Local Environment</span>
              </div>
            </div>
          )}
        </div>
      )}
    </aside>
  )
}
