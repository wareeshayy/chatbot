"use client";

import { useState, ChangeEvent } from "react";

interface Props {
  documentTitle: string;
  pdfFileName: string;
  pdfUrl?: string;
}

export function DocumentViewerUploader({ documentTitle, pdfFileName, pdfUrl }: Props) {
  const [uploadedFile, setUploadedFile] = useState<{ name: string; size: string; date: string } | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const handleFileUpload = (file: File) => {
    setIsUploading(true);
    setTimeout(() => {
      const sizeMb = (file.size / (1024 * 1024)).toFixed(2);
      setUploadedFile({
        name: file.name,
        size: `${sizeMb} MB`,
        date: new Date().toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }),
      });
      setIsUploading(false);
    }, 600);
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="my-8 rounded-xl border border-slate-200 bg-slate-50/80 p-6 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <span className="inline-block bg-[#0a1628] text-[#d4a843] text-[10px] uppercase font-bold tracking-wider px-2.5 py-0.5 rounded">
            Official PDF Document
          </span>
          <h3 className="text-base font-bold text-[#0a1628] mt-1">{documentTitle}</h3>
          <p className="text-xs text-slate-500 mt-0.5">
            {uploadedFile ? `Custom Version: ${uploadedFile.name} (${uploadedFile.size})` : `File: ${pdfFileName}`}
          </p>
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

      {/* Upload Zone */}
      <div className="mt-4">
        <p className="text-xs font-semibold text-slate-700 mb-2">Upload Updated Document / Replacement Copy:</p>
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-lg p-4 text-center transition ${
            dragActive ? "border-[#d4a843] bg-amber-50/50" : "border-slate-300 hover:border-[#d4a843] bg-white"
          }`}
        >
          <input
            type="file"
            id={`file-upload-${pdfFileName.replace(/[^a-zA-Z0-9]/gi, "")}`}
            className="hidden"
            accept=".pdf,.docx,.doc"
            onChange={handleInputChange}
          />
          <label
            htmlFor={`file-upload-${pdfFileName.replace(/[^a-zA-Z0-9]/gi, "")}`}
            className="cursor-pointer flex flex-col items-center justify-center gap-1"
          >
            <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <span className="text-xs font-medium text-[#0a1628]">
              {isUploading ? "Uploading file..." : "Click to select or drag & drop a PDF / Word file here"}
            </span>
            <span className="text-[10px] text-slate-400">Supports .pdf, .docx, .doc (Max 25MB)</span>
          </label>
        </div>

        {uploadedFile && (
          <div className="mt-3 flex items-center gap-2 text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-lg p-2.5">
            <svg className="w-4 h-4 text-emerald-600 shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span>
              <strong>Uploaded:</strong> {uploadedFile.name} ({uploadedFile.size}) on {uploadedFile.date}.
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
