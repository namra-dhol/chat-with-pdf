/**
 * app/page.tsx
 * ------------
 * Upload Page — Landing page where users upload their PDF.
 */

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { FileUpload } from "@/components/FileUpload";
import { UploadResponse } from "@/services/api";

export default function UploadPage() {
  const router = useRouter();
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);

  const handleUploadSuccess = (data: UploadResponse) => {
    setUploadResult(data);
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-950 via-[#0f0a2e] to-gray-950 flex flex-col items-center justify-center px-4 py-12">
      {/* Background glow */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-violet-600/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 left-1/3 w-[400px] h-[400px] bg-purple-800/10 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 w-full max-w-2xl flex flex-col items-center">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-400 text-xs font-medium mb-6 backdrop-blur-sm">
            <span className="w-2 h-2 rounded-full bg-violet-400 animate-pulse" />
            Powered by sentence-transformers + Ollama
          </div>

          <h1 className="text-5xl font-bold text-white mb-3 tracking-tight">
            Chat with your{" "}
            <span className="bg-gradient-to-r from-violet-400 to-purple-400 bg-clip-text text-transparent">
              PDF
            </span>
          </h1>
          <p className="text-gray-400 text-lg">
            Upload a document and get instant AI-powered answers from its content.
          </p>
        </div>

        {/* Upload or Success State */}
        {uploadResult ? (
          <div className="w-full max-w-xl">
            {/* Success Card */}
            <div className="rounded-2xl bg-emerald-500/10 border border-emerald-500/30 p-8 text-center mb-6">
              <div className="w-16 h-16 rounded-2xl bg-emerald-500/20 flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-white mb-1">PDF Processed!</h2>
              <p className="text-emerald-400 font-medium text-sm mb-1">{uploadResult.filename}</p>
              <p className="text-gray-400 text-sm">
                {uploadResult.chunks_count} text chunks embedded and ready for search.
              </p>
            </div>

            <div className="flex flex-col gap-3">
              <button
                onClick={() => router.push("/chat")}
                className="w-full py-4 rounded-xl bg-gradient-to-r from-violet-600 to-purple-700 hover:from-violet-500 hover:to-purple-600 text-white font-semibold text-lg transition-all duration-200 shadow-lg shadow-violet-900/40 hover:shadow-violet-900/60 hover:-translate-y-0.5"
              >
                Start Chatting →
              </button>
              <button
                onClick={() => setUploadResult(null)}
                className="w-full py-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-gray-300 text-sm transition-all duration-200"
              >
                Upload a different PDF
              </button>
            </div>
          </div>
        ) : (
          <div className="w-full">
            <FileUpload onSuccess={handleUploadSuccess} />

            {/* Feature pills */}
            <div className="flex flex-wrap justify-center gap-2 mt-8">
              {[
                "🔒 Processed Locally",
                "⚡ Fast Semantic Search",
                "🧠 LLM-Powered Answers",
                "📦 Stored in .pkl File",
              ].map((feat) => (
                <span
                  key={feat}
                  className="px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-gray-400 text-xs"
                >
                  {feat}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
