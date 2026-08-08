import Link from "next/link";
import { DocumentViewerUploader } from "@/components/DocumentViewerUploader";

export const metadata = {
  title: "Custom AI-Powered Web Applications & Full-Stack Software Development | AIKE Services",
  description: "End-to-end full-stack software development, AI web apps, enterprise portals, and cloud engineering by JAIKE Business Unit.",
};

export default function CustomAiWebAppsPage() {
  const capabilities = [
    { title: "Business Websites", desc: "Professional, responsive, SEO-friendly websites that establish a strong digital presence and convert visitors into customers." },
    { title: "AI-Powered Web Applications", desc: "Custom web apps that embed intelligent features such as chatbots, recommendation engines, search, and automation directly into the product experience." },
    { title: "Enterprise Portals & Dashboards", desc: "Secure, role-based portals and real-time dashboards that give teams and clients a single place to manage data, workflows, and reporting." },
    { title: "Full-Stack Software Development", desc: "End-to-end engineering across frontend, backend, database, and infrastructure, delivered as a single accountable service." },
    { title: "API & Systems Integration", desc: "Connecting new and existing applications with CRMs, ERPs, payment gateways, and third-party services via secure, well-documented APIs." },
    { title: "Cloud Deployment & DevOps", desc: "Reliable, scalable hosting and deployment pipelines that keep applications fast, secure, and easy to maintain." },
  ];

  const buildItems = [
    "1. Custom Business Websites",
    "2. AI-Powered Web Applications",
    "3. Enterprise Portals & Dashboards (Client, vendor, partner, employee HR portals, real-time analytics)",
    "4. Full-Stack Software Development (React, Next.js, Node.js, Python, Auth, DB Modeling)",
    "5. API & Third-Party Integrations (CRMs, ERPs, Payment gateways, Calendars)",
    "6. E-Commerce & SaaS Platforms (Multi-tenant SaaS, subscription billing, order processing)",
    "7. UI/UX Design & Frontend Engineering (Wireframing, Design systems, Responsive, Accessibility)",
    "8. Cloud Deployment & DevOps (CI/CD pipelines, Docker, Kubernetes, Monitoring)",
    "9. Database Design & Management (PostgreSQL, MongoDB, Redis, SQLite)",
    "10. Performance Optimization & Security (Audits, Encryption, Vulnerability testing)",
    "11. Maintenance & Ongoing Support",
    "12. Embedded AI Features (Conversational assistants, semantic search, RAG)",
    "13. Consulting & Solution Architecture",
  ];

  const techStack = {
    Frontend: ["React", "Next.js", "TypeScript", "Tailwind CSS"],
    Backend: ["Node.js", "Express.js", "Python", "FastAPI"],
    Databases: ["MongoDB", "PostgreSQL", "Redis", "SQLite"],
    "API & Integration": ["REST APIs", "GraphQL", "Webhooks", "OAuth 2.0"],
    "DevOps & Deployment": ["Docker", "Kubernetes", "Git & GitHub", "GitHub Actions (CI/CD)", "Vercel / Netlify", "Render / Railway"],
    "Design & Testing": ["Figma", "Storybook", "Jest", "Playwright"],
  };

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
            <span>Document 2</span>
          </div>
          <p className="text-xs uppercase font-mono tracking-wider text-white/60">JAIKE BUSINESS UNIT AI SERVICES</p>
          <h1 className="text-2xl md:text-4xl font-bold text-white mt-1 leading-tight">
            Custom AI-Powered Web Applications &amp; Full-Stack Software Development
          </h1>
          <p className="mt-3 text-sm text-white/80 leading-relaxed italic">
            Transform your digital presence and internal operations through modern, scalable, and intelligent software.
          </p>
        </div>
      </section>

      {/* Main Document Content */}
      <main className="mx-auto max-w-4xl px-4 py-10 space-y-10 text-left">
        {/* PDF Download & File Upload Widget */}
        <DocumentViewerUploader
          documentTitle="Custom AI-Powered Web Applications & Full-Stack Software Development"
          pdfFileName="Custom_AI_Powered_Web_Applications_and_Full_Stack_Software_Development.pdf"
          pdfUrl="/documents/Custom_AI_Powered_Web_Applications_and_Full_Stack_Software_Development.pdf"
        />

        {/* Executive Summary */}
        <section className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm space-y-4">
          <h2 className="text-xl font-bold text-[#0a1628] border-b border-slate-100 pb-3">
            Executive Summary
          </h2>
          <p className="text-sm text-slate-700 leading-relaxed">
            At the <strong>IJAIKE Business Unit</strong>, we provide a variety of AI-powered software development services. Transform your digital presence and internal operations through modern, scalable, and intelligent software. We design and develop custom AI-powered web applications, business websites, enterprise portals, and dashboards that combine clean engineering, thoughtful design, and applied AI to deliver fast, reliable, and secure digital products.
          </p>
          <p className="text-sm text-slate-700 leading-relaxed">
            Our AI solutions are tailored for startups, enterprises, universities, research organizations, and businesses seeking a dependable technology partner for full-stack software development, from prototype to production deployment.
          </p>
        </section>

        {/* Capabilities at a Glance */}
        <section className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm space-y-6">
          <h2 className="text-xl font-bold text-[#0a1628] border-b border-slate-100 pb-3">
            Full-Stack Software Capabilities at a Glance
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            {capabilities.map((cap, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                <h3 className="font-bold text-[#0a1628] text-sm mb-1.5">{cap.title}</h3>
                <p className="text-slate-600 leading-relaxed">{cap.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* What JAIKE Builds */}
        <section className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm space-y-4">
          <h2 className="text-xl font-bold text-[#0a1628] border-b border-slate-100 pb-3">
            01 — Our AI Services: What JAIKE Builds
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            {buildItems.map((item, i) => (
              <div key={i} className="p-3 bg-slate-50 border border-slate-100 rounded-lg text-slate-700 font-medium">
                {item}
              </div>
            ))}
          </div>
        </section>

        {/* Technology Stack Grid */}
        <section className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm space-y-6">
          <h2 className="text-xl font-bold text-[#0a1628] border-b border-slate-100 pb-3">
            02 — Technology Stack
          </h2>
          <p className="text-xs text-slate-600">
            Our web applications and enterprise software are engineered on a modern, dependable, and cost-efficient open-source stack:
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            {Object.entries(techStack).map(([category, items]) => (
              <div key={category} className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
                <h3 className="font-bold text-[#0a1628] border-b border-slate-200 pb-1.5 mb-2">{category}</h3>
                <ul className="space-y-1 text-slate-700 font-medium">
                  {items.map((it, idx) => (
                    <li key={idx} className="flex items-center gap-1.5">
                      <span className="text-[#d4a843]">✓</span> {it}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>

        {/* Call to Action */}
        <section className="bg-[#0a1628] text-white rounded-2xl p-8 border border-white/10 text-center">
          <h3 className="text-xl font-bold text-[#d4a843]">📢 Call to Action</h3>
          <p className="text-xs md:text-sm text-white/80 mt-2 max-w-xl mx-auto leading-relaxed">
            If your organization is exploring custom AI-powered web applications, business websites, enterprise portals, and dashboards, JAIKE Business Solutions is ready to help you build the next generation of digital products.
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
