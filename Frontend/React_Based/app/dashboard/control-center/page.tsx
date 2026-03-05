"use client";

import { motion } from "framer-motion";
import {
  GitBranch,
  GitCommit,
  GitPullRequest,
  Activity as ActivityIcon,
  Users,
  Settings2,
  Play,
  CheckCircle2,
  ArrowLeftRight,
  GitMerge,
  Plus,
  ArrowUpCircle,
  Clock,
  History as HistoryIcon,
  FileText,
  BrainCircuit,
  LayoutDashboard,
  AlertTriangle,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function ControlCenterPage() {
  return (
    <div className="flex flex-col gap-6 h-full max-w-6xl mx-auto pb-10">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="flex flex-col gap-2"
      >
        <h1 className="text-3xl font-black text-white tracking-tight">
          Control Center
        </h1>
        <p className="text-white/60 font-mono text-sm max-w-2xl">
          Analysis Versioning & Collaboration layer.
        </p>
      </motion.div>

      {/* Data Snapshot Banner */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.1 }}
        className="flex items-center gap-6 p-4 bg-white/[0.02] border border-white/[0.05] rounded-xl flex-wrap shadow-xl shadow-black/50"
      >
        <div className="flex items-center gap-3">
          <span className="text-xs text-white/40 uppercase tracking-widest font-mono">
            Data Version
          </span>
          <span className="text-sm font-bold text-white font-mono bg-white/[0.05] px-2 py-1 rounded">
            v3
          </span>
        </div>
        <div className="w-px h-6 bg-white/[0.1] hidden md:block" />
        <div className="flex items-center gap-3">
          <span className="text-xs text-white/40 uppercase tracking-widest font-mono">
            Schema Hash
          </span>
          <span className="text-sm font-mono text-white/80">#a84f3c9</span>
        </div>
        <div className="w-px h-6 bg-white/[0.1] hidden md:block" />
        <div className="flex items-center gap-3">
          <span className="text-xs text-white/40 uppercase tracking-widest font-mono">
            Rows
          </span>
          <span className="text-sm font-mono text-white/80">14.2M</span>
        </div>
        <div className="w-px h-6 bg-white/[0.1] hidden md:block" />
        <div className="flex items-center gap-3 md:ml-auto">
          <span className="text-xs text-white/40 uppercase tracking-widest font-mono">
            Drift Status
          </span>
          <div className="flex items-center gap-1.5 bg-emerald-500/10 border border-emerald-500/20 px-2 py-1 rounded">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs font-medium text-emerald-400 uppercase tracking-wider">
              Stable
            </span>
          </div>
        </div>
      </motion.div>

      <Tabs defaultValue="versions" className="w-full mt-2">
        <TabsList className="bg-white/[0.02] border border-white/[0.05] p-1 h-auto rounded-xl inline-flex w-full md:w-auto overflow-x-auto">
          <TabsTrigger
            value="versions"
            className="rounded-lg px-4 py-2 text-sm font-medium data-[state=active]:bg-white/[0.08] data-[state=active]:text-white text-white/60 flex items-center gap-2"
          >
            <GitCommit className="w-4 h-4" />
            Versions
          </TabsTrigger>
          <TabsTrigger
            value="branches"
            className="rounded-lg px-4 py-2 text-sm font-medium data-[state=active]:bg-white/[0.08] data-[state=active]:text-white text-white/60 flex items-center gap-2"
          >
            <GitBranch className="w-4 h-4" />
            Branches
          </TabsTrigger>
          <TabsTrigger
            value="merge-requests"
            className="rounded-lg px-4 py-2 text-sm font-medium data-[state=active]:bg-white/[0.08] data-[state=active]:text-white text-white/60 flex items-center gap-2"
          >
            <GitPullRequest className="w-4 h-4" />
            Merge Requests
          </TabsTrigger>
          <TabsTrigger
            value="activity"
            className="rounded-lg px-4 py-2 text-sm font-medium data-[state=active]:bg-white/[0.08] data-[state=active]:text-white text-white/60 flex items-center gap-2"
          >
            <ActivityIcon className="w-4 h-4" />
            Activity
          </TabsTrigger>
        </TabsList>

        {/* VERSIONS TAB */}
        <TabsContent value="versions" className="mt-6 space-y-6">
          {/* Top Section */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="bg-white/[0.02] border-white/[0.05] md:col-span-2">
              <CardContent className="p-4 flex items-center gap-4 h-full">
                <div className="w-12 h-12 rounded-xl bg-orange-500/10 flex items-center justify-center shrink-0 border border-orange-500/20">
                  <span className="font-black text-xl text-orange-400 font-mono">
                    EV
                  </span>
                </div>
                <div className="flex flex-col">
                  <span className="text-sm text-white/40 uppercase tracking-widest font-mono">
                    Project Name
                  </span>
                  <span className="text-xl font-bold text-white">
                    Project EVA Alpha
                  </span>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white/[0.02] border-white/[0.05]">
              <CardContent className="p-4 flex flex-col justify-center h-full">
                <span className="text-xs text-white/40 uppercase tracking-widest font-mono mb-1">
                  Active Version
                </span>
                <div className="flex items-center gap-2">
                  <span className="text-2xl font-bold text-white font-mono">
                    v17
                  </span>
                  <span className="text-[10px] bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2 py-0.5 rounded font-mono">
                    HEAD
                  </span>
                </div>
                <span className="text-xs text-white/40 mt-1">
                  Data Snapshot: v3
                </span>
              </CardContent>
            </Card>

            <Card className="bg-white/[0.02] border-white/[0.05]">
              <CardContent className="p-4 flex flex-col justify-center h-full">
                <span className="text-xs text-white/40 uppercase tracking-widest font-mono mb-1">
                  Sync Status
                </span>
                <div className="flex items-center gap-2 mt-1">
                  <span className="flex h-3 w-3 relative">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                  </span>
                  <span className="text-sm font-medium text-emerald-400">
                    Synced to Cloud
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Timeline Section */}
          <div className="mt-8 relative max-w-4xl">
            <div className="absolute left-8 flex items-center justify-center top-4 bottom-4 w-px bg-white/[0.05]" />

            <div className="space-y-6">
              {[
                {
                  id: "v17",
                  author: "Jayesh",
                  time: "10 mins ago",
                  impact: "High",
                  confidence: 94,
                  active: true,
                  changes: [
                    "Merged feat/anomalies branch",
                    "Updated Random Forest hyperparameters",
                    "Added executive summary to insights",
                  ],
                },
                {
                  id: "v16",
                  author: "System",
                  time: "2 hours ago",
                  impact: "Medium",
                  confidence: 88,
                  active: false,
                  changes: [
                    "Auto-snapshot before RL tuning",
                    "Invalidated cache for model metrics",
                  ],
                },
                {
                  id: "v15",
                  author: "Jayesh",
                  time: "1 day ago",
                  impact: "Low",
                  confidence: 96,
                  active: false,
                  changes: [
                    "Updated feature importance chart colors",
                    "Fixed typo in report section",
                  ],
                },
              ].map((version, i) => (
                <div
                  key={version.id}
                  className="relative flex gap-6 items-start group"
                >
                  <div
                    className={`mt-4 w-16 text-right shrink-0 text-white/40 font-mono text-xs pt-1`}
                  >
                    {version.time}
                  </div>

                  <div className="relative flex flex-col items-center justify-start pt-4 z-10">
                    <div
                      className={`w-3 h-3 rounded-full border-2 ${version.active ? "bg-orange-500 border-none shadow-[0_0_15px_rgba(249,115,22,0.5)]" : "bg-black border-white/20 group-hover:border-white/50 transition-colors"}`}
                    />
                  </div>

                  <Card
                    className={`flex-1 transition-all ${version.active ? "bg-white/[0.03] border-white/[0.1]" : "bg-white/[0.01] border-white/[0.03] hover:border-white/[0.08]"}`}
                  >
                    <CardHeader className="pb-3 flex flex-row items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-lg font-bold text-white font-mono">
                          {version.id}
                        </span>
                        <div className="w-px h-4 bg-white/[0.1]" />
                        <div className="flex items-center gap-2 text-sm text-white/60">
                          <div className="w-6 h-6 rounded-full bg-white/[0.05] flex items-center justify-center text-[10px] font-bold text-white">
                            {version.author.charAt(0)}
                          </div>
                          {version.author}
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        {version.impact === "High" && (
                          <span className="text-[10px] bg-red-500/10 text-red-400 border border-red-500/20 px-2 py-0.5 rounded font-mono uppercase">
                            High Impact
                          </span>
                        )}
                        {version.impact === "Medium" && (
                          <span className="text-[10px] bg-yellow-500/10 text-yellow-400 border border-yellow-500/20 px-2 py-0.5 rounded font-mono uppercase">
                            Med Impact
                          </span>
                        )}
                        {version.impact === "Low" && (
                          <span className="text-[10px] bg-white/5 text-white/40 border border-white/10 px-2 py-0.5 rounded font-mono uppercase">
                            Low Impact
                          </span>
                        )}
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-white/40 font-mono text-right w-8">
                            {version.confidence}%
                          </span>
                          <div className="w-16 h-1.5 bg-white/[0.05] rounded-full overflow-hidden">
                            <div
                              className="h-full bg-emerald-400"
                              style={{ width: `${version.confidence}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <ul className="space-y-1.5 text-sm text-white/60 list-disc pl-4">
                        {version.changes.map((change, cIdx) => (
                          <li key={cIdx}>{change}</li>
                        ))}
                      </ul>

                      <div className="flex items-center gap-3 pt-4 border-t border-white/[0.05] opacity-50 group-hover:opacity-100 transition-opacity">
                        <button className="text-xs font-medium text-white/80 hover:text-white bg-white/[0.03] hover:bg-white/[0.08] px-3 py-1.5 rounded border border-white/[0.05] transition-colors flex items-center gap-1.5">
                          View details
                        </button>
                        {!version.active && (
                          <button className="text-xs font-medium text-white/80 hover:text-white bg-white/[0.03] hover:bg-white/[0.08] px-3 py-1.5 rounded border border-white/[0.05] transition-colors flex items-center gap-1.5">
                            <ArrowLeftRight className="w-3.5 h-3.5" />
                            Compare to v17
                          </button>
                        )}
                        {!version.active && (
                          <button className="text-xs font-medium text-orange-400/80 hover:text-orange-400 bg-orange-500/10 hover:bg-orange-500/20 px-3 py-1.5 rounded border border-orange-500/20 transition-colors flex items-center gap-1.5 ml-auto">
                            <HistoryIcon className="w-3.5 h-3.5" />
                            Rollback to this
                          </button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ))}
            </div>
            <div className="pl-[7rem] pt-6 flex justify-center w-full">
              <button className="text-xs text-white/40 hover:text-white/80 font-mono transition-colors border border-white/[0.05] bg-white/[0.02] hover:bg-white/[0.05] rounded px-4 py-2">
                Load Older Versions...
              </button>
            </div>
          </div>
        </TabsContent>

        {/* BRANCHES TAB */}
        <TabsContent value="branches" className="mt-6 space-y-6">
          <div className="flex items-center justify-between p-4 bg-white/[0.02] border border-white/[0.05] rounded-xl max-w-4xl">
            <div className="flex items-center gap-3">
              <span className="text-xs uppercase tracking-widest text-white/40 font-mono">
                Active Branch
              </span>
              <div className="flex items-center gap-2 bg-white/[0.05] border border-white/[0.1] px-3 py-1.5 rounded-lg">
                <GitBranch className="w-4 h-4 text-orange-400" />
                <span className="font-bold text-white text-sm">main</span>
              </div>
            </div>
            <button className="bg-white text-black hover:bg-white/90 px-4 py-2 rounded-lg text-sm font-bold transition-colors flex items-center gap-2">
              <Plus className="w-4 h-4" />
              New Branch
            </button>
          </div>

          <div className="space-y-4 max-w-4xl">
            {[
              {
                name: "jayesh-branch",
                author: "Jayesh",
                time: "1 hour ago",
                insights: 4,
                ml: 2,
                status: "Ahead",
                statusColor: "text-emerald-400",
              },
              {
                name: "exp/rl-tuning",
                author: "System",
                time: "10 hours ago",
                insights: 1,
                ml: 5,
                status: "Behind",
                statusColor: "text-red-400",
              },
              {
                name: "hotfix/data-cleaning",
                author: "Jayesh",
                time: "3 days ago",
                insights: 0,
                ml: 1,
                status: "Synced",
                statusColor: "text-white/40",
              },
            ].map((branch, i) => (
              <Card
                key={i}
                className="bg-white/[0.02] border-white/[0.05] hover:border-white/[0.1] transition-colors rounded-xl overflow-hidden"
              >
                <div className="p-4 flex items-center justify-between">
                  <div className="flex items-center gap-4 w-1/3">
                    <div className="w-10 h-10 rounded-lg bg-white/[0.05] flex items-center justify-center shrink-0 border border-white/[0.05]">
                      <GitBranch className="w-5 h-5 text-white/80" />
                    </div>
                    <div>
                      <h4 className="font-medium text-white">{branch.name}</h4>
                      <div className="flex items-center gap-2 text-xs text-white/40 font-mono mt-1">
                        <span>by {branch.author}</span>
                        <span>•</span>
                        <span>{branch.time}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-8 w-1/3 justify-center">
                    <div className="flex flex-col items-center gap-1">
                      <span className="text-xl font-bold text-white font-mono">
                        {branch.insights}
                      </span>
                      <span className="text-[10px] uppercase tracking-wider text-white/40">
                        New Insights
                      </span>
                    </div>
                    <div className="w-px h-8 bg-white/[0.1]" />
                    <div className="flex flex-col items-center gap-1">
                      <span className="text-xl font-bold text-white font-mono">
                        {branch.ml}
                      </span>
                      <span className="text-[10px] uppercase tracking-wider text-white/40">
                        ML Exps
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 w-1/3 justify-end">
                    <div
                      className={`text-xs font-mono uppercase flex items-center gap-1.5 ${branch.statusColor}`}
                    >
                      {branch.status === "Ahead" && (
                        <ArrowUpCircle className="w-4 h-4" />
                      )}
                      {branch.status === "Behind" && (
                        <Clock className="w-4 h-4 text-red-400" />
                      )}
                      {branch.status === "Synced" && (
                        <CheckCircle2 className="w-4 h-4" />
                      )}
                      {branch.status}
                    </div>
                    <div className="flex items-center gap-2">
                      <button className="bg-white/[0.03] hover:bg-white/[0.08] text-white/80 hover:text-white border border-white/[0.05] px-3 py-1.5 rounded transition-colors text-xs font-medium flex items-center gap-1.5">
                        Compare
                      </button>
                      <button className="bg-[#F97316]/10 text-[#F97316] hover:bg-[#F97316]/20 border border-[#F97316]/20 px-3 py-1.5 rounded transition-colors text-xs font-medium flex items-center gap-1.5">
                        Merge
                      </button>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* MERGE REQUESTS TAB (Placeholder) */}
        <TabsContent value="merge-requests" className="mt-6">
          <Card className="bg-white/[0.02] border-white/[0.05]">
            <CardContent className="flex flex-col items-center justify-center py-20">
              <GitPullRequest className="w-12 h-12 text-white/20 mb-4" />
              <h3 className="text-xl font-medium text-white mb-2">
                No Active Merge Requests
              </h3>
              <p className="text-white/40 text-sm max-w-sm text-center">
                There are no pending branch merges at this time. Create a branch
                and request a merge to see them here.
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ACTIVITY TAB */}
        <TabsContent value="activity" className="mt-6">
          <Card className="bg-white/[0.02] border-white/[0.05]">
            <CardHeader className="border-b border-white/[0.05]">
              <CardTitle className="text-lg font-medium text-white flex items-center gap-2">
                <ActivityIcon className="w-5 h-5 text-indigo-400" />
                Audit Trail
              </CardTitle>
              <CardDescription className="text-white/40">
                Detailed system and user activity log
              </CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              <div className="flex flex-col">
                {[
                  {
                    type: "Insight Created",
                    author: "EVA Agent",
                    time: "10 mins ago",
                    version: "v17",
                    color: "blue",
                    icon: FileText,
                    desc: "Identified anomalous correlation between sales and weather metrics.",
                  },
                  {
                    type: "Model Trained",
                    author: "System",
                    time: "1 hour ago",
                    version: "v16",
                    color: "green",
                    icon: BrainCircuit,
                    desc: "Random Forest regressor training completed with 94% confidence.",
                  },
                  {
                    type: "Merge Approved",
                    author: "Jayesh",
                    time: "3 hours ago",
                    version: "v16",
                    color: "orange",
                    icon: GitMerge,
                    desc: "Merged branch 'feat/anomalies' into main.",
                  },
                  {
                    type: "Conflict",
                    author: "System",
                    time: "1 day ago",
                    version: "v15",
                    color: "red",
                    icon: AlertTriangle,
                    desc: "Merge conflict detected in ML hyperparameters configuration.",
                  },
                  {
                    type: "Dashboard Modified",
                    author: "Jayesh",
                    time: "1.5 days ago",
                    version: "v15",
                    color: "purple",
                    icon: LayoutDashboard,
                    desc: "Added 2 new KPI widgets to the main performance view.",
                  },
                ].map((log, i) => {
                  const Icon = log.icon;

                  // Get color variants
                  const colorClasses = {
                    blue: "text-blue-400 bg-blue-500/10 border-blue-500/20",
                    green:
                      "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
                    purple:
                      "text-purple-400 bg-purple-500/10 border-purple-500/20",
                    orange:
                      "text-orange-400 bg-orange-500/10 border-orange-500/20",
                    red: "text-red-400 bg-red-500/10 border-red-500/20",
                  }[log.color];

                  return (
                    <div
                      key={i}
                      className="flex gap-4 p-4 border-b border-white/[0.05] hover:bg-white/[0.02] transition-colors relative group"
                    >
                      <div className="w-12 text-right shrink-0 text-white/40 font-mono text-xs pt-1 hidden sm:block">
                        {log.time.split(" ")[0] +
                          log.time.split(" ")[1].charAt(0)}
                      </div>
                      <div
                        className={`mt-0.5 w-8 h-8 rounded-full flex items-center justify-center shrink-0 border ${colorClasses}`}
                      >
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 mb-1">
                          <h4 className="text-sm font-medium text-white">
                            {log.type}
                          </h4>
                          <div className="flex items-center gap-2 text-xs font-mono">
                            <span
                              className={`px-2 py-0.5 rounded border ${colorClasses} uppercase`}
                            >
                              {log.color === "red" ? "Alert" : "Log"}
                            </span>
                            <span className="text-white/40">
                              by{" "}
                              <span className="text-white/80">
                                {log.author}
                              </span>
                            </span>
                            <span className="text-white/20">•</span>
                            <span className="text-white/40 uppercase tracking-widest">
                              {log.version}
                            </span>
                            <span className="text-white/40 sm:hidden ml-auto">
                              {log.time}
                            </span>
                          </div>
                        </div>
                        <p className="text-sm text-white/60 line-clamp-2 md:line-clamp-1 group-hover:text-white/80 transition-colors">
                          {log.desc}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="p-4 flex justify-center border-t border-white/[0.05] bg-white/[0.01]">
                <button className="text-xs text-indigo-400 hover:text-indigo-300 font-mono transition-colors border border-indigo-500/20 bg-indigo-500/10 hover:bg-indigo-500/20 rounded px-4 py-2 flex items-center gap-2">
                  <Clock className="w-3.5 h-3.5" />
                  Load More Events
                </button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
