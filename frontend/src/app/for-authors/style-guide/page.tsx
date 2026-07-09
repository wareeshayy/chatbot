import { notFound } from "next/navigation";
import { ContentPageView } from "@/components/ContentPageView";
import { getPageByTitle } from "@/lib/content-loader";

export default function StyleGuidePage() {
  const page = getPageByTitle("Journal Article Types and Style Guide");
  if (!page) notFound();
  return <ContentPageView page={page} />;
}
