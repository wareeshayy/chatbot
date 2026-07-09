import type { ContentPage } from "@/lib/ijaike-content";
import knowledge from "@/data/ijaike_knowledge.json";

const pages = (knowledge as { pages: ContentPage[] }).pages;

export function getPageByTitle(title: string): ContentPage | undefined {
  return pages.find((p) => p.page_title === title);
}

export function getAllPages(): ContentPage[] {
  return pages;
}
