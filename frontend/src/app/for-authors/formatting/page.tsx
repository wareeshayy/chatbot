import Link from "next/link";
import { ContentPageView } from "@/components/ContentPageView";
import { getPageByTitle } from "@/lib/content-loader";

export default function FormattingPage() {
  const page = getPageByTitle("Journal Article Types and Style Guide");
  if (!page) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-16 text-center">
        <h1 className="text-2xl font-semibold text-[#0a1628]">Formatting for Publication</h1>
        <p className="mt-4 text-slate-600">See the IJAIKE Formatting PDF in the knowledge base or ask the AI Assistant.</p>
        <Link href="/" className="mt-6 inline-block text-[#d4a843] hover:underline">Ask the Chatbot →</Link>
      </div>
    );
  }

  return (
    <>
      <div className="border-b border-slate-200 bg-white px-4 py-6">
        <div className="mx-auto max-w-4xl">
          <p className="text-xs font-semibold uppercase tracking-wide text-[#d4a843]">For Authors</p>
          <h1 className="mt-1 text-2xl font-semibold text-[#0a1628]">Formatting for Publication</h1>
          <p className="mt-2 text-sm text-slate-600">
            Official Word formatting requirements. PDF submissions are not accepted for initial submission.
          </p>
        </div>
      </div>
      <ContentPageView page={page} showChatLink />
    </>
  );
}
