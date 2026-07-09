import Link from "next/link";
import { SPECIAL_ISSUE_TOPICS, MANUSCRIPT_CENTRAL } from "@/lib/ijaike-content";

const CFP_DOCUMENTS = [
  "Agentic AI",
  "Generative AI",
  "AI for Healthcare",
  "Explainability in AI",
  "AI for PLM",
  "AI for Supply Chain Management",
  "AI for Bioinformatics in Healthcare",
  "AI-driven Concurrent Engineering",
  "AI-driven Robotics and Automation",
  "AI for Education",
  "AI for Intelligent Wireless Communication and Networked Systems",
  "NLP in Software Security and Vulnerability Management",
  "Research Applications of Generative AI in Enterprise Automation",
  "Quantum Intelligence Computing into Industry 5.0",
  "Inaugural Issues of IJAIKE Journal",
];

export default function CallsForPapersPage() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-10">
      <p className="text-xs font-semibold uppercase tracking-[0.15em] text-[#d4a843]">Special Issues</p>
      <h1 className="mt-2 text-3xl font-semibold text-[#0a1628]">Calls for Papers</h1>
      <p className="mt-4 text-slate-600">
        IJAIKE publishes special issues on emerging AI and knowledge engineering topics.
        All CFP documents below are indexed in the AI knowledge base for citation-backed answers.
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        {CFP_DOCUMENTS.map((title) => (
          <div key={title} className="rounded-sm border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="font-semibold text-[#0a1628]">Call for Papers — {title}</h3>
            <p className="mt-2 text-sm text-slate-600">
              Submit via Manuscript Central and indicate the special issue title on the submission form.
            </p>
            <Link href="/" className="mt-3 inline-block text-sm font-medium text-[#d4a843] hover:underline">
              Ask AI about this CFP →
            </Link>
          </div>
        ))}
      </div>

      <div className="mt-10 rounded-sm bg-[#0a1628] p-6 text-white">
        <h2 className="font-semibold">Propose a New Special Issue</h2>
        <p className="mt-2 text-sm text-white/70">
          Send a formal proposal to editor-in-chief@ijaike.org including title, theme, guest editors, timeline, and rationale.
        </p>
        <div className="mt-4 flex flex-wrap gap-3">
          <Link href="/special-issues/process" className="rounded-sm bg-[#d4a843] px-4 py-2 text-sm font-semibold text-[#0a1628]">
            Special Issue Process
          </Link>
          <a href={MANUSCRIPT_CENTRAL} target="_blank" rel="noopener noreferrer" className="rounded-sm border border-white/30 px-4 py-2 text-sm hover:border-[#d4a843]">
            Submit Manuscript
          </a>
        </div>
      </div>

      <div className="mt-8">
        <h2 className="text-lg font-semibold text-[#0a1628]">All Inaugural Topics</h2>
        <ul className="mt-4 flex flex-wrap gap-2">
          {SPECIAL_ISSUE_TOPICS.map((t) => (
            <li key={t} className="rounded-full bg-slate-100 px-3 py-1 text-sm text-slate-700">{t}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
