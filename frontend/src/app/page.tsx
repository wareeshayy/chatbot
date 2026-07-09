"use client";

import Link from "next/link";
import { SPECIAL_ISSUE_TOPICS, MANUSCRIPT_CENTRAL } from "@/lib/ijaike-content";

export default function HomePage() {
  const recentArticles = [
    {
      title: "Optimizing Agentic Workflows in Distributed IoT Networks",
      authors: "Dr. Elena Rostova, Prof. Marcus Chen",
      abstract: "This paper presents a novel framework for distributed decision-making in multi-agent IoT networks, optimizing latency by 34% using deep reinforcement learning models.",
      category: "Agentic AI",
      date: "June 25, 2026",
    },
    {
      title: "Knowledge Graphs for Enterprise Automation: A Comprehensive Review",
      authors: "Sarah Jenkins, Dr. Aaron Vance",
      abstract: "A benchmarking study on semantic linking and schemas for relational databases in large-scale enterprise settings, outlining zero-shot translation properties.",
      category: "Knowledge Engineering",
      date: "May 14, 2026",
    },
    {
      title: "Ensuring Safety and Alignment in Generative LLMs via Reward Shaping",
      authors: "Prof. Kenneth Sterling, Amit Patel",
      abstract: "We introduce a context-filtering system that optimizes reward shaping for large-scale code-generation parameters, reducing hallucination vectors significantly.",
      category: "AI Safety & Ethics",
      date: "April 02, 2026",
    },
  ];

  return (
    <div className="bg-slate-55 flex-1 flex flex-col font-sans">
      {/* 1. Scholarly Hero Section */}
      <section className="bg-gradient-to-r from-[#030b14] via-[#091526] to-[#040d1a] text-white py-16 px-4 border-b-4 border-[#d4a843] select-none text-left">
        <div className="mx-auto max-w-6xl">
          <span className="inline-block bg-[#d4a843]/10 border border-[#d4a843]/40 text-[#d4a843] px-3 py-1 rounded text-xs font-semibold tracking-wider uppercase mb-4">
            Inaugural Issues CFP
          </span>
          <h1 className="text-3xl md:text-5xl font-bold tracking-tight text-white leading-tight">
            International Journal of Artificial Intelligence <br className="hidden md:block"/>
            &amp; Knowledge Engineering <span className="text-[#d4a843]">(IJAIKE)</span>
          </h1>
          <p className="mt-4 text-base md:text-lg text-white/80 max-w-3xl leading-relaxed">
            A premier peer-reviewed, open-access journal publishing high-quality theoretical and applied research at the intersection of AI paradigms, Knowledge Representation, and IoT engineering.
          </p>
          <div className="mt-8 flex flex-wrap gap-4 text-sm font-medium">
            <a
              href={MANUSCRIPT_CENTRAL}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-[#d4a843] text-[#0a1628] hover:bg-[#c49738] px-6 py-3 rounded-lg font-semibold transition"
            >
              Submit Your Manuscript
            </a>
            <Link
              href="/resources"
              className="bg-white/10 hover:bg-white/15 text-white border border-white/20 px-6 py-3 rounded-lg font-semibold transition"
            >
              Author Guidelines
            </Link>
            <Link
              href="/apc"
              className="text-[#d4a843] hover:text-[#c49738] px-4 py-3 rounded font-semibold transition flex items-center gap-1"
            >
              Estimate APC Fees →
            </Link>
          </div>
        </div>
      </section>

      {/* 2. Journal Metrics Quick stats */}
      <section className="bg-white border-b border-slate-200 select-none py-8 px-4">
        <div className="mx-auto max-w-6xl grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          <div className="p-3">
            <p className="text-xl md:text-3xl font-bold text-[#0a1628]">4–8 Weeks</p>
            <p className="text-xs text-slate-500 uppercase tracking-wider mt-1">Average Peer Review</p>
          </div>
          <div className="p-3 border-l border-slate-100">
            <p className="text-xl md:text-3xl font-bold text-[#0a1628]">4–6 Weeks</p>
            <p className="text-xs text-slate-500 uppercase tracking-wider mt-1">Decision to Publish</p>
          </div>
          <div className="p-3 border-l border-slate-100">
            <p className="text-xl md:text-3xl font-bold text-[#d4a843]">$99/Page</p>
            <p className="text-xs text-slate-500 uppercase tracking-wider mt-1">Inaugural APC Rate</p>
          </div>
          <div className="p-3 border-l border-slate-100">
            <p className="text-xl md:text-3xl font-bold text-[#0a1628]">Fully Open</p>
            <p className="text-xs text-slate-500 uppercase tracking-wider mt-1">Access Policy</p>
          </div>
        </div>
      </section>

      {/* 3. Main Content Columns */}
      <div className="mx-auto max-w-6xl px-4 py-12 grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Columns: Scope & Recent Papers */}
        <div className="lg:col-span-2 space-y-12">
          {/* Scope and topics */}
          <section className="text-left">
            <h2 className="text-2xl font-bold text-[#0a1628] border-b-2 border-slate-200 pb-2.5">
              Journal Scope &amp; Focus Area
            </h2>
            <p className="mt-4 text-sm text-slate-600 leading-relaxed">
              IJAIKE seeks core research contributions advancing the foundations, applications, and validation of artificial intelligence. We focus on bridging the gaps between generative capabilities and symbolic knowledge structures.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
              {[
                { title: "Knowledge Graphs", desc: "Modeling semantic facts and ontology relations." },
                { title: "Agentic AI Frameworks", desc: "Automated workflow tools, orchestration, and alignment." },
                { title: "Double-Blind Review", desc: "Ensuring peer-review integrity with rigorous guidelines." },
                { title: "IoT Integration", desc: "Deep edge intelligence, sensor models, and microcontrollers." }
              ].map((scope, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-white border border-slate-200/80 shadow-sm flex items-start gap-3">
                  <div className="mt-1 h-2.5 w-2.5 rounded-full bg-[#d4a843] shrink-0" />
                  <div>
                    <h3 className="font-semibold text-slate-800 text-xs">{scope.title}</h3>
                    <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">{scope.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Recent Articles */}
          <section className="text-left">
            <h2 className="text-2xl font-bold text-[#0a1628] border-b-2 border-slate-200 pb-2.5">
              Featured Articles &amp; Recent Releases
            </h2>
            <div className="mt-6 space-y-6">
              {recentArticles.map((article, idx) => (
                <div key={idx} className="p-6 bg-white border border-slate-200/80 rounded-2xl shadow-sm hover:shadow-md transition">
                  <span className="inline-block bg-[#0a1628]/5 text-[#0a1628] px-2.5 py-0.5 rounded text-[10px] font-semibold tracking-wide uppercase">
                    {article.category}
                  </span>
                  <h3 className="font-bold text-slate-800 text-sm mt-2 hover:text-[#d4a843] transition cursor-pointer">
                    {article.title}
                  </h3>
                  <p className="text-xs text-slate-500 mt-1">{article.authors} · {article.date}</p>
                  <p className="text-xs text-slate-600 mt-3 leading-relaxed">{article.abstract}</p>
                  <div className="mt-4 flex items-center justify-between text-[11px] font-medium border-t border-slate-100 pt-3">
                    <span className="text-slate-400 font-mono">DOI: 10.32982/ijaike.2026.{idx + 104}</span>
                    <button className="text-[#d4a843] hover:text-[#c49738]">View PDF / Full Text →</button>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>

        {/* Right 1 Column: Promotion, Instructions, Call for Papers */}
        <aside className="space-y-6 text-left">
          {/* Call for papers widget */}
          <div className="p-6 bg-[#0a1628] text-white rounded-2xl border border-white/5 shadow-xl relative overflow-hidden select-none">
            <div className="absolute top-0 right-0 h-16 w-16 bg-[#d4a843]/15 rounded-full -mr-6 -mt-6"></div>
            <h3 className="text-lg font-bold text-[#d4a843]">Inaugural Call for Papers</h3>
            <p className="text-[11px] text-white/80 mt-2 leading-relaxed">
              Submit your work to the inaugural issues of IJAIKE. Take advantage of promotional launch packages and discount windows:
            </p>
            <ul className="mt-4 space-y-2 text-xs text-white/90">
              <li className="flex items-start gap-2">
                <span className="text-[#d4a843]">✓</span>
                <span><strong>50% APC Discount</strong> for submissions by Dec 30, 2025.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-[#d4a843]">✓</span>
                <span><strong>Flat $99/page</strong> for accepted text and illustrations.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-[#d4a843]">✓</span>
                <span>Waivers for low-income researchers and early careers.</span>
              </li>
            </ul>
            <Link
              href="/apc"
              className="mt-5 block text-center bg-[#d4a843] hover:bg-[#c49738] text-[#0a1628] font-bold text-xs py-2.5 rounded-lg transition"
            >
              Estimate Page Charges
            </Link>
          </div>

          {/* Active Special Issue Topics */}
          <div className="p-6 bg-white border border-slate-200/80 rounded-2xl shadow-sm">
            <h3 className="text-sm font-bold text-slate-800 border-b border-slate-100 pb-2">
              Active Special Issues
            </h3>
            <div className="mt-3.5 space-y-2 text-xs max-h-56 overflow-y-auto pr-1">
              {SPECIAL_ISSUE_TOPICS.slice(0, 8).map((topic, index) => (
                <div key={index} className="p-2 border-b border-slate-50 last:border-b-0 hover:bg-slate-50 transition rounded cursor-pointer">
                  <p className="font-semibold text-slate-800 text-[11px]">{topic}</p>
                  <p className="text-[9px] text-slate-400 mt-0.5">Submissions Open · CFP Available</p>
                </div>
              ))}
            </div>
            <Link
              href="/special-issues/calls-for-papers"
              className="mt-4 block text-center text-xs font-semibold text-[#d4a843] hover:underline"
            >
              See All Special Issue CFPs →
            </Link>
          </div>

          {/* Assistant Info block */}
          <div className="p-6 bg-gradient-to-br from-amber-500/5 to-amber-600/10 border border-[#d4a843]/30 rounded-2xl">
            <h3 className="font-bold text-[#0a1628] text-xs flex items-center gap-1.5">
              💡 Need Quick Information?
            </h3>
            <p className="text-[11px] text-slate-650 mt-1.5 leading-relaxed">
              Use our floating <strong>IJAIKE AI Assistant</strong> at the bottom right of the page to ask about:
            </p>
            <ul className="mt-2.5 space-y-1 text-[10px] text-slate-600">
              <li>• Margin, spacing, and word limits requirements</li>
              <li>• Required documents (Cover letter, manuscript docx)</li>
              <li>• Review processes and anonymity constraints</li>
              <li>• Waiver eligibility and APC estimations</li>
            </ul>
            <p className="text-[10px] font-semibold text-[#d4a843] mt-3">
              Click the blue chat icon to start a conversation!
            </p>
          </div>
        </aside>
      </div>
    </div>
  );
}
