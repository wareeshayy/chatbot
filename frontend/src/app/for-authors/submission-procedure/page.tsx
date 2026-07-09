import { notFound } from "next/navigation";
import { ContentPageView } from "@/components/ContentPageView";
import { getPageByTitle } from "@/lib/content-loader";

export default function SubmissionProcedurePage() {
  const page = getPageByTitle("Submission Procedure");
  if (!page) notFound();
  return <ContentPageView page={page} />;
}
