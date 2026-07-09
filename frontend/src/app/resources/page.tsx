import Link from "next/link";
import { MANUSCRIPT_CENTRAL, SITE_NAV, SPECIAL_ISSUE_TOPICS } from "@/lib/ijaike-content";

/** Secondary resource hub — chatbot remains at `/` */
export default function ResourcesPage() {
  return (
    <>
      <section className="bg-[#0a1628] px-4 py-12 text-white">
        <div className="mx-auto max-w-4xl">
          <Link href="/" className="text-sm text-[#d4a843] hover:underline">← Back to Chatbot</Link>
          <h1 className="mt-4 text-2xl font-semibold">IJAIKE Guidelines &amp; Resources</h1>
          <p className="mt-2 text-white/70">
            Browse official policies below, or ask the AI chatbot on the home page for instant answers with citations.
          </p>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-12">
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {SITE_NAV.filter((g) => !["Chat", "Resources"].includes(g.label)).flatMap((group) =>
            group.items
              ? group.items.map((item) => 
                  item.href.startsWith("http") ? (
                    <a
                      key={item.href}
                      href={item.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="group rounded-sm border border-slate-200 bg-white p-6 shadow-sm hover:border-[#d4a843]/50"
                    >
                      <p className="text-xs font-semibold uppercase text-[#d4a843]">{group.label}</p>
                      <h3 className="mt-2 font-semibold text-[#0a1628] group-hover:text-[#d4a843]">{item.label}</h3>
                      {item.description && <p className="mt-2 text-sm text-slate-600">{item.description}</p>}
                    </a>
                  ) : (
                    <Link
                      key={item.href}
                      href={item.href}
                      className="group rounded-sm border border-slate-200 bg-white p-6 shadow-sm hover:border-[#d4a843]/50"
                    >
                      <p className="text-xs font-semibold uppercase text-[#d4a843]">{group.label}</p>
                      <h3 className="mt-2 font-semibold text-[#0a1628] group-hover:text-[#d4a843]">{item.label}</h3>
                      {item.description && <p className="mt-2 text-sm text-slate-600">{item.description}</p>}
                    </Link>
                  )
                )
              : group.href
                ? [
                    group.href.startsWith("http") ? (
                      <a
                        key={group.href}
                        href={group.href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="group rounded-sm border border-slate-200 bg-white p-6 shadow-sm hover:border-[#d4a843]/50"
                      >
                        <h3 className="font-semibold text-[#0a1628] hover:text-[#d4a843]">{group.label}</h3>
                      </a>
                    ) : (
                      <Link
                        key={group.href}
                        href={group.href}
                        className="group rounded-sm border border-slate-200 bg-white p-6 shadow-sm hover:border-[#d4a843]/50"
                      >
                        <h3 className="font-semibold text-[#0a1628]">{group.label}</h3>
                      </Link>
                    )
                  ]
                : [],
          )}
        </div>
      </section>

      <section className="bg-white px-4 py-12">
        <div className="mx-auto max-w-6xl">
          <h2 className="text-xl font-semibold text-[#0a1628]">Special Issue Topics</h2>
          <div className="mt-6 flex flex-wrap gap-2">
            {SPECIAL_ISSUE_TOPICS.map((topic) => (
              <Link key={topic} href="/special-issues/calls-for-papers" className="rounded-full border border-slate-200 bg-slate-50 px-4 py-1.5 text-sm hover:border-[#d4a843]">
                {topic}
              </Link>
            ))}
          </div>
          <a href={MANUSCRIPT_CENTRAL} target="_blank" rel="noopener noreferrer" className="mt-8 inline-block rounded-sm bg-[#d4a843] px-6 py-3 text-sm font-semibold text-[#0a1628]">
            Submit Manuscript
          </a>
        </div>
      </section>
    </>
  );
}
