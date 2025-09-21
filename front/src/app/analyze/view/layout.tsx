"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { FileText, BarChart3, MessageCircle } from "lucide-react";

export default function Layout({ children }: { children: React.ReactNode }) {
  const searchParams = useSearchParams();
  const id = searchParams.get("id");
  const view = searchParams.get("view") || "file";

  return (
    <div className="relative min-h-screen">
      {children}
      <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2 bg-white/10 backdrop-blur-xl rounded-full px-6 py-3 shadow-xl border border-white/20">
        <div className="flex space-x-8">
          <Link
            href={`/analyze/view?id=${id}&view=file`}
            className={`flex items-center space-x-2 px-4 py-2 rounded-full transition-all duration-300 ${
              view === "file"
                ? "bg-white/40 text-black shadow-md"
                : "text-gray-600 hover:bg-white/20 hover:text-gray-800"
            }`}
          >
            <FileText size={20} />
            <span>File</span>
          </Link>
          <Link
            href={`/analyze/view?id=${id}&view=graph`}
            className={`flex items-center space-x-2 px-4 py-2 rounded-full transition-all duration-300 ${
              view === "graph"
                ? "bg-white/40 text-black shadow-md"
                : "text-gray-600 hover:bg-white/20 hover:text-gray-800"
            }`}
          >
            <BarChart3 size={20} />
            <span>Graph</span>
          </Link>
          <Link
            href={`/analyze/view?id=${id}&view=chat`}
            className={`flex items-center space-x-2 px-4 py-2 rounded-full transition-all duration-300 ${
              view === "chat"
                ? "bg-white/40 text-black shadow-md"
                : "text-gray-600 hover:bg-white/20 hover:text-gray-800"
            }`}
          >
            <MessageCircle size={20} />
            <span>Chat</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
