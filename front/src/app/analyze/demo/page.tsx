"use client";
// src/app/some-page/page.js

import LegalDocumentViewer from "@/components/LegalDocumentViewer";

// --- DATA DEFINITION ---
// This data can come from an API, a database, or be defined statically here.
const highlightData = [
  {
    id: "gdpr-clause",
    page: 1,
    rect: { x: 100, y: 420, width: 350, height: 32 },
    color: "yellow",
    metadata: {
      shortTitle: "GDPR Clause",
      title: "GDPR Violation Risk",
      explanation:
        "This clause requires processing personal data without explicit consent. Under GDPR, consent must be freely given, specific, informed, and unambiguous. Immediate review recommended.",
    },
  },
  {
    id: "consent-clause",
    page: 2,
    rect: { x: 100, y: 500, width: 300, height: 28 },
    color: "red",
    metadata: {
      shortTitle: "Consent Clause",
      title: "Invalid Consent Mechanism",
      explanation:
        "Pre-ticked boxes do not constitute valid consent under GDPR Article 7(1). This requires immediate amendment to comply with explicit opt-in requirements.",
    },
  },
  {
    id: "liability-clause",
    page: 3,
    rect: { x: 100, y: 320, width: 400, height: 35 },
    color: "blue",
    metadata: {
      shortTitle: "Liability",
      title: "Liability Limitation Clause",
      explanation:
        "This limitation of liability clause is fairly standard but consider if the liability cap amount is adequate for your business needs and risk profile.",
    },
  },
];

const DOCUMENT_INFO_DATA = {
  name: "Anthropic Terms of Service",
  date: "June 15, 2023",
};

const pageContent = {
  1: (
    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
      <h3 className="font-bold text-green-800 mb-2">Welcome to Page 1!</h3>
      <p className="text-green-700 mb-3">
        This page contains the introduction and overview.
      </p>
      <button className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
        Learn More
      </button>
    </div>
  ),
  2: (
    <div className="space-y-4">
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <h3 className="font-bold text-red-800">⚠️ Important Notice</h3>
        <p className="text-red-700">
          This section requires immediate attention.
        </p>
      </div>
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-semibold text-blue-800 mb-2">Quick Actions:</h4>
        <div className="flex gap-2">
          <button className="bg-blue-600 text-white px-3 py-1 rounded text-sm">
            Review
          </button>
          <button className="bg-white border border-blue-600 text-blue-600 px-3 py-1 rounded text-sm">
            Edit
          </button>
        </div>
      </div>
    </div>
  ),
  3: (
    <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
      <h3 className="font-bold text-purple-800 mb-3">Resources</h3>
      <div className="space-y-2">
        <a
          href="#"
          className="block text-purple-700 hover:text-purple-900 underline"
        >
          📄 Download Template
        </a>
        <a
          href="#"
          className="block text-purple-700 hover:text-purple-900 underline"
        >
          🔗 External Reference
        </a>
        <img
          src="/your-image.jpg"
          alt="Example"
          className="w-full h-32 object-cover rounded mt-3"
        />
      </div>
    </div>
  ),
};

// NEW: Define the content that should appear for specific pages.
const PAGE_INSIGHTS_DATA = [
  {
    page: 1,
    content: (
      <div className="space-y-4 text-center pt-12">
        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          {/* Icon */}
        </div>
        <h3 className="text-xl font-bold text-gray-800">
          Title Page & Introduction
        </h3>
        <p className="text-gray-600 max-w-md mx-auto">
          This is the first page of the document, outlining the main parties
          involved and the effective date of the agreement.
        </p>
      </div>
    ),
  },
  {
    page: 3,
    content: (
      <div className="space-y-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="text-lg font-semibold text-blue-900">
          Key Considerations for Page 3
        </h3>
        <p className="text-blue-800">
          This page contains the main "Limitation of Liability" clause. It's a
          standard clause, but pay close attention to the specified liability
          cap to ensure it aligns with your risk tolerance.
        </p>
      </div>
    ),
  },
];

export default function DocumentReviewPage() {
  return (
    <main>
      <LegalDocumentViewer
        fileUrl="/anthropic.pdf"
        highlights={highlightData}
        documentInfo={DOCUMENT_INFO_DATA}
        pageContent={pageContent} // Pass the new prop here
        title="Anthropic ToS Review"
        subtitle="AI-powered analysis of terms and conditions"
      />
    </main>
  );
}
