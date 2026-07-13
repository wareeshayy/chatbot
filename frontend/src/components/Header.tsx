"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { MANUSCRIPT_CENTRAL, SITE_NAV } from "@/lib/ijaike-content";
import { useAuth } from "@/lib/auth";

export function Header() {
  const { user, logout } = useAuth();
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);

  const isActive = (href: string) => pathname === href || pathname.startsWith(href + "/");

  return (
    <header className="bg-[#0a1628] text-white">
      <div className="border-b border-white/10">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-2 px-4 py-2 text-xs text-white/70">
          <span className="text-[20px] font-semibold text-white tracking-wide leading-tight">International Journal of Artificial Intelligence &amp; Knowledge Engineering</span>
          <a href="https://ijaike.org" target="_blank" rel="noopener noreferrer" className="hover:text-[#d4a843] shrink-0">
            ijaike.org
          </a>
        </div>
      </div>

      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
        <Link href="/" className="flex items-center gap-3">
          <img src="/journal_logo.png" alt="JAIKE Logo" className="h-11 w-11 object-contain rounded-sm bg-white p-0.5" />
          <div>
            <p className="text-lg font-semibold tracking-wide">JAIKE</p>
            <p className="hidden text-xs text-white/60 sm:block">Publishing Tomorrow&apos;s Intelligence Today</p>
          </div>
        </Link>

        <button
          type="button"
          className="rounded border border-white/20 px-3 py-1 text-sm md:hidden"
          onClick={() => setMobileOpen(!mobileOpen)}
        >
          Menu
        </button>

        <nav className="hidden items-center gap-1 text-sm md:flex">
          {SITE_NAV.map((group) =>
            group.items ? (
              <div
                key={group.label}
                className="relative"
                onMouseEnter={() => setOpenDropdown(group.label)}
                onMouseLeave={() => setOpenDropdown(null)}
              >
                <button
                  type="button"
                  className={`px-3 py-2 ${group.items.some((i) => isActive(i.href)) ? "text-[#d4a843]" : "text-white/80 hover:text-[#d4a843]"}`}
                >
                  {group.label} ▾
                </button>
                {openDropdown === group.label && (
                  <div className="absolute left-0 top-full z-50 min-w-[260px] rounded-sm border border-white/10 bg-[#0f1f35] py-2 shadow-xl">
                    {group.items.map((item) => 
                      item.href.startsWith("http") ? (
                        <a
                          key={item.href}
                          href={item.href}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block px-4 py-2 hover:bg-white/5 text-left"
                        >
                          <span className="block text-white/90">{item.label}</span>
                          {item.description && (
                            <span className="block text-xs text-white/50">{item.description}</span>
                          )}
                        </a>
                      ) : (
                        <Link
                          key={item.href}
                          href={item.href}
                          className="block px-4 py-2 hover:bg-white/5 text-left"
                        >
                          <span className="block text-white/90">{item.label}</span>
                          {item.description && (
                            <span className="block text-xs text-white/50">{item.description}</span>
                          )}
                        </Link>
                      )
                    )}
                  </div>
                )}
              </div>
            ) : (
              group.href!.startsWith("http") ? (
                <a
                  key={group.label}
                  href={group.href!}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-2 text-white/80 hover:text-[#d4a843]"
                >
                  {group.label}
                </a>
              ) : (
                <Link
                  key={group.label}
                  href={group.href!}
                  className={`px-3 py-2 ${isActive(group.href!) ? "text-[#d4a843]" : "text-white/80 hover:text-[#d4a843]"}`}
                >
                  {group.label}
                </Link>
              )
            ),
          )}
          <a
            href={MANUSCRIPT_CENTRAL}
            target="_blank"
            rel="noopener noreferrer"
            className="ml-2 rounded-sm bg-[#d4a843] px-4 py-2 font-medium text-[#0a1628] hover:bg-[#c49738]"
          >
            Submit
          </a>
          {user ? (
            <button type="button" onClick={logout} className="ml-2 px-3 py-2 text-white/70 hover:text-white">
              Log out
            </button>
          ) : (
            <Link href="/login" className="ml-2 px-3 py-2 text-white/70 hover:text-white">
              Sign in
            </Link>
          )}
        </nav>
      </div>

      {mobileOpen && (
        <div className="border-t border-white/10 px-4 py-4 md:hidden text-left">
          {SITE_NAV.map((group) => (
            <div key={group.label} className="mb-3">
              {group.href ? (
                group.href.startsWith("http") ? (
                  <a
                    href={group.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block py-1 font-medium text-white/90 hover:text-[#d4a843]"
                    onClick={() => setMobileOpen(false)}
                  >
                    {group.label}
                  </a>
                ) : (
                  <Link href={group.href} className="block py-1 font-medium" onClick={() => setMobileOpen(false)}>
                    {group.label}
                  </Link>
                )
              ) : (
                <>
                  <p className="py-1 font-medium text-[#d4a843]">{group.label}</p>
                  {group.items?.map((item) => (
                    item.href.startsWith("http") ? (
                      <a
                        key={item.href}
                        href={item.href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block py-1 pl-3 text-sm text-white/80 hover:text-[#d4a843]"
                        onClick={() => setMobileOpen(false)}
                      >
                        {item.label}
                      </a>
                    ) : (
                      <Link
                        key={item.href}
                        href={item.href}
                        className="block py-1 pl-3 text-sm text-white/80"
                        onClick={() => setMobileOpen(false)}
                      >
                        {item.label}
                      </Link>
                    )
                  ))}
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </header>
  );
}
