// EXAMPLE: What the LLM needs to generate instead of complex JSX

// ❌ BEFORE: LLM had to generate complex JSX structures like this:
/*
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
  )
};
*/

// ✅ NOW: LLM only generates simple structured data:

export const exampleLLMOutput = {
  // For highlights - just specify type and simple data
  highlights: [
    {
      id: "clause-1",
      page: 1,
      rect: { x: 100, y: 420, width: 350, height: 32 },
      color: "red",
      metadata: {
        shortTitle: "Privacy Issue",
        title: "Data Collection Without Consent",
        type: "legal_risk", // Just specify the type!
        data: {
          title: "Data Collection Without Consent",
          explanation:
            "This clause allows data collection without explicit user consent.",
          severity: "high",
          article: "GDPR Art. 6(1)(a)",
          recommendation:
            "Add explicit consent mechanism before data collection.",
        },
      },
    },
  ],

  // For page content - just specify type and data
  pageContent: {
    1: {
      type: "intro", // Just specify the type!
      data: {
        title: "Document Analysis Started",
        description:
          "We've identified several key areas that need your attention.",
        buttonText: "Begin Review",
      },
    },
    2: {
      type: "notice", // Just specify the type!
      data: {
        title: "Critical Issues Found",
        message: "This page contains 3 high-priority compliance issues.",
        severity: "error",
        actions: [
          { label: "View Issues", primary: true },
          { label: "Export Report", primary: false },
        ],
      },
    },
    3: {
      type: "key_points", // Just specify the type!
      data: {
        title: "Key Terms Summary",
        theme: "blue",
        points: [
          "Liability cap set at $100,000",
          "Termination clause allows 30-day notice",
          "Data retention period is 2 years",
          "Jurisdiction is Delaware courts",
        ],
      },
    },
  },
};

// Available types for LLM to choose from:

export const availableHighlightTypes = [
  "legal_risk", // For legal violations/risks
  "compliance_issue", // For regulatory compliance problems
  "standard_clause", // For standard but notable clauses
  "custom", // For simple custom explanations
];

export const availablePageContentTypes = [
  "intro", // Welcome/introduction sections
  "notice", // Alerts/warnings/important notices
  "resources", // Links, downloads, references
  "key_points", // Bullet point summaries
  "summary", // Multi-section summaries
  "custom", // Simple custom content
];

// Benefits of this approach:
// 1. LLM generates 90% less code
// 2. Consistent styling across all content
// 3. Easy to maintain and update designs
// 4. Type-safe and structured
// 5. Reusable components mean faster rendering
// 6. LLM can focus on content, not UI implementation
