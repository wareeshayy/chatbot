import Link from "next/link";
import { DocumentViewerUploader } from "@/components/DocumentViewerUploader";

export const metadata = {
  title: "AIKE AI Services | International Journal of Artificial Intelligence & Knowledge Engineering",
  description: "Explore JAIKE Business Unit AI Services: Agentic AI Chatbot Development and Custom AI-Powered Web Applications & Full-Stack Software Development.",
};

export default function AIKEServicesPage() {
  return (
    <div className="bg-slate-50 min-h-screen text-slate-800 font-sans">
      {/* Hero Header */}
      <section className="bg-gradient-to-r from-[#030b14] via-[#0a1628] to-[#051122] text-white py-14 px-4 border-b-4 border-[#d4a843]">
        <div className="mx-auto max-w-5xl">
          <span className="inline-block bg-[#d4a843]/15 border border-[#d4a843]/40 text-[#d4a843] px-3 py-1 rounded text-xs font-bold tracking-wider uppercase mb-3">
            JAIKE Business Unit AI Services
          </span>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-white leading-tight">
            AIKE AI Services &amp; Enterprise Solutions
          </h1>
          <p className="mt-4 text-sm md:text-base text-white/80 max-w-3xl leading-relaxed">
            We specialize in designing and engineering custom Agentic AI chatbots, RAG knowledge retrieval systems, and full-stack AI-powered web applications tailored for academic journals, universities, research labs, and enterprise organizations.
          </p>
        </div>
      </section>

      {/* Main Content Hub */}
      <main className="mx-auto max-w-5xl px-4 py-12 space-y-12 text-left">
        {/* Document Showcase Grid */}
        <section>
          <h2 className="text-2xl font-bold text-[#0a1628] border-b-2 border-slate-200 pb-3">
            Service Specifications &amp; Official Documentation
          </h2>
          <p className="text-sm text-slate-600 mt-2">
            Select a document below to view detailed capabilities, multi-agent architectures, technology stacks, and enterprise deployment options.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8">
            {/* Card 1 */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="h-3 w-3 rounded-full bg-[#d4a843]"></span>
                  <span className="text-xs font-mono uppercase tracking-wider text-[#d4a843] font-semibold">Document 1</span>
                </div>
                <h3 className="text-lg font-bold text-[#0a1628] mt-3 leading-snug">
                  Agentic AI Solutions for Intelligent ChatBot Development
                </h3>
                <p className="text-xs text-slate-600 mt-3 leading-relaxed">
                  Advanced AI Assistants for research, knowledge automation, and enterprise multi-agent workflows. Features RAG retrieval, multi-turn persistent memory, and dynamic tool selection.
                </p>
              </div>

              <div className="mt-6 pt-4 border-t border-slate-100 flex flex-wrap gap-3">
                <Link
                  href="/aike-services/agentic-ai-chatbot"
                  className="flex-1 text-center bg-[#0a1628] hover:bg-[#142847] text-white text-xs font-semibold py-2.5 px-4 rounded-lg transition"
                >
                  View Full Document →
                </Link>
                <a
                  href="/documents/Agentic_AI_Solutions_for_Intelligent_Chatbot_Development.txt"
                  download="Agentic_AI_Solutions_for_Intelligent_Chatbot_Development.txt"
                  className="bg-slate-100 hover:bg-slate-200 text-[#0a1628] text-xs font-semibold py-2.5 px-4 rounded-lg transition flex items-center gap-1"
                >
                  Download PDF
                </a>
              </div>
            </div>

            {/* Card 2 */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="h-3 w-3 rounded-full bg-[#d4a843]"></span>
                  <span className="text-xs font-mono uppercase tracking-wider text-[#d4a843] font-semibold">Document 2</span>
                </div>
                <h3 className="text-lg font-bold text-[#0a1628] mt-3 leading-snug">
                  Custom AI-Powered Web Applications &amp; Full-Stack Software Development
                </h3>
                <p className="text-xs text-slate-600 mt-3 leading-relaxed">
                  Full-stack software engineering across React/Next.js, Node.js, Python FastAPI, PostgreSQL, and Cloud DevOps. Delivering custom business portals, dashboards, and embedded AI.
                </p>
              </div>

              <div className="mt-6 pt-4 border-t border-slate-100 flex flex-wrap gap-3">
                <Link
                  href="/aike-services/custom-ai-web-apps"
                  className="flex-1 text-center bg-[#0a1628] hover:bg-[#142847] text-white text-xs font-semibold py-2.5 px-4 rounded-lg transition"
                >
                  View Full Document →
                </Link>
                <a
                  href="/documents/Custom_AI_Powered_Web_Applications_and_Full_Stack_Software_Development.txt"
                  download="Custom_AI_Powered_Web_Applications_and_Full_Stack_Software_Development.txt"
                  className="bg-slate-100 hover:bg-slate-200 text-[#0a1628] text-xs font-semibold py-2.5 px-4 rounded-lg transition flex items-center gap-1"
                >
                  Download PDF
                </a>
              </div>
            </div>
          </div>
        </section>

        {/* Upload Widget Section */}
        <section className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <h3 className="text-lg font-bold text-[#0a1628]">Document Management &amp; File Upload</h3>
          <p className="text-xs text-slate-500 mt-1">
            Need to upload a revised PDF version or upload a new service proposal? Use the document uploader below:
          </p>
          <DocumentViewerUploader
            documentTitle="AIKE Business Services Overview Document"
            pdfFileName="AIKE_Services_Specification.pdf"
            pdfUrl="/documents/Agentic_AI_Solutions_for_Intelligent_Chatbot_Development.txt"
          />
        </section>

        {/* Contact / CTA Banner */}
        <section className="bg-[#0a1628] text-white rounded-2xl p-8 border border-white/10 text-center relative overflow-hidden">
          <div className="max-w-2xl mx-auto">
            <h3 className="text-2xl font-bold text-[#d4a843]">Ready to Build Your AI Solution?</h3>
            <p className="text-xs md:text-sm text-white/80 mt-3 leading-relaxed">
              We will be happy to discuss your needs and explore how Agentic AI can transform your workflows at no cost to you.
            </p>
            <div className="mt-6 flex flex-wrap items-center justify-center gap-4 text-xs font-semibold">
              <a
                href="https://ijaike.org/contacts-us/"
                target="_blank"
                rel="noopener noreferrer"
                className="bg-[#d4a843] hover:bg-[#c49738] text-[#0a1628] px-6 py-3 rounded-lg transition"
              >
                Contact Us Online
              </a>
              <a
                href="mailto:JournalAIKE@Gmail.com"
                className="bg-white/10 hover:bg-white/20 text-white border border-white/20 px-6 py-3 rounded-lg transition"
              >
                Email: JournalAIKE@Gmail.com
              </a>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
