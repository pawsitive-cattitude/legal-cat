// src/components/LegalDocumentViewer.js

"use client";

import { Viewer, SpecialZoomLevel } from "@react-pdf-viewer/core";
import { defaultLayoutPlugin } from "@react-pdf-viewer/default-layout";
import "@react-pdf-viewer/core/lib/styles/index.css";
import "@react-pdf-viewer/default-layout/lib/styles/index.css";
import { useEffect, useRef, useState } from "react";
import { usePathname, useSearchParams, useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";

import * as pdfjs from 'pdfjs-dist';
pdfjs.GlobalWorkerOptions.workerSrc = "/pdf.worker.min.js";

const defaultDocumentInfo = {
  name: "Untitled Document",
  date: "N/A"
};

export default function LegalDocumentViewer({
  fileUrl,
  highlights = [],
  pageInsights = [], // NEW: Accept page-specific insights as a prop
  documentInfo = defaultDocumentInfo,
  title = "Document Analysis",
  subtitle = "Legal analysis powered by AI"
}) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const viewerRef = useRef(null);
  const [activeHighlight, setActiveHighlight] = useState(null);
  const [isViewerReady, setIsViewerReady] = useState(false);
  const [currentPageIndex, setCurrentPageIndex] = useState(0); // NEW: State to track current page

  const defaultLayoutPluginInstance = defaultLayoutPlugin({
    sidebarTabs: () => [],
    renderToolbar: () => <></>,
    toolbarPlugin: { /* ... */ }
  });

  const handleHighlightClick = (highlight) => { /* ... (no changes here) ... */ };

  useEffect(() => { /* ... (no changes here) ... */ }, [isViewerReady, highlights]);
  
  // NEW: Handler for when the user scrolls to a new page
  const handlePageChange = (e) => {
    setCurrentPageIndex(e.currentPage);
  };

  const renderPage = (props) => { /* ... (no changes here) ... */ };
  
  const selectedHighlight = highlights.find(h => h.id === activeHighlight);
  
  // NEW: Find the insight for the current page
  const currentPageInsight = pageInsights.find(
    (insight) => insight.page === currentPageIndex + 1
  );

  const getButtonClass = (color) => { /* ... (no changes here) ... */ };

  return (
    <div className="flex h-screen bg-gray-100 font-sans">
      {/* LEFT PANEL - PDF VIEWER */}
      <div className="w-1/2 flex flex-col bg-gray-50">
        {/* ... (Header is unchanged) ... */}
        <div className="flex-1 relative overflow-auto">
          {/* ... (Loading state is unchanged) ... */}
          <div className="flex justify-center py-4">
            <div style={{ width: '100%', maxWidth: '800px' }}>
              <Viewer
                fileUrl={fileUrl}
                plugins={[defaultLayoutPluginInstance]}
                defaultScale={SpecialZoomLevel.PageWidth}
                renderPage={renderPage}
                onDocumentLoad={() => setIsViewerReady(true)}
                viewRef={viewerRef}
                onPageChange={handlePageChange} // NEW: Attach the page change handler
                theme={{ /* ... */ }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* RIGHT PANEL - EXPLANATION */}
      <div className="w-1/2 bg-white flex flex-col">
        {/* ... (Header is unchanged) ... */}
        <div className="flex-1 overflow-y-auto p-6">
          <AnimatePresence mode="wait">
            {/* CHANGED: Updated logic to show page insights */}
            {!selectedHighlight ? (
              currentPageInsight ? (
                // If there's an insight for the current page, show it
                <motion.div
                  key={`page-${currentPageIndex}`}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.2 }}
                >
                    <div className="flex items-center mb-3">
                        <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 006-6v-1.5m-6 7.5a6 6 0 01-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 01-3-3V4.5a3 3 0 116 0v8.25a3 3 0 01-3 3z" />
                            </svg>
                        </div>
                        <h4 className="ml-2 font-medium text-gray-900">Page Insight</h4>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4 border border-gray-100 text-gray-700">
                      {currentPageInsight.content}
                    </div>
                </motion.div>
              ) : (
                // Otherwise, show the default initial message
                <motion.div
                  key="initial"
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                  className="text-center text-gray-500 pt-16"
                >
                    {/* ... (Default "Select a clause" content) ... */}
                </motion.div>
              )
            ) : (
              // If a highlight IS selected, show its details (existing logic)
              <motion.div
                key={selectedHighlight.id}
                initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}
                className="space-y-4"
              >
                  {/* ... (Existing highlight details content) ... */}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
        {/* ... (Footer is unchanged) ... */}
      </div>
    </div>
  );
}