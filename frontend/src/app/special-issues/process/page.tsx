import { notFound } from "next/navigation";
import { ContentPageView } from "@/components/ContentPageView";
import { getPageByTitle } from "@/lib/content-loader";

export default function SpecialIssueProcessPage() {
  const page = getPageByTitle("Special Issue Process");
  if (!page) notFound();
  return <ContentPageView page={page} />;
}
