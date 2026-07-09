export interface ContentBlock {
  type: string;
  text?: string;
  items?: string[];
  title?: string;
  additional?: string;
  note?: string;
  steps?: string[];
  name?: string;
  [key: string]: unknown;
}

export interface ContentSection {
  section_number?: string;
  section_title: string;
  content: ContentBlock[];
}

export interface ContentPage {
  page_title: string;
  url?: string;
  source?: string;
  intro?: string;
  note?: string;
  sections: ContentSection[];
}

export interface NavItem {
  label: string;
  href: string;
  description?: string;
}

export interface NavGroup {
  label: string;
  href?: string;
  items?: NavItem[];
}

export const SITE_NAV: NavGroup[] = [
  { label: "Home", href: "/" },
  { label: "Resources", href: "/resources" },
  {
    label: "For Authors",
    items: [
      { label: "Submission Requirements", href: "https://ijaike.org/submission-requirements/", description: "Manuscript preparation & documentation" },
      { label: "Submission Procedure", href: "https://ijaike.org/submission-procedure/", description: "Step-by-step online submission" },
      { label: "Formatting for Publication", href: "https://ijaike.org/formatting-for-publication/", description: "Word format, margins, references" },
      { label: "Article Types & Style Guide", href: "https://ijaike.org/formatting-for-publication/", description: "Word limits, structure, figures" },
    ],
  },
  {
    label: "APC",
    items: [
      { label: "APC Policy (Official)", href: "https://ijaike.org/article-processing-charges-apc/", description: "Official JAIKE processing charges" },
      { label: "Interactive APC Estimator", href: "/apc", description: "Calculate page and illustration fees" }
    ]
  },
  {
    label: "Review",
    items: [
      { label: "Reviewer Anonymity Policy", href: "https://ijaike.org/reviewer-anonymity-policy/", description: "Double-blind peer review" },
    ],
  },
  {
    label: "Special Issues",
    items: [
      { label: "Special Issue Process", href: "https://ijaike.org/special-issue-process/", description: "How to propose a special issue" },
      { label: "Calls for Papers", href: "https://ijaike.org/cfp-special-issues/", description: "Active special issue CFPs" },
    ],
  },
];

export const PAGE_SLUGS: Record<string, string> = {
  "submission-requirements": "Submission Requirements",
  "submission-procedure": "Submission Procedure",
  "formatting": "Journal Article Types and Style Guide",
  "style-guide": "Journal Article Types and Style Guide",
  "anonymity-policy": "Reviewer Anonymity Policy",
  "process": "Special Issue Process",
  "apc-info": "Article Processing Charges (APC)",
};

export const SPECIAL_ISSUE_TOPICS = [
  "Agentic AI",
  "Generative AI",
  "AI for Healthcare",
  "AI for Enterprise Automation",
  "Explainability in AI & Safety",
  "Knowledge Graphs & Semantic Web",
  "NLP in Software Security and Vulnerability Management",
  "AI for Wireless Communication and Networking",
  "AI for Education",
  "AI-driven Concurrent Engineering",
  "AI-driven Robotics and Automation",
  "AI for Bioinformatics in Healthcare",
  "AI for PLM",
  "AI for Supply Chain Management",
  "Quantum Intelligence Computing into Industry 5.0",
];

export const MANUSCRIPT_CENTRAL = "https://mc04.manuscriptcentral.com/jaike";
