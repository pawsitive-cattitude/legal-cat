// Reusable page content components

export const PageContentTypes = {
  INTRO: "intro",
  NOTICE: "notice",
  ACTIONS: "actions",
  RESOURCES: "resources",
  KEY_POINTS: "key_points",
  SUMMARY: "summary",
  EXPLANATION: "explanation",
  CUSTOM: "custom",
};

// Introduction/Welcome component
export function IntroPageContent({
  title,
  description,
  buttonText,
  onButtonClick,
}) {
  return (
    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
      <h3 className="font-bold text-green-800 mb-2">{title}</h3>
      <p className="text-green-700 mb-3">{description}</p>
      {buttonText && (
        <button
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          onClick={onButtonClick}
        >
          {buttonText}
        </button>
      )}
    </div>
  );
}

// Notice/Alert component
export function NoticePageContent({
  title,
  message,
  severity = "warning",
  actions = [],
}) {
  const severityStyles = {
    info: "bg-blue-50 border-blue-200 text-blue-800",
    warning: "bg-yellow-50 border-yellow-200 text-yellow-800",
    error: "bg-red-50 border-red-200 text-red-800",
    success: "bg-green-50 border-green-200 text-green-800",
  };

  const icons = {
    info: "ℹ️",
    warning: "⚠️",
    error: "❌",
    success: "✅",
  };

  return (
    <div className="space-y-4">
      <div className={`p-4 rounded-lg border ${severityStyles[severity]}`}>
        <h3 className="font-bold">
          {icons[severity]} {title}
        </h3>
        <p className="mt-2">{message}</p>
      </div>
      {actions.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-semibold text-blue-800 mb-2">Quick Actions:</h4>
          <div className="flex gap-2 flex-wrap">
            {actions.map((action, index) => (
              <button
                key={index}
                className={`px-3 py-1 rounded text-sm transition-colors ${
                  action.primary
                    ? "bg-blue-600 text-white hover:bg-blue-700"
                    : "bg-white border border-blue-600 text-blue-600 hover:bg-blue-50"
                }`}
                onClick={action.onClick}
              >
                {action.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// Resources component
export function ResourcesPageContent({ title, links = [], images = [] }) {
  return (
    <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
      <h3 className="font-bold text-purple-800 mb-3">{title}</h3>
      <div className="space-y-2">
        {links.map((link, index) => (
          <a
            key={index}
            href={link.url}
            className="block text-purple-700 hover:text-purple-900 underline"
            target={link.external ? "_blank" : "_self"}
            rel={link.external ? "noopener noreferrer" : ""}
          >
            {link.icon} {link.label}
          </a>
        ))}
        {images.map((image, index) => (
          <img
            key={index}
            src={image.src}
            alt={image.alt}
            className="w-full h-32 object-cover rounded mt-3"
          />
        ))}
      </div>
    </div>
  );
}

// Key Points summary component
export function KeyPointsPageContent({ title, points = [], theme = "blue" }) {
  const themeStyles = {
    blue: "bg-blue-50 border-blue-200 text-blue-800",
    green: "bg-green-50 border-green-200 text-green-800",
    purple: "bg-purple-50 border-purple-200 text-purple-800",
    gray: "bg-gray-50 border-gray-200 text-gray-800",
  };

  return (
    <div className={`p-4 rounded-lg border ${themeStyles[theme]}`}>
      <h3 className="text-lg font-semibold mb-3">{title}</h3>
      <ul className="space-y-2">
        {points.map((point, index) => (
          <li key={index} className="flex items-start gap-2">
            <span className="text-lg">•</span>
            <span>{point}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

// Summary component with sections
export function SummaryPageContent({ title, sections = [] }) {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-gray-900">{title}</h3>
      {sections.map((section, index) => (
        <div
          key={index}
          className="bg-gray-50 border border-gray-200 rounded-lg p-4"
        >
          <h4 className="font-semibold text-gray-800 mb-2">{section.title}</h4>
          <p className="text-gray-700">{section.content}</p>
          {section.status && (
            <div className="mt-2">
              <span
                className={`px-2 py-1 rounded text-xs font-medium ${
                  section.status === "good"
                    ? "bg-green-100 text-green-800"
                    : section.status === "warning"
                    ? "bg-yellow-100 text-yellow-800"
                    : "bg-red-100 text-red-800"
                }`}
              >
                {section.status.toUpperCase()}
              </span>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// Explanation component with detailed analysis
export function ExplanationPageContent({ title, explanation, points = [] }) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
      <h3 className="font-bold text-gray-900 mb-4 text-lg">{title}</h3>
      <div className="text-gray-700 mb-5 leading-relaxed">
        <p className="text-base">{explanation}</p>
      </div>
      {points && points.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4 border-l-4 border-gray-400">
          <h4 className="font-semibold text-gray-800 mb-3 text-sm uppercase tracking-wide">
            Key Points
          </h4>
          <ul className="space-y-2">
            {points.map((point, index) => (
              <li key={index} className="flex items-start text-gray-700">
                <span className="flex-shrink-0 w-2 h-2 bg-gray-400 rounded-full mt-2 mr-3"></span>
                <span className="text-sm leading-relaxed">{point}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

// Simple custom content
export function CustomPageContent({ content }) {
  return <div dangerouslySetInnerHTML={{ __html: content }} />;
}

// Factory function to create page content based on type
export function createPageContent(type, data) {
  switch (type) {
    case PageContentTypes.INTRO:
      return <IntroPageContent {...data} />;
    case PageContentTypes.NOTICE:
      return <NoticePageContent {...data} />;
    case PageContentTypes.RESOURCES:
      return <ResourcesPageContent {...data} />;
    case PageContentTypes.KEY_POINTS:
      return <KeyPointsPageContent {...data} />;
    case PageContentTypes.SUMMARY:
      return <SummaryPageContent {...data} />;
    case PageContentTypes.EXPLANATION:
      return <ExplanationPageContent {...data} />;
    case PageContentTypes.CUSTOM:
      return <CustomPageContent {...data} />;
    default:
      return <div>{data.content || "No content available"}</div>;
  }
}
