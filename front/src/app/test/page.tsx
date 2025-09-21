"use client";

import LegalDocumentViewer from "@/components/LegalDocumentViewer";
import {
  createHighlightContent,
  HighlightTypes,
} from "@/components/HighlightComponents";
import {
  createPageContent,
  PageContentTypes,
} from "@/components/PageContentComponents";

// --- SIMPLE DATA FROM LLM ---
// The LLM only needs to generate this structured data, not JSX!

const highlightData = [
  {
    id: "gdpr-clause",
    page: 1,
    rect: { x: 100, y: 420, width: 350, height: 32 },
    color: "yellow",
    metadata: {
      shortTitle: "GDPR Clause",
      title: "GDPR Violation Risk",
      type: HighlightTypes.LEGAL_RISK,
      data: {
        title: "GDPR Violation Risk",
        explanation:
          "This clause requires processing personal data without explicit consent.",
        severity: "high",
        article: "GDPR Art. 5(1)(a)",
        recommendation:
          "Revise to require explicit consent before processing any personal data.",
      },
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
      type: HighlightTypes.COMPLIANCE_ISSUE,
      data: {
        title: "Invalid Consent Mechanism",
        explanation: "Pre-ticked boxes do not constitute valid consent.",
        regulation: "GDPR Article 7(1)",
        urgency: "high",
      },
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
      type: HighlightTypes.STANDARD_CLAUSE,
      data: {
        title: "Liability Limitation Clause",
        explanation: "This limitation of liability clause is fairly standard.",
        isNegotiable: true,
        tips: [
          "Consider if the liability cap amount is adequate",
          "Review coverage for data breaches specifically",
          "Ensure mutual limitation applies to both parties",
        ],
      },
    },
  },
];

// Convert the simple data to rendered components
const processedHighlights = highlightData.map((highlight) => ({
  ...highlight,
  metadata: {
    ...highlight.metadata,
    explanation: createHighlightContent(
      highlight.metadata.type,
      highlight.metadata.data
    ),
  },
}));

const DOCUMENT_INFO_DATA = {
  name: "Anthropic Terms of Service",
  date: "June 15, 2023",
};

// --- SIMPLE PAGE CONTENT DATA ---
// Again, LLM just generates this structured data:

const pageContentData: { [key: number]: { type: string; data: any } } = {
  1: {
    type: PageContentTypes.INTRO,
    data: {
      title: "Welcome to Document Analysis",
      description:
        "This page contains the introduction and overview of the legal document.",
      buttonText: "Start Analysis",
      onButtonClick: () => console.log("Analysis started!"),
    },
  },
  2: {
    type: PageContentTypes.NOTICE,
    data: {
      title: "Critical Issues Found",
      message:
        "This section contains clauses that require immediate attention.",
      severity: "error",
      actions: [
        {
          label: "Review Issues",
          primary: true,
          onClick: () => console.log("Reviewing..."),
        },
        {
          label: "Export Report",
          primary: false,
          onClick: () => console.log("Exporting..."),
        },
      ],
    },
  },
  3: {
    type: PageContentTypes.KEY_POINTS,
    data: {
      title: "Key Considerations for Page 3",
      theme: "blue",
      points: [
        "Contains the main Limitation of Liability clause",
        "Standard clause but liability cap should be reviewed",
        "Consider negotiating mutual limitations",
        "Ensure adequate coverage for your risk profile",
      ],
    },
  },
};

// Convert to rendered components
const pageContent: { [key: number]: React.ReactNode } = {};
Object.keys(pageContentData).forEach((pageNum) => {
  const pageNumber = parseInt(pageNum);
  const { type, data } = pageContentData[pageNumber];
  pageContent[pageNumber] = createPageContent(type, data);
});

export default function DocumentReviewPage() {
  return (
    <main>
      <LegalDocumentViewer
        fileUrl="/anthropic.pdf"
        highlights={processedHighlights}
        documentInfo={DOCUMENT_INFO_DATA}
        pageContent={pageContent}
        title="Anthropic ToS Review"
        subtitle="AI-powered analysis of terms and conditions"
      />
    </main>
  );
}
