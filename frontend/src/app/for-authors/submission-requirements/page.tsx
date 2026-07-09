import { notFound } from "next/navigation";
import { ContentPageView } from "@/components/ContentPageView";
import { getPageByTitle } from "@/lib/content-loader";

export default function SubmissionRequirementsPage() {
  const page = getPageByTitle("Submission Requirements");
  if (!page) notFound();
  return <ContentPageView page={page} />;
}
