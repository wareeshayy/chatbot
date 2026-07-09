import { notFound } from "next/navigation";
import { ContentPageView } from "@/components/ContentPageView";
import { getPageByTitle } from "@/lib/content-loader";

export default function AnonymityPolicyPage() {
  const page = getPageByTitle("Reviewer Anonymity Policy");
  if (!page) notFound();
  return <ContentPageView page={page} />;
}
