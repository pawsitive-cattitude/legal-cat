// src/components/LegalDocumentViewer.js

"use client";

import { Viewer, SpecialZoomLevel } from "@react-pdf-viewer/core";
import { defaultLayoutPlugin } from "@react-pdf-viewer/default-layout";
import "@react-pdf-viewer/core/lib/styles/index.css";
import "@react-pdf-viewer/default-layout/lib/styles/index.css";
import { useEffect, useRef, useState } from "react";
import { usePathname, useSearchParams, useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";

// --- IMPORTANT SETUP ---
import * as pdfjs from 'pdfjs-dist';
pdfjs.GlobalWorkerOptions.workerSrc = "/pdf.worker.min.js";
// --- END SETUP ---

// NEW: Default props for titles and info
const defaultDocumentInfo = {
  name: "Untitled Document",
  date: "N/A"
};

export default function LegalDocumentViewer({
  fileUrl,
  highlights = [], // CHANGED: Accept highlights as a prop, default to empty array
  documentInfo = defaultDocumentInfo, // CHANGED: Accept document info as a prop
  title = "Document Analysis", // CHANGED: Accept title as a prop
  subtitle = "Legal analysis powered by AI" // CHANGED: Accept subtitle as a prop
}) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const viewerRef = useRef(null);
  const [activeHighlight, setActiveHighlight] = useState(null);
  const [isViewerReady, setIsViewerReady] = useState(false);

  // Initialize the default layout plugin (with toolbar hidden)
  const defaultLayoutPluginInstance = defaultLayoutPlugin({
    sidebarTabs: () => [],
    renderToolbar: () => <></>,
    toolbarPlugin: {
      download: { enableShortcuts: false },
      enterFullScreen: { enableShortcuts: false },
      print: { enableShortcuts: false },
      sidebar: { enableShortcuts: false },
      zoom: { enableShortcuts: false }
    }
  });

  // This function is for user-initiated clicks.
  const handleHighlightClick = (highlight) => {
    if (!viewerRef.current || !highlight) return;
    
    setActiveHighlight(highlight.id);

    const params = new URLSearchParams(searchParams.toString());
    params.set('highlight', highlight.id);
    router.replace(`${pathname}?${params.toString()}`);

    viewerRef.current.scrollPageIntoView({
      pageIndex: highlight.page - 1,
      bottomOffset: highlight.rect.y + highlight.rect.height + 50
    });
  };

  // This useEffect hook handles the INITIAL page load based on URL param.
  useEffect(() => {
    if (isViewerReady) {
      const highlightIdFromUrl = searchParams.get("highlight");
      if (highlightIdFromUrl) {
        // CHANGED: Use the 'highlights' prop
        const highlight = highlights.find(h => h.id === highlightIdFromUrl);
        if (highlight) {
          handleHighlightClick(highlight);
        }
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isViewerReady, highlights]); // Depend on highlights prop


  // Custom renderer to add the highlight overlays on each page
  const renderPage = (props) => {
    return (
      <div style={{ position: 'relative', width: '100%', height: '100%' }}>
        {props.canvasLayer.children}
        <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}>
          {/* CHANGED: Use the 'highlights' prop */}
          {highlights
            .filter(h => h.page === props.pageIndex + 1)
            .map((highlight) => {
              const isActive = activeHighlight === highlight.id;
              const colorMap = {
                  red: { bg: 'rgba(239, 68, 68, 0.2)', border: '#ef4444' },
                  blue: { bg: 'rgba(59, 130, 246, 0.2)', border: '#3b82f6' },
                  yellow: { bg: 'rgba(234, 179, 8, 0.25)', border: '#eab308' },
              };
              const { bg, border } = colorMap[highlight.color] || colorMap.yellow;

              return (
                <div
                  key={highlight.id}
                  className="absolute rounded cursor-pointer transition-all duration-200"
                  style={{
                    left: `${highlight.rect.x}px`,
                    top: `${highlight.rect.y}px`,
                    width: `${highlight.rect.width}px`,
                    height: `${highlight.rect.height}px`,
                    backgroundColor: bg,
                    border: isActive ? `2px solid ${border}` : 'none',
                    boxShadow: isActive ? `0 0 5px ${border}` : 'none',
                  }}
                  onClick={() => handleHighlightClick(highlight)}
                />
              );
            })
          }
        </div>
        {props.textLayer.children}
        {props.annotationLayer.children}
      </div>
    );
  };

  // CHANGED: Use the 'highlights' prop
  const selectedHighlight = highlights.find(h => h.id === activeHighlight);

  // NEW: Helper for dynamic button styling
  const getButtonClass = (color) => {
    const colorStyles = {
        red: "bg-red-100 text-red-800 hover:bg-red-200",
        blue: "bg-blue-100 text-blue-800 hover:bg-blue-200",
        yellow: "bg-amber-100 text-amber-800 hover:bg-amber-200",
    };
    return colorStyles[color] || colorStyles.yellow;
  };

  return (
    <div className="flex h-screen bg-gray-100 font-sans">
      {/* LEFT PANEL - PDF VIEWER */}
      <div className="w-1/2 flex flex-col bg-gray-50">
        <div className="p-3 border-b border-gray-200 bg-white flex justify-between items-center">
          <div className="text-sm text-gray-500">
            {/* CHANGED: Use 'title' prop */}
            {title}
          </div>
          {/* CHANGED: Buttons are now dynamically generated */}
          <div className="flex gap-2">
            {highlights.map(highlight => (
                <button
                    key={highlight.id}
                    onClick={() => handleHighlightClick(highlight)}
                    className={`px-3 py-1.5 text-sm rounded-md transition-colors ${getButtonClass(highlight.color)}`}
                >
                    {/* Assuming a short title exists, otherwise use the main one */}
                    {highlight.metadata.shortTitle || highlight.metadata.title}
                </button>
            ))}
          </div>
        </div>
        
        <div className="flex-1 relative overflow-auto">
          {!isViewerReady && (
            <div className="absolute inset-0 bg-white/80 flex items-center justify-center z-10">
              <div className="text-gray-600">Loading document...</div>
            </div>
          )}
          <div className="flex justify-center py-4">
            <div style={{ width: '100%', maxWidth: '800px' }}>
              <Viewer
                // CHANGED: Use 'fileUrl' prop
                fileUrl={fileUrl}
                plugins={[defaultLayoutPluginInstance]}
                defaultScale={SpecialZoomLevel.PageWidth}
                renderPage={renderPage}
                onDocumentLoad={() => setIsViewerReady(true)}
                viewRef={viewerRef}
                theme={{
                  theme: 'light',
                  styles: {
                    viewer: { backgroundColor: '#f8fafc' },
                    page: {
                      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
                      marginBottom: '1.5rem',
                      borderRadius: '4px',
                      overflow: 'hidden',
                    },
                    '.rpv-core__inner-pages': { justifyContent: 'center' }
                  },
                }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* RIGHT PANEL - EXPLANATION */}
      <div className="w-1/2 bg-white flex flex-col">
        <div className="p-4 border-b border-gray-200 bg-gray-50">
            {/* CHANGED: Use props for title and subtitle */}
            <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
        </div>
        
        <div className="flex-1 overflow-y-auto p-6">
          <AnimatePresence mode="wait">
            {!selectedHighlight ? (
              <motion.div
                key="initial"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="text-center text-gray-500 pt-16"
              >
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-1">Select a clause</h3>
                <p className="text-gray-500 max-w-sm mx-auto">
                  Click on any highlighted section in the document to view detailed legal analysis
                </p>
              </motion.div>
            ) : (
              <motion.div
                key={selectedHighlight.id}
                initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }} className="space-y-4"
              >
                {/* Risk Banner */}
                <div className={`p-3 rounded-lg border ${
                  selectedHighlight.color === 'red' ? 'bg-red-50 border-red-200'
                  : selectedHighlight.color === 'blue' ? 'bg-blue-50 border-blue-200'
                  : 'bg-amber-50 border-amber-200'
                }`}>
                  <div className="flex items-start">
                    <div className={`mt-0.5 w-2 h-2 rounded-full ${
                      selectedHighlight.color === 'red' ? 'bg-red-500'
                      : selectedHighlight.color === 'blue' ? 'bg-blue-500' : 'bg-amber-500'
                    }`} />
                    <div className="ml-3">
                      <h3 className="font-semibold text-gray-900">{selectedHighlight.metadata.title}</h3>
                    </div>
                  </div>
                </div>
                
                {/* Explanation Content */}
                <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                  {selectedHighlight.metadata.explanation}
                </div>
                
                {/* AI Assistant Section */}
                <div className="mt-6">
                  <div className="flex items-center mb-3">
                    <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-indigo-600" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M18 8a6 6 0 01-7.743 5.743L10 14l-1 1-1 1H6v2H2v-4l4.257-4.257A6 6 0 1118 8zm-10 4-2 2v-1h-1v-2h1V8h2v1h1v2h-1v1z" clipRule="evenodd" />
                        </svg>
                    </div>
                    <h4 className="ml-2 font-medium text-gray-900">AI Legal Assistant</h4>
                  </div>
                  <div className="bg-indigo-50 border border-indigo-100 rounded-lg p-4">
                    <p className="text-indigo-800 text-sm">
                      This clause requires immediate attention. I recommend requesting 
                      an amendment to align with GDPR requirements. Would you like me to 
                      draft a suggested revision?
                    </p>
                    <div className="mt-3 flex gap-2">
                      <button className="px-3 py-1.5 bg-white border border-indigo-200 text-indigo-700 text-sm rounded hover:bg-indigo-50 transition-colors">
                        Draft revision
                      </button>
                      <button className="px-3 py-1.5 bg-indigo-600 text-white text-sm rounded hover:bg-indigo-700 transition-colors">
                        Request human review
                      </button>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
        
        {/* Footer with document info */}
        <div className="border-t border-gray-200 p-3 bg-gray-50">
          <div className="flex items-center justify-between text-sm">
            {/* CHANGED: Use 'documentInfo' prop */}
            <div className="text-gray-500">Document: {documentInfo.name}</div>
            <div className="flex items-center text-gray-500">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span>Updated: {documentInfo.date}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}