import Link from "next/link";
import { ContentPageView } from "@/components/ContentPageView";
import { APCEstimator } from "@/components/APCEstimator";
import { getPageByTitle } from "@/lib/content-loader";

export default function APCPage() {
  const page = getPageByTitle("Article Processing Charges (APC)");

  return (
    <>
      {page && <ContentPageView page={page} showChatLink={false} />}
      <section className="border-t border-slate-200 bg-slate-50 px-4 py-12">
        <div className="mx-auto max-w-2xl">
          <h2 className="text-xl font-semibold text-[#0a1628]">APC Estimator Tool</h2>
          <p className="mt-2 text-sm text-slate-600">
            Calculate an estimated Article Processing Charge based on article type, page count, and author category.
          </p>
          <div className="mt-6">
            <APCEstimator />
          </div>
          <p className="mt-6 text-center text-sm text-slate-500">
            Need help? <Link href="/" className="text-[#d4a843] hover:underline">Ask the Chatbot</Link>
          </p>
        </div>
      </section>
    </>
  );
}
