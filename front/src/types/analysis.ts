// TypeScript types for the analysis system

export enum HighlightColor {
  RED = "red",
  YELLOW = "yellow",
  BLUE = "blue",
}

export enum HighlightType {
  LEGAL_RISK = "legal_risk",
  COMPLIANCE_ISSUE = "compliance_issue",
  STANDARD_CLAUSE = "standard_clause",
  CUSTOM = "custom",
}

export enum PageContentType {
  INTRO = "intro",
  NOTICE = "notice",
  RESOURCES = "resources",
  KEY_POINTS = "key_points",
  SUMMARY = "summary",
  CUSTOM = "custom",
}

export interface Rectangle {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface HighlightMetadata {
  shortTitle: string;
  title: string;
  type: HighlightType;
  data: Record<string, any>;
}

export interface Highlight {
  id: string;
  page: number;
  rect: Rectangle;
  color: HighlightColor;
  metadata: HighlightMetadata;
}

export interface PageContent {
  type: PageContentType;
  data: Record<string, any>;
}

export interface DocumentInfo {
  name: string;
  date: string;
}

export interface AnalysisResponse {
  highlights: Highlight[];
  pageContent: Record<number, PageContent>;
  documentInfo: DocumentInfo;
}

export interface UploadResponse {
  message: string;
  analysis_id: string;
}

// Helper types for component data structures

export interface LegalRiskData {
  title: string;
  explanation: string;
  severity: "high" | "medium" | "low";
  article?: string;
  recommendation?: string;
}

export interface ComplianceIssueData {
  title: string;
  explanation: string;
  regulation?: string;
  urgency: "high" | "medium" | "low";
}

export interface StandardClauseData {
  title: string;
  explanation: string;
  isNegotiable?: boolean;
  tips?: string[];
}

export interface IntroPageData {
  title: string;
  description: string;
  buttonText?: string;
  onButtonClick?: () => void;
}

export interface NoticePageData {
  title: string;
  message: string;
  severity: "info" | "warning" | "error" | "success";
  actions?: Array<{
    label: string;
    primary: boolean;
    onClick?: () => void;
  }>;
}

export interface KeyPointsPageData {
  title: string;
  theme?: "blue" | "green" | "purple" | "gray";
  points: string[];
}
