"use client";

import { motion } from "framer-motion";
import { Settings, User, Bell, Shield, Key } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function SettingsPage() {
  return (
    <div className="flex flex-col gap-8 h-full max-w-4xl mx-auto pb-10">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
          <Settings className="w-8 h-8 text-white/80" />
          Settings
        </h1>
        <p className="text-white/60 mt-2 font-mono text-sm max-w-2xl">
          Manage your account, preferences, and API keys.
        </p>
      </motion.div>

      <div className="grid gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <Card className="bg-white/[0.02] border-white/[0.05]">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <User className="w-5 h-5 text-blue-400" />
                Profile
              </CardTitle>
              <CardDescription className="text-white/40">
                Update your personal information.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid gap-2">
                  <label className="text-sm font-medium text-white/80">
                    Name
                  </label>
                  <input
                    type="text"
                    disabled
                    value="Jayesh"
                    className="bg-white/[0.02] border border-white/[0.05] rounded-lg px-3 py-2 text-white/60 focus:outline-none"
                  />
                </div>
                <div className="grid gap-2">
                  <label className="text-sm font-medium text-white/80">
                    Email
                  </label>
                  <input
                    type="email"
                    disabled
                    value="jayesh@example.com"
                    className="bg-white/[0.02] border border-white/[0.05] rounded-lg px-3 py-2 text-white/60 focus:outline-none"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
        >
          <Card className="bg-white/[0.02] border-white/[0.05]">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <Key className="w-5 h-5 text-orange-400" />
                API Keys
              </CardTitle>
              <CardDescription className="text-white/40">
                Manage your external model integration keys (OpenAI, Anthropic).
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col gap-3">
                <div className="flex items-center justify-between p-3 bg-white/[0.02] rounded-lg border border-white/[0.05]">
                  <div className="flex items-center gap-3">
                    <Shield className="w-4 h-4 text-emerald-400" />
                    <span className="text-sm text-white font-medium">
                      OpenAI API Key
                    </span>
                  </div>
                  <span className="text-xs text-white/40 font-mono">
                    sk-...abc
                  </span>
                </div>
                <button className="text-sm text-white/80 hover:text-white bg-white/[0.03] hover:bg-white/[0.08] px-4 py-2 rounded-lg border border-white/[0.05] transition-colors self-start">
                  Add New Key
                </button>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.3 }}
        >
          <Card className="bg-white/[0.02] border-white/[0.05]">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <Bell className="w-5 h-5 text-purple-400" />
                Notifications
              </CardTitle>
              <CardDescription className="text-white/40">
                Configure your pipeline alert preferences.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-white/80">
                    Pipeline Failures
                  </span>
                  <div className="w-10 h-5 bg-emerald-500 rounded-full relative cursor-pointer">
                    <div className="absolute right-1 top-0.5 w-4 h-4 bg-white rounded-full" />
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-white/80">
                    Merge Request Updates
                  </span>
                  <div className="w-10 h-5 bg-emerald-500 rounded-full relative cursor-pointer">
                    <div className="absolute right-1 top-0.5 w-4 h-4 bg-white rounded-full" />
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-white/80">
                    Model Drift Alerts
                  </span>
                  <div className="w-10 h-5 bg-white/[0.1] rounded-full relative cursor-pointer">
                    <div className="absolute left-1 top-0.5 w-4 h-4 bg-white/60 rounded-full" />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
