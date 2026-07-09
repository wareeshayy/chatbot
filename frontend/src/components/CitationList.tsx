import type { Citation } from "@/lib/types";

function getDocUrl(title: string): string | null {
  const t = title.toLowerCase();
  if (t.includes("requirement")) return "https://ijaike.org/submission-requirements/";
  if (t.includes("procedure")) return "https://ijaike.org/submission-procedure/";
  if (t.includes("formatting")) return "https://ijaike.org/formatting-for-publication/";
  if (t.includes("anonymity")) return "https://ijaike.org/reviewer-anonymity-policy/";
  if (t.includes("reviewing")) return "https://ijaike.org/reviewing-process/";
  if (t.includes("special issue process")) return "https://ijaike.org/special-issue-process/";
  if (t.includes("cfp") || t.includes("call for papers")) return "https://ijaike.org/cfp-special-issues/";
  if (t.includes("apc") || t.includes("charges")) return "https://ijaike.org/article-processing-charges-apc/";
  if (t.includes("focus")) return "https://ijaike.org/journal-focus/";
  if (t.includes("scope")) return "https://ijaike.org/journal-scope/";
  if (t.includes("readership")) return "https://ijaike.org/journal-readership/";
  if (t.includes("subscription")) return "https://ijaike.org/subscription-information/";
  if (t.includes("editor-in-chief")) return "https://ijaike.org/about-the-editor-in-chief-2/";
  if (t.includes("associate editor")) return "https://ijaike.org/about-the-associate-editor/";
  if (t.includes("charter")) return "https://ijaike.org/editorial-charter/";
  if (t.includes("contact")) return "https://ijaike.org/contacts-us/";
  if (t.includes("aaks") || t.includes("association")) return "https://ijaike.org/association-for-the-advancement-of-knowledge-solutions-aaks/";
  if (t.includes("joseph")) return "https://ijaike.org/st-joseph-institute-of-technology/";
  if (t.includes("knowledge engineering")) return "https://ijaike.org/what-is-knowledge-engineering-ke/";
  if (t.includes("about jaike")) return "https://ijaike.org/about-jaike/";
  return null;
}

export function CitationList({ citations }: { citations: Citation[] }) {
  if (!citations.length) return null;

  return (
    <div className="mt-3 border-t border-slate-200 pt-3">
      <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
        Sources
      </p>
      <ul className="space-y-2">
        {citations.map((c, i) => {
          const liveUrl = getDocUrl(c.document_title);
          return (
            <li
              key={c.chunk_id ?? i}
              className="rounded-md border border-slate-100 bg-slate-50 px-3 py-2 text-xs text-slate-600"
            >
              <div className="flex items-start justify-between">
                <p className="font-medium text-[#0a1628]">
                  {c.document_title}
                  {c.page_number ? ` — p. ${c.page_number}` : ""}
                  {c.relevance_score != null && (
                    <span className="ml-2 font-normal text-slate-400">
                      ({Math.round(c.relevance_score * 100)}% match)
                    </span>
                  )}
                </p>
                {liveUrl && (
                  <a
                    href={liveUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-[#d4a843] hover:text-[#c49738] font-semibold flex items-center gap-0.5 ml-2 whitespace-nowrap"
                    title="Open official webpage on ijaike.org"
                  >
                    Open Page ↗
                  </a>
                )}
              </div>
              {c.excerpt && <p className="mt-1 line-clamp-2 italic">{c.excerpt}</p>}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
