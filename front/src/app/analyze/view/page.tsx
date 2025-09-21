"use client";

import { useSearchParams } from "next/navigation";
import AnalysisViewPage from "./components/FileView";
import ChatView from "./components/ChatView";
import GraphView from "./components/GraphView";

export default function ViewPage() {
  const searchParams = useSearchParams();
  const view = searchParams.get("view") || "file";

  switch (view) {
    case "chat":
      return <ChatView />;
    case "graph":
      return <GraphView />;
    case "file":
    default:
      return <AnalysisViewPage />;
  }
}
