"use client";

import { useState, useRef } from "react";
import { UploadCloud, FileType, CheckCircle } from "lucide-react";
import { useSession } from "@/lib/session-context";

export function DatasetUpload() {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const { isExecuting, createAndUpload } = useSession();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelection(e.target.files[0]);
    }
  };

  const handleFileSelection = (selectedFile: File) => {
    // Only warn if they upload a file that might genuinely be unsupported,
    // though the backend accepts a wide range of LOM files (.json, .log, .yaml, .txt, .csv, ...)
    const ext = selectedFile.name.split(".").pop()?.toLowerCase();
    const validExts = [
      "csv",
      "json",
      "log",
      "txt",
      "py",
      "js",
      "ts",
      "yaml",
      "yml",
    ];

    if (!ext || !validExts.includes(ext)) {
      alert("Please upload a supported file (.csv, .json, .log, etc).");
      return;
    }
    setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!file) return;
    await createAndUpload(file);
  };

  return (
    <div className="w-full max-w-4xl mx-auto mt-10">
      <div
        className={`border-2 border-dashed rounded-2xl p-12 transition-all duration-300 flex flex-col items-center justify-center text-center ${
          isDragging
            ? "border-white/20 bg-white/[0.04]"
            : file
              ? "border-green-500/40 bg-green-900/5"
              : "border-white/[0.06] hover:border-white/20 hover:bg-white/[0.02]"
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          type="file"
          accept=".csv,.json,.log,.txt,.yaml,.yml,.py,.js,.ts"
          className="hidden"
          ref={fileInputRef}
          onChange={handleFileInput}
        />

        {!file ? (
          <>
            <div className="w-20 h-20 rounded-full bg-[#0A0A0A] flex items-center justify-center mb-6 border border-white/[0.06]">
              <UploadCloud className="w-10 h-10 text-white/40" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-2">
              Upload your dataset
            </h3>
            <p className="text-white/40 max-w-md mx-auto mb-8">
              Drag and drop your CSV or LOM text/log files here, or click the
              button below to browse.
            </p>
            <button
              suppressHydrationWarning
              onClick={() => fileInputRef.current?.click()}
              className="px-6 py-3 rounded-lg bg-[#0A0A0A] border border-white/[0.06] text-white hover:bg-white/[0.06] transition-all focus:outline-none"
            >
              Select File
            </button>
          </>
        ) : (
          <>
            <div className="w-20 h-20 rounded-full bg-green-900/20 flex items-center justify-center mb-6 border border-green-500/30">
              <FileType className="w-10 h-10 text-green-400" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-2">{file.name}</h3>
            <p className="text-white/40 mb-8">
              {(file.size / 1024).toFixed(2)} KB
            </p>

            <div className="flex gap-4">
              <button
                suppressHydrationWarning
                onClick={() => setFile(null)}
                className="px-6 py-3 rounded-lg border border-red-500/30 text-red-400 hover:bg-red-900/20 transition-all focus:outline-none"
                disabled={isExecuting}
              >
                Remove
              </button>
              <button
                suppressHydrationWarning
                onClick={handleUpload}
                disabled={isExecuting}
                className="px-8 py-3 rounded-lg bg-[#3B82F6] hover:bg-[#2563EB] text-white font-bold transition-all focus:outline-none disabled:opacity-70 flex items-center gap-2"
              >
                {isExecuting ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-5 h-5" />
                    Confirm & Start EVA
                  </>
                )}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
