"use client";

import React, { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import LegalDocumentViewer from "@/components/LegalDocumentViewer";
import {
  createHighlightContent,
  HighlightTypes,
} from "@/components/HighlightComponents";
import {
  createPageContent,
  PageContentTypes,
} from "@/components/PageContentComponents";
import { AnalysisAPI } from "@/services/analysisAPI";
import { AnalysisResponse, Highlight, PageContent } from "@/types/analysis";

export default function AnalysisViewPage() {
  const searchParams = useSearchParams();
  const analysisId = searchParams.get("id");

  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!analysisId) {
      setError("No analysis ID provided");
      setLoading(false);
      return;
    }

    const fetchAnalysis = async () => {
      try {
        const analysisData = await AnalysisAPI.getAnalysis(analysisId);
        setAnalysis(analysisData);
      } catch (err) {
        console.error("Failed to fetch analysis:", err);
        setError(
          err instanceof Error ? err.message : "Failed to load analysis"
        );
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysis();
  }, [analysisId]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-700">
            Loading Analysis...
          </h2>
          <p className="text-gray-500 mt-2">Processing your document with AI</p>
        </div>
      </div>
    );
  }

  if (error || !analysis || !analysisId) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md mx-auto">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            Analysis Error
          </h2>
          <p className="text-gray-600 mb-6">
            {error ||
              "Unable to load the analysis. Please try uploading your document again."}
          </p>
          <a
            href="/analyze"
            className="bg-gray-800 text-white px-6 py-3 rounded hover:bg-gray-700 transition-colors"
          >
            Upload New Document
          </a>
        </div>
      </div>
    );
  }

  // Process highlights - convert LLM data to rendered components
  const processedHighlights = analysis.highlights.map(
    (highlight: Highlight) => ({
      ...highlight,
      metadata: {
        ...highlight.metadata,
        explanation: createHighlightContent(
          highlight.metadata.type,
          highlight.metadata.data
        ),
      },
    })
  );

  // Process page content - convert LLM data to rendered components
  const processedPageContent: { [key: number]: React.ReactNode } = {};
  Object.entries(analysis.pageContent).forEach(
    ([pageNum, content]: [string, PageContent]) => {
      const pageNumber = parseInt(pageNum);
      processedPageContent[pageNumber] = createPageContent(
        content.type,
        content.data
      );
    }
  );

  // Get PDF URL
  const pdfUrl = AnalysisAPI.getPdfUrl(analysisId);

  return (
    <main className="h-screen">
      <LegalDocumentViewer
        fileUrl={pdfUrl}
        highlights={processedHighlights}
        documentInfo={analysis.documentInfo}
        pageContent={processedPageContent}
        title={`Analysis: ${analysis.documentInfo.name}`}
        subtitle="AI-powered legal document analysis"
      />
    </main>
  );
}
