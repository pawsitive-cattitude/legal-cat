// Reusable highlight explanation components

export const HighlightTypes = {
  LEGAL_RISK: "legal_risk",
  COMPLIANCE_ISSUE: "compliance_issue",
  STANDARD_CLAUSE: "standard_clause",
  IMPORTANT_TERM: "important_term",
  CUSTOM: "custom",
};

// Simple text explanation
export function SimpleHighlight({ title, explanation, severity = "medium" }) {
  return (
    <div className="space-y-3">
      <p className="font-medium text-gray-900">{title}</p>
      <p className="text-gray-700">{explanation}</p>
    </div>
  );
}

// Legal risk highlight with severity indicator
export function LegalRiskHighlight({
  title,
  explanation,
  severity = "high",
  article,
  recommendation,
}) {
  const severityStyles = {
    low: "bg-blue-50 border-blue-200 text-blue-800",
    medium: "bg-yellow-50 border-yellow-200 text-yellow-800",
    high: "bg-red-50 border-red-200 text-red-800",
  };

  return (
    <div className="space-y-3">
      <div className={`p-3 rounded-lg border ${severityStyles[severity]}`}>
        <p className="font-medium">{title}</p>
        {article && <p className="text-sm opacity-80">Violates: {article}</p>}
      </div>
      <p className="text-gray-700">{explanation}</p>
      {recommendation && (
        <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
          <p className="text-sm text-gray-700">
            <span className="font-medium">Recommendation:</span>{" "}
            {recommendation}
          </p>
        </div>
      )}
    </div>
  );
}

// Compliance issue highlight
export function ComplianceHighlight({
  title,
  explanation,
  regulation,
  urgency = "medium",
}) {
  const urgencyStyles = {
    low: "bg-green-100 text-green-800",
    medium: "bg-yellow-100 text-yellow-800",
    high: "bg-red-100 text-red-800",
  };

  return (
    <div className="space-y-3">
      <div className="flex items-start gap-3">
        <div
          className={`px-2 py-1 rounded text-xs font-medium ${urgencyStyles[urgency]}`}
        >
          {urgency.toUpperCase()}
        </div>
        <div>
          <p className="font-medium text-gray-900">{title}</p>
          {regulation && (
            <p className="text-sm text-gray-600">Under {regulation}</p>
          )}
        </div>
      </div>
      <p className="text-gray-700">{explanation}</p>
    </div>
  );
}

// Standard clause highlight
export function StandardClauseHighlight({
  title,
  explanation,
  isNegotiable = false,
  tips = [],
}) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <p className="font-medium text-gray-900">{title}</p>
        {isNegotiable && (
          <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
            Negotiable
          </span>
        )}
      </div>
      <p className="text-gray-700">{explanation}</p>
      {tips.length > 0 && (
        <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
          <p className="text-sm font-medium text-blue-900 mb-2">💡 Tips:</p>
          <ul className="text-sm text-blue-800 space-y-1">
            {tips.map((tip, index) => (
              <li key={index}>• {tip}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

// Factory function to create highlight content based on type
export function createHighlightContent(type, data) {
  switch (type) {
    case HighlightTypes.LEGAL_RISK:
      return <LegalRiskHighlight {...data} />;
    case HighlightTypes.COMPLIANCE_ISSUE:
      return <ComplianceHighlight {...data} />;
    case HighlightTypes.STANDARD_CLAUSE:
      return <StandardClauseHighlight {...data} />;
    case HighlightTypes.CUSTOM:
      return <SimpleHighlight {...data} />;
    default:
      return <SimpleHighlight {...data} />;
  }
}
