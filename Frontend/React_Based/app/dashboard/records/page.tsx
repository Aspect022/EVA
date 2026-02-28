"use client";

import { motion } from "framer-motion";
import {
  Archive,
  BarChart2,
  LayoutDashboard,
  FileText,
  Search,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function RecordsPage() {
  return (
    <div className="flex flex-col gap-6 h-full max-w-6xl mx-auto pb-10">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="flex flex-col gap-2"
      >
        <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
          <Archive className="w-8 h-8 text-white/80" />
          Records
        </h1>
        <p className="text-white/60 font-mono text-sm max-w-2xl">
          Centralized repository for all generated Visualizations, Dashboards,
          and Reports across sessions.
        </p>
      </motion.div>

      {/* Search Bar Placeholder */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.1 }}
        className="relative max-w-md w-full"
      >
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
        <input
          type="text"
          placeholder="Search records by session, name, or date..."
          className="w-full bg-white/[0.02] border border-white/[0.05] hover:border-white/[0.1] focus:border-white/[0.2] transition-colors rounded-lg pl-10 pr-4 py-2.5 text-sm text-white focus:outline-none focus:ring-1 focus:ring-white/[0.1]"
        />
      </motion.div>

      <Tabs defaultValue="visualizations" className="w-full mt-2">
        <TabsList className="bg-white/[0.02] border border-white/[0.05] p-1 h-auto rounded-xl inline-flex w-full md:w-auto overflow-x-auto">
          <TabsTrigger
            value="visualizations"
            className="rounded-lg px-4 py-2 text-sm font-medium data-[state=active]:bg-white/[0.08] data-[state=active]:text-white text-white/60 flex items-center gap-2"
          >
            <BarChart2 className="w-4 h-4" />
            Visualizations
          </TabsTrigger>
          <TabsTrigger
            value="dashboards"
            className="rounded-lg px-4 py-2 text-sm font-medium data-[state=active]:bg-white/[0.08] data-[state=active]:text-white text-white/60 flex items-center gap-2"
          >
            <LayoutDashboard className="w-4 h-4" />
            Dashboards
          </TabsTrigger>
          <TabsTrigger
            value="reports"
            className="rounded-lg px-4 py-2 text-sm font-medium data-[state=active]:bg-white/[0.08] data-[state=active]:text-white text-white/60 flex items-center gap-2"
          >
            <FileText className="w-4 h-4" />
            Reports
          </TabsTrigger>
        </TabsList>

        {/* VISUALIZATIONS TAB */}
        <TabsContent value="visualizations" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                title: "Anomaly Distribution Map",
                type: "Scatter Plot",
                session: "v17 • 2h ago",
              },
              {
                title: "Sales Forecast Timeline",
                type: "Line Chart",
                session: "v16 • 1d ago",
              },
              {
                title: "Customer Cluster Analysis",
                type: "Bubble Chart",
                session: "v15 • 2d ago",
              },
            ].map((viz, i) => (
              <Card
                key={i}
                className="bg-white/[0.02] border-white/[0.05] hover:border-white/[0.1] transition-all cursor-pointer group group-hover:bg-white/[0.03]"
              >
                <CardHeader className="p-4 pb-2">
                  <div className="flex justify-between items-start gap-2">
                    <CardTitle className="text-base text-white/90 group-hover:text-white transition-colors">
                      {viz.title}
                    </CardTitle>
                    <BarChart2 className="w-4 h-4 text-orange-400 shrink-0" />
                  </div>
                  <CardDescription className="text-white/40 text-xs font-mono">
                    {viz.type}
                  </CardDescription>
                </CardHeader>
                <CardContent className="p-4 pt-2">
                  <div className="aspect-video w-full bg-black/40 border border-white/[0.05] rounded-lg mt-2 flex items-center justify-center relative overflow-hidden">
                    {/* Placeholder graphic for visualization thumbnail */}
                    <div className="absolute inset-0 bg-gradient-to-tr from-orange-500/10 to-transparent opacity-50" />
                    <BarChart2 className="w-8 h-8 text-white/10" />
                  </div>
                  <div className="flex items-center justify-between mt-4">
                    <span className="text-xs text-white/30 font-mono tracking-widest uppercase">
                      {viz.session}
                    </span>
                    <button className="text-xs text-white/60 hover:text-white bg-white/[0.03] hover:bg-white/[0.08] border border-white/[0.05] px-2 py-1 rounded transition-colors">
                      View Full
                    </button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* DASHBOARDS TAB */}
        <TabsContent value="dashboards" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {[
              {
                title: "Executive Performance Summary",
                items: 12,
                session: "v17 • 2h ago",
              },
              {
                title: "Operational Risk KPIs",
                items: 8,
                session: "v14 • 1w ago",
              },
            ].map((dash, i) => (
              <Card
                key={i}
                className="bg-white/[0.02] border-white/[0.05] hover:border-white/[0.1] transition-all cursor-pointer group"
              >
                <div className="flex flex-col sm:flex-row h-full">
                  <div className="sm:w-2/5 aspect-video sm:aspect-auto bg-black border-b sm:border-b-0 sm:border-r border-white/[0.05] relative overflow-hidden flex items-center justify-center">
                    <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:20px_20px]" />
                    <div className="absolute inset-0 bg-gradient-to-tr from-emerald-500/10 to-transparent opacity-30" />
                    <LayoutDashboard className="w-10 h-10 text-white/10" />
                  </div>
                  <div className="sm:w-3/5 p-5 flex flex-col justify-between">
                    <div>
                      <div className="flex items-center gap-2 mb-1 text-emerald-400">
                        <LayoutDashboard className="w-4 h-4" />
                        <span className="text-[10px] uppercase tracking-wider font-mono">
                          Dashboard View
                        </span>
                      </div>
                      <h3 className="text-lg font-medium text-white/90 group-hover:text-white transition-colors leading-tight">
                        {dash.title}
                      </h3>
                      <p className="text-xs text-white/40 mt-2">
                        {dash.items} widgets arranged
                      </p>
                    </div>
                    <div className="flex items-center justify-between mt-6">
                      <span className="text-xs text-white/30 font-mono tracking-widest uppercase">
                        {dash.session}
                      </span>
                      <button className="text-[10px] font-medium uppercase tracking-wider text-emerald-400 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/20 px-3 py-1.5 rounded transition-colors">
                        Open View
                      </button>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* REPORTS TAB */}
        <TabsContent value="reports" className="mt-6">
          <div className="flex flex-col gap-4 max-w-4xl">
            {[
              {
                title: "Q3 Technical Due Diligence",
                score: 94,
                size: "1.2 MB",
                session: "v17 • 2h ago",
              },
              {
                title: "Anomaly Detection Post-Mortem",
                score: 88,
                size: "840 KB",
                session: "v16 • 1d ago",
              },
              {
                title: "Customer Churn Prediction Analysis",
                score: 91,
                size: "2.1 MB",
                session: "v12 • 2w ago",
              },
              {
                title: "Inventory Restocking Strategy Memo",
                score: 85,
                size: "1.5 MB",
                session: "v10 • 1mo ago",
              },
            ].map((report, i) => (
              <Card
                key={i}
                className="bg-white/[0.02] border-white/[0.05] hover:border-white/[0.1] transition-all group flex flex-col sm:flex-row"
              >
                <div className="p-4 flex items-center gap-4 flex-1">
                  <div className="w-12 h-12 bg-blue-500/10 border border-blue-500/20 rounded-xl flex items-center justify-center shrink-0">
                    <FileText className="w-5 h-5 text-blue-400" />
                  </div>
                  <div className="min-w-0">
                    <h4 className="text-base font-medium text-white/90 group-hover:text-white transition-colors truncate">
                      {report.title}
                    </h4>
                    <div className="flex items-center gap-3 mt-1.5">
                      <span className="text-xs text-white/40 font-mono tracking-widest uppercase">
                        {report.session}
                      </span>
                      <span className="w-1 h-1 bg-white/20 rounded-full" />
                      <span className="text-xs text-white/40 font-mono uppercase">
                        {report.size}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="p-4 sm:border-l border-t sm:border-t-0 border-white/[0.05] flex items-center justify-between sm:justify-end gap-6 sm:w-64 shrink-0 bg-white/[0.01]">
                  <div className="flex flex-col items-start sm:items-end">
                    <span className="text-[10px] text-white/40 uppercase tracking-widest font-mono mb-0.5">
                      Confidence
                    </span>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold text-white font-mono">
                        {report.score}%
                      </span>
                      <div className="w-12 h-1.5 bg-white/[0.05] rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-400"
                          style={{ width: `${report.score}%` }}
                        />
                      </div>
                    </div>
                  </div>
                  <button className="text-blue-400 hover:text-white hover:bg-blue-500/20 bg-blue-500/10 border border-blue-500/20 px-3 py-1.5 rounded text-xs font-medium transition-colors">
                    Read
                  </button>
                </div>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
