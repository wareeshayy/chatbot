"use client";

import { FormEvent, useState } from "react";
import { api } from "@/lib/api";
import type { APCEstimateResponse } from "@/lib/types";

const PAPER_TYPES = [
  { value: "standard_article", label: "Standard Article (20 pages — $1,000)" },
  { value: "short_paper", label: "Short Paper (≤15 pages — $750)" },
  { value: "review_article", label: "Review Article (30 pages — $1,500)" },
  { value: "long_paper", label: "Long Paper (40 pages — $2,000)" },
  { value: "research_article", label: "Research Article ($49/page)" },
];

const AUTHOR_CATEGORIES = [
  { value: "regular", label: "Regular author" },
  { value: "special_issue_early", label: "Special issue — early submission (50% off)" },
  { value: "phd_candidate", label: "Ph.D. candidate without funding (50% waiver)" },
  { value: "institutional_partner", label: "Institutional partner (30% off)" },
  { value: "student", label: "Student (25% off)" },
];

export function APCEstimator() {
  const [paperType, setPaperType] = useState("standard_article");
  const [numPages, setNumPages] = useState(20);
  const [authorCategory, setAuthorCategory] = useState("regular");
  const [result, setResult] = useState<APCEstimateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const estimate = await api.estimateAPC({
        paper_type: paperType,
        num_pages: numPages,
        author_category: authorCategory,
      });
      setResult(estimate);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Estimation failed — is the backend running?");
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <form onSubmit={handleSubmit} className="space-y-4 rounded-sm border border-slate-200 bg-white p-6 shadow-sm">
        <div>
          <label className="block text-xs font-medium text-slate-600">Article type</label>
          <select
            value={paperType}
            onChange={(e) => setPaperType(e.target.value)}
            className="mt-1 w-full rounded-sm border border-slate-300 px-3 py-2 text-sm"
          >
            {PAPER_TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-600">Number of pages</label>
          <input
            type="number"
            min={1}
            max={500}
            value={numPages}
            onChange={(e) => setNumPages(Number(e.target.value))}
            className="mt-1 w-full rounded-sm border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-600">Author category</label>
          <select
            value={authorCategory}
            onChange={(e) => setAuthorCategory(e.target.value)}
            className="mt-1 w-full rounded-sm border border-slate-300 px-3 py-2 text-sm"
          >
            {AUTHOR_CATEGORIES.map((c) => (
              <option key={c.value} value={c.value}>{c.label}</option>
            ))}
          </select>
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-sm bg-[#d4a843] py-2.5 text-sm font-semibold text-[#0a1628] hover:bg-[#c49738] disabled:opacity-50"
        >
          {loading ? "Calculating…" : "Calculate APC"}
        </button>
      </form>

      {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

      {result && (
        <div className="mt-6 rounded-sm border border-[#d4a843]/30 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-[#0a1628]">Estimated APC</h3>
          <p className="mt-2 text-3xl font-bold text-[#0a1628]">
            ${Number(result.total).toFixed(2)} {result.currency}
          </p>
          <p className="mt-3 whitespace-pre-wrap text-sm text-slate-600">{result.breakdown}</p>
          {result.requires_waiver_approval && (
            <p className="mt-3 rounded-sm bg-amber-50 px-3 py-2 text-xs text-amber-800">
              This discount requires editorial approval (waiver request).
            </p>
          )}
        </div>
      )}
    </>
  );
}
