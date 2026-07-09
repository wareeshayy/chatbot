"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export function Footer() {
  const pathname = usePathname();

  return (
    <footer className="mt-auto border-t border-slate-200 bg-[#0a1628] text-white">
      <div className="mx-auto grid max-w-6xl gap-8 px-4 py-10 md:grid-cols-3">
        <div>
          <p className="text-lg font-semibold text-[#d4a843]">JAIKE</p>
          <p className="mt-2 text-sm text-white/70">
            Peer-reviewed, open-access journal for AI, Knowledge Engineering, and IoT research.
          </p>
        </div>
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-white/90">Quick Links</p>
          <ul className="mt-3 space-y-2 text-sm text-white/70">
            <li>
              <Link href="/" className="hover:text-[#d4a843]">Home</Link>
            </li>
            <li>
              <Link href="/apc" className="hover:text-[#d4a843]">APC Estimator</Link>
            </li>
            <li>
              <a href="https://ijaike.org/submission-requirements/" target="_blank" rel="noopener noreferrer" className="hover:text-[#d4a843]">
                Submission Requirements
              </a>
            </li>
            <li>
              <a href="https://mc04.manuscriptcentral.com/jaike" target="_blank" rel="noopener noreferrer" className="hover:text-[#d4a843]">
                Manuscript Central
              </a>
            </li>
          </ul>
        </div>
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-white/90">Contact</p>
          <ul className="mt-3 space-y-2 text-sm text-white/70">
            <li>editor-in-chief@ijaike.org</li>
            <li>Redondo Beach, California, USA</li>
            <li>
              <a href="https://ijaike.org" target="_blank" rel="noopener noreferrer" className="hover:text-[#d4a843]">
                https://ijaike.org
              </a>
            </li>
          </ul>
        </div>
      </div>
      <div className="border-t border-white/10 py-4 text-center text-xs text-white/50">
        Copyright {new Date().getFullYear()} IJAIKE — All Rights Reserved
      </div>
    </footer>
  );
}
