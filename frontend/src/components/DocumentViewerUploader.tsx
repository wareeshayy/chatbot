interface Props {
  documentTitle: string;
  pdfFileName: string;
  pdfUrl?: string;
}

export function DocumentViewerUploader({ documentTitle, pdfFileName, pdfUrl }: Props) {
  return (
    <div className="my-8 rounded-xl border border-slate-200 bg-slate-50/80 p-6 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="inline-block bg-[#0a1628] text-[#d4a843] text-[10px] uppercase font-bold tracking-wider px-2.5 py-0.5 rounded">
            Official PDF Document
          </span>
          <h3 className="text-base font-bold text-[#0a1628] mt-1">{documentTitle}</h3>
          <p className="text-xs text-slate-500 mt-0.5">File: {pdfFileName}</p>
        </div>
        <div className="flex items-center gap-3">
          {pdfUrl && (
            <a
              href={pdfUrl}
              download={pdfFileName}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 rounded-lg bg-[#0a1628] px-4 py-2 text-xs font-semibold text-white shadow hover:bg-[#142847] transition shrink-0"
            >
              <svg className="w-4 h-4 text-[#d4a843]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download PDF
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
