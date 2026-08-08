import Link from "next/link";
import { DocumentViewerUploader } from "@/components/DocumentViewerUploader";

export const metadata = {
  title: "Agentic AI Solutions for Intelligent ChatBot Development | AIKE Services",
  description: "Advanced AI Assistants for Research, Knowledge Automation, and Enterprise Workflows by JAIKE Business Solutions.",
};

export default function AgenticAiChatbotPage() {
  return (
    <div className="bg-slate-50 min-h-screen text-slate-800 font-sans">
      {/* Top Header */}
      <section className="bg-[#0a1628] text-white py-12 px-4 border-b-4 border-[#d4a843]">
        <div className="mx-auto max-w-4xl">
          <div className="flex items-center gap-2 text-xs text-[#d4a843] mb-3">
            <Link href="/aike-services" className="hover:underline">
              AIKE Services
            </Link>
            <span>/</span>
            <span>Document 1</span>
          </div>
          <p className="text-xs uppercase font-mono tracking-wider text-white/60">JAIKE BUSINESS UNIT AI SERVICES</p>
          <h1 className="text-2xl md:text-4xl font-bold text-white mt-1 leading-tight">
            Agentic AI Solutions for Intelligent ChatBot Development
          </h1>
          <p className="mt-3 text-sm text-white/80 leading-relaxed italic">
            Advanced AI Assistants for Research, Knowledge Automation, and Enterprise Workflows
          </p>
        </div>
      </section>

      {/* Main Document Content */}
      <main className="mx-auto max-w-4xl px-4 py-10 space-y-10 text-left">
        {/* PDF Download & File Upload Widget */}
        <DocumentViewerUploader
          documentTitle="Agentic AI Solutions for Intelligent ChatBot Development"
          pdfFileName="Agentic_AI_Solutions_for_Intelligent_Chatbot_Development.pdf"
          pdfUrl="/documents/Agentic_AI_Solutions_for_Intelligent_Chatbot_Development.txt"
        />

        {/* Introduction */}
        <section className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm space-y-4">
          <h2 className="text-xl font-bold text-[#0a1628] border-b border-slate-100 pb-3">
            Executive Summary &amp; Overview
          </h2>
          <p className="text-sm text-slate-700 leading-relaxed">
            At <strong>JAIKE Business Solutions</strong>, we specialize in designing and developing <strong>Agentic AI chatbots</strong> that go far beyond traditional conversational systems. These intelligent assistants are engineered to understand complex domain-specific queries, retrieve and analyze information from structured and unstructured sources, and deliver accurate, context-aware responses grounded in your organization’s knowledge base.
          </p>
          <p className="text-sm text-slate-700 leading-relaxed">
            Our Agentic AI chatbots are ideal for <strong>academic journals, universities, research groups, enterprises, and knowledge-driven organizations</strong> seeking to modernize how information is accessed, processed, and delivered.
          </p>
        </section>

        {/* Core Capabilities */}
        <section className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm space-y-6">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <span className="text-xl">🌐</span>
            <h2 className="text-xl font-bold text-[#0a1628]">Core Capabilities</h2>
          </div>

          <div className="space-y-6 text-sm text-slate-700">
            {/* 1 */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <h3 className="font-bold text-[#0a1628] text-base">1. Semantic Knowledge Retrieval</h3>
              <p className="mt-1 text-slate-600">
                Our chatbots use <strong>vector embeddings, semantic search, and RAG pipelines</strong> to retrieve the most relevant information from PDFs, Word documents, databases, and internal repositories.
              </p>
            </div>

            {/* 2 */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <h3 className="font-bold text-[#0a1628] text-base">2. Multi-Agent Reasoning</h3>
              <p className="mt-1 text-slate-600">
                We implement multi-agent workflows that mirror human research and review processes:
              </p>
              <ul className="mt-2 space-y-1.5 pl-4 list-disc text-slate-700 font-medium">
                <li><strong className="text-[#0a1628]">Researcher Agent</strong> – retrieves relevant context</li>
                <li><strong className="text-[#0a1628]">Reviewer Agent</strong> – validates and refines retrieved information</li>
                <li><strong className="text-[#0a1628]">Writer Agent</strong> – generates structured, citation-aware responses</li>
              </ul>
              <p className="mt-2 text-xs text-slate-500 italic">This ensures reliability, accuracy, and consistency across all interactions.</p>
            </div>

            {/* 3 */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <h3 className="font-bold text-[#0a1628] text-base">3. Dynamic Tool Selection</h3>
              <p className="mt-1 text-slate-600">
                The system autonomously determines the best action for each query:
              </p>
              <div className="mt-3 grid grid-cols-2 md:grid-cols-3 gap-2 text-xs">
                <span className="bg-white border border-slate-200 p-2 rounded text-center">Vector DB Search</span>
                <span className="bg-white border border-slate-200 p-2 rounded text-center">Live Calculators (APC/Metrics)</span>
                <span className="bg-white border border-slate-200 p-2 rounded text-center">Web Search</span>
                <span className="bg-white border border-slate-200 p-2 rounded text-center">Document Parsing</span>
                <span className="bg-white border border-slate-200 p-2 rounded text-center">Knowledge Graph Lookup</span>
              </div>
            </div>

            {/* 4 */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <h3 className="font-bold text-[#0a1628] text-base">4. Persistent Memory &amp; Multi-Turn Conversations</h3>
              <p className="mt-1 text-slate-600">
                Our chatbots maintain conversation history across sessions, enabling context-aware follow-up questions, long-form research assistance, and personalized user interactions.
              </p>
            </div>

            {/* 5 */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <h3 className="font-bold text-[#0a1628] text-base">5. Intelligent Document Processing</h3>
              <p className="mt-1 text-slate-600">
                We support automated ingestion of <strong>PDFs, Word documents, research papers, reports, and manuscripts</strong>. Documents are parsed, embedded, indexed, and made searchable through semantic retrieval.
              </p>
            </div>
          </div>
        </section>

        {/* Where Used */}
        <section className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm space-y-6">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <span className="text-xl">💐</span>
            <h2 className="text-xl font-bold text-[#0a1628]">Where Used? (Target Customers)</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs text-slate-700">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <h3 className="font-bold text-[#0a1628] text-sm mb-2">Academic Journals</h3>
              <ul className="space-y-1.5 list-disc pl-4">
                <li>Assist authors in understanding journal scope</li>
                <li>Provide citation-aware answers</li>
                <li>Help researchers explore previously published work</li>
                <li>Automate responses to common author queries</li>
                <li>Support manuscript preparation and submission workflows</li>
              </ul>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <h3 className="font-bold text-[#0a1628] text-sm mb-2">Universities &amp; Research Labs</h3>
              <ul className="space-y-1.5 list-disc pl-4">
                <li>Provide intelligent access to internal research repositories</li>
                <li>Assist students and faculty with domain-specific queries</li>
                <li>Automate literature review support</li>
                <li>Enable interactive exploration of research topics</li>
              </ul>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <h3 className="font-bold text-[#0a1628] text-sm mb-2">AI Researchers</h3>
              <ul className="space-y-1.5 list-disc pl-4">
                <li>Demonstrate practical applications of Agentic AI</li>
                <li>Showcase RAG architectures in real-world systems</li>
                <li>Provide a foundation for explainable AI and knowledge engineering</li>
              </ul>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <h3 className="font-bold text-[#0a1628] text-sm mb-2">AI Application Developers in Industries</h3>
              <ul className="space-y-1.5 list-disc pl-4">
                <li>Customer support automation</li>
                <li>Internal knowledge management</li>
                <li>Technical documentation search</li>
                <li>Compliance and policy assistance</li>
                <li>Product &amp; engineering knowledge bases</li>
                <li>HR and onboarding automation</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Why Choose JAIKE */}
        <section className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <span className="text-xl">🚀</span>
            <h2 className="text-xl font-bold text-[#0a1628]">Why Choose JAIKE Business Solutions?</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="p-3 bg-amber-50/50 border border-amber-200/60 rounded-lg">
              <strong className="text-[#0a1628] text-sm block">Expertise in Agentic AI</strong>
              <span className="text-slate-600 mt-1 block">We specialize in multi-agent architectures, RAG pipelines, and domain-aware AI systems.</span>
            </div>
            <div className="p-3 bg-amber-50/50 border border-amber-200/60 rounded-lg">
              <strong className="text-[#0a1628] text-sm block">Deep Research Background</strong>
              <span className="text-slate-600 mt-1 block">Built with academic research rigor and enterprise engineering practicality.</span>
            </div>
            <div className="p-3 bg-amber-50/50 border border-amber-200/60 rounded-lg">
              <strong className="text-[#0a1628] text-sm block">Customizable &amp; Scalable</strong>
              <span className="text-slate-600 mt-1 block">Tailored to your organization&apos;s domain, workflows, and data sources.</span>
            </div>
            <div className="p-3 bg-amber-50/50 border border-amber-200/60 rounded-lg">
              <strong className="text-[#0a1628] text-sm block">End-to-End Development</strong>
              <span className="text-slate-600 mt-1 block">From system design to deployment, maintenance, and continuous improvement.</span>
            </div>
          </div>
        </section>

        {/* Call to Action */}
        <section className="bg-[#0a1628] text-white rounded-2xl p-8 border border-white/10 text-center">
          <h3 className="text-xl font-bold text-[#d4a843]">📢 Call to Action</h3>
          <p className="text-xs md:text-sm text-white/80 mt-2 max-w-xl mx-auto leading-relaxed">
            If your organization is exploring AI-powered research assistants, knowledge automation, or custom Agentic AI solutions, JAIKE Business Solutions is ready to help you build the next generation of fast, reliable, and secure intelligent systems.
          </p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-4 text-xs font-semibold">
            <a
              href="https://ijaike.org/contacts-us/"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-[#d4a843] hover:bg-[#c49738] text-[#0a1628] px-6 py-2.5 rounded-lg transition"
            >
              Contact Us Online
            </a>
            <a
              href="mailto:JournalAIKE@Gmail.com"
              className="bg-white/10 hover:bg-white/20 text-white border border-white/20 px-6 py-2.5 rounded-lg transition"
            >
              JournalAIKE@Gmail.com
            </a>
          </div>
        </section>
      </main>
    </div>
  );
}
