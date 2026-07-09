import type { ContentBlock, ContentPage, ContentSection } from "@/lib/ijaike-content";

function renderBlock(block: ContentBlock, key: number) {
  switch (block.type) {
    case "paragraph":
      return <p key={key} className="mb-4 leading-relaxed text-slate-700">{block.text}</p>;
    case "list":
      return (
        <ul key={key} className="mb-4 list-disc space-y-1 pl-6 text-slate-700">
          {(block.items ?? []).map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      );
    case "formula":
      return (
        <div key={key} className="mb-4 rounded-sm border border-[#d4a843]/40 bg-[#0a1628]/5 px-4 py-3 font-mono text-sm text-[#0a1628]">
          {block.text}
        </div>
      );
    case "deadline":
      return (
        <p key={key} className="mb-4 inline-block rounded-sm bg-[#d4a843]/20 px-3 py-1 text-sm font-semibold text-[#0a1628]">
          {block.text}
        </p>
      );
    case "subsection":
      return (
        <div key={key} className="mb-5">
          {block.title && <h4 className="mb-2 font-semibold text-[#0a1628]">{block.title}</h4>}
          {block.text && <p className="mb-2 text-slate-700">{block.text}</p>}
          {block.additional && <p className="mb-2 text-slate-600">{block.additional}</p>}
          {block.items && (
            <ul className="mb-2 list-disc space-y-1 pl-6 text-slate-700">
              {block.items.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          )}
          {block.steps && (
            <ol className="mb-2 list-decimal space-y-1 pl-6 text-slate-700">
              {block.steps.map((step, i) => (
                <li key={i}>{step}</li>
              ))}
            </ol>
          )}
          {block.note && <p className="text-sm italic text-slate-500">Note: {block.note}</p>}
        </div>
      );
    case "article_type":
      return (
        <div key={key} className="mb-4 rounded-sm border border-slate-200 bg-slate-50 p-4">
          <h4 className="font-semibold text-[#0a1628]">{block.name as string}</h4>
          <dl className="mt-2 grid gap-1 text-sm text-slate-600 sm:grid-cols-2">
            {Object.entries(block)
              .filter(([k]) => !["type", "name"].includes(k))
              .map(([k, v]) => (
                <div key={k}>
                  <dt className="inline font-medium capitalize">{k.replace(/_/g, " ")}: </dt>
                  <dd className="inline">{String(v)}</dd>
                </div>
              ))}
          </dl>
        </div>
      );
    default:
      return block.text ? <p key={key} className="mb-4 text-slate-700">{block.text}</p> : null;
  }
}

function SectionBlock({ section }: { section: ContentSection }) {
  const heading = section.section_number
    ? `${section.section_number}. ${section.section_title}`
    : section.section_title;

  return (
    <section className="mb-10">
      <h3 className="mb-4 border-b border-[#d4a843]/40 pb-2 text-lg font-semibold text-[#0a1628]">
        {heading}
      </h3>
      {section.content.map((block, i) => renderBlock(block, i))}
    </section>
  );
}

interface Props {
  page: ContentPage;
  showChatLink?: boolean;
}

export function ContentPageView({ page, showChatLink = true }: Props) {
  return (
    <article className="mx-auto max-w-4xl px-4 py-10">
      <p className="text-xs font-semibold uppercase tracking-[0.15em] text-[#d4a843]">IJAIKE</p>
      <h1 className="mt-2 text-3xl font-semibold text-[#0a1628]">{page.page_title}</h1>
      {page.url && (
        <a href={page.url} target="_blank" rel="noopener noreferrer" className="mt-1 block text-sm text-slate-500 hover:text-[#d4a843]">
          {page.url}
        </a>
      )}
      {page.intro && <p className="mt-6 text-lg leading-relaxed text-slate-600">{page.intro}</p>}
      {page.note && (
        <p className="mt-4 rounded-sm border-l-4 border-[#d4a843] bg-amber-50 px-4 py-3 text-sm text-amber-900">
          {page.note}
        </p>
      )}

      <div className="mt-10">
        {page.sections.map((section, i) => (
          <SectionBlock key={i} section={section} />
        ))}
      </div>

      {showChatLink && (
        <div className="mt-10 rounded-sm bg-[#0a1628] p-6 text-white">
          <p className="font-semibold">Have questions about this section?</p>
          <p className="mt-1 text-sm text-white/70">Ask the JAIKE AI Assistant for instant, citation-backed answers.</p>
          <a href="/" className="mt-4 inline-block rounded-sm bg-[#d4a843] px-4 py-2 text-sm font-semibold text-[#0a1628] hover:bg-[#c49738]">
            Ask the Chatbot
          </a>
        </div>
      )}
    </article>
  );
}
