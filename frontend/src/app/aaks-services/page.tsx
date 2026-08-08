export const metadata = {
  title: "AAKS Services | Advanced AI & Knowledge Systems",
  description: "Explore AAKS Services products: NeuroSyn-Copilot, NeuroSyn-Dev, NeuroSyn-Aero, and NeuroSyn-SAP documentation and demo videos.",
};

export default function AAKSServicesPage() {
  const products = [
    {
      id: "neurosyn-copilot",
      title: "NeuroSyn-Copilot",
      category: "Research & Writing Assistant",
      description: "AI-Powered Research & Coding Copilot for intelligent manuscript generation, agentic reasoning, and interactive knowledge assistance.",
      docName: "NeuroSyn-Copilot-Documentation",
      docLink: "https://drive.google.com/file/d/1LgGkC8pt4hbhX7PgHkFMJSIKCLWPqRnj/view?",
      demoName: "NeuroSyn-Copilot-Demo",
      demoLink: "https://drive.google.com/file/d/10ms4rgy1t8nZPzpwsmLCsUeWFR542L48/view?",
      icon: "🧠",
      features: [
        "Interactive RAG semantic literature retrieval",
        "Automated citation formatting & verification",
        "Multi-turn research assistant agent",
      ],
    },
    {
      id: "neurosyn-dev",
      title: "NeuroSyn-Dev",
      category: "Software Engineering Intelligence",
      description: "Full-Stack Developer AI Copilot & Automated Software Engineering Toolsuite for continuous integration, code auditing, and API synthesis.",
      docName: "NeuroSyn-Dev-Documentation",
      docLink: "https://drive.google.com/file/d/1ahUqSCkSwETs8kaf2YicuqwwqkPYXaBu/view?",
      demoName: "NeuroSyn-Dev-Demo",
      demoLink: "https://drive.google.com/file/d/1OnTfLcLJu7pFFQaqNxPdNC19GdgSrfOu/view?",
      icon: "💻",
      features: [
        "Full-stack code generation & refactoring",
        "Automated unit test & documentation generator",
        "Security vulnerability & bug scanner",
      ],
    },
    {
      id: "neurosyn-aero",
      title: "NeuroSyn-Aero",
      category: "Aerospace & Autonomous Intelligence",
      description: "Aerospace Engineering AI & Autonomous Simulation Intelligence Platform engineered for telemetry analysis, flight dynamics, and IoT modeling.",
      docName: "NeuroSyn-Aero-Documentation",
      docLink: "https://drive.google.com/file/d/1ADppcPRL7AzdbP4G7psPyQ3DNo2DFBR-/view?",
      demoName: "NeuroSyn-Aero-Demo",
      demoLink: "https://drive.google.com/file/d/1CKWSOBrEwr4KkKD0E-Im2U1ZxWur-msT/view?",
      icon: "✈️",
      features: [
        "Aerospace telemetry & sensor data parsing",
        "Autonomous simulation feedback loops",
        "Real-time edge analytics & flight dynamics",
      ],
    },
    {
      id: "neurosyn-sap",
      title: "NeuroSyn-SAP",
      category: "Enterprise ERP & SAP Automation",
      description: "Enterprise SAP Automation & Intelligent ERP Integration System designed to streamline workflow orchestration, data pipelines, and ERP reporting.",
      docName: "NeuroSyn-Sap-Documentation",
      docLink: "https://drive.google.com/file/d/1ZCjWGgL-uj6UyUnDHmT5IgMRK6MihpIM/view?",
      demoName: "NeuroSyn-Sap-Demo",
      demoLink: "https://drive.google.com/file/d/1HyvCIugjy5tzfsTzSlCbRnroCEJBFJ4t/view?",
      icon: "📊",
      features: [
        "SAP & ERP process automation",
        "Role-based enterprise security integration",
        "Intelligent analytics & executive reporting",
      ],
    },
  ];

  return (
    <div className="bg-slate-50 min-h-screen text-slate-800 font-sans">
      {/* Hero Header */}
      <section className="bg-gradient-to-r from-[#030b14] via-[#0a1628] to-[#040e1d] text-white py-14 px-4 border-b-4 border-[#d4a843]">
        <div className="mx-auto max-w-5xl">
          <span className="inline-block bg-[#d4a843]/15 border border-[#d4a843]/40 text-[#d4a843] px-3 py-1 rounded text-xs font-bold tracking-wider uppercase mb-3">
            AAKS Services Product Suite
          </span>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-white leading-tight">
            Advanced AI &amp; Knowledge Systems (AAKS)
          </h1>
          <p className="mt-4 text-sm md:text-base text-white/80 max-w-3xl leading-relaxed">
            Discover our specialized NeuroSyn product suite empowering academic researchers, software engineers, aerospace teams, and enterprise SAP operations.
          </p>
        </div>
      </section>

      {/* Main Content Product Suite */}
      <main className="mx-auto max-w-5xl px-4 py-12 space-y-10 text-left">
        <div className="space-y-8">
          {products.map((prod) => (
            <div
              key={prod.id}
              id={prod.id}
              className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm hover:shadow-md transition scroll-mt-24"
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 pb-4">
                <div className="flex items-center gap-3">
                  <span className="text-3xl bg-amber-50 p-2.5 rounded-xl border border-amber-200/60">{prod.icon}</span>
                  <div>
                    <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-[#d4a843] block">
                      {prod.category}
                    </span>
                    <h2 className="text-2xl font-bold text-[#0a1628]">{prod.title}</h2>
                  </div>
                </div>
              </div>

              <p className="mt-4 text-sm text-slate-700 leading-relaxed">
                {prod.description}
              </p>

              {/* Key Features */}
              <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
                {prod.features.map((feat, idx) => (
                  <div key={idx} className="p-2.5 bg-slate-50 border border-slate-100 rounded-lg text-slate-700 flex items-center gap-2">
                    <span className="text-[#d4a843] font-bold">✓</span>
                    <span>{feat}</span>
                  </div>
                ))}
              </div>

              {/* Links Grid */}
              <div className="mt-6 pt-5 border-t border-slate-100 grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Documentation Link */}
                <a
                  href={prod.docLink}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-between bg-slate-900 hover:bg-[#0a1628] text-white p-4 rounded-xl shadow-sm transition group"
                >
                  <div>
                    <span className="text-[10px] text-[#d4a843] uppercase tracking-wider font-bold block">Documentation</span>
                    <span className="text-xs font-semibold text-white/90 group-hover:text-white mt-0.5 block">
                      {prod.docName}
                    </span>
                  </div>
                  <span className="text-xs font-bold text-[#d4a843] bg-white/10 group-hover:bg-[#d4a843] group-hover:text-[#0a1628] px-3 py-1.5 rounded-lg transition shrink-0 ml-2">
                    Open PDF ↗
                  </span>
                </a>

                {/* Demo Video Link */}
                <a
                  href={prod.demoLink}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-between bg-amber-500/10 hover:bg-amber-500/20 border border-[#d4a843]/40 p-4 rounded-xl transition group"
                >
                  <div>
                    <span className="text-[10px] text-amber-900 uppercase tracking-wider font-bold block">Demo Video</span>
                    <span className="text-xs font-semibold text-[#0a1628] mt-0.5 block">
                      {prod.demoName}
                    </span>
                  </div>
                  <span className="text-xs font-bold bg-[#0a1628] text-white group-hover:bg-[#d4a843] group-hover:text-[#0a1628] px-3 py-1.5 rounded-lg transition shrink-0 ml-2">
                    Watch Demo ↗
                  </span>
                </a>
              </div>
            </div>
          ))}
        </div>

        {/* Contact Banner */}
        <section className="bg-[#0a1628] text-white rounded-2xl p-8 border border-white/10 text-center">
          <h3 className="text-xl font-bold text-[#d4a843]">Interested in AAKS Solutions?</h3>
          <p className="text-xs md:text-sm text-white/80 mt-2 max-w-xl mx-auto leading-relaxed">
            Contact us for custom deployment, live demonstrations, and institutional licensing of NeuroSyn-Copilot, NeuroSyn-Dev, NeuroSyn-Aero, and NeuroSyn-SAP.
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
