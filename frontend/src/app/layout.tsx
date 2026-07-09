import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { AuthProvider } from "@/lib/auth";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "IJAIKE AI Chatbot — JAIKE.org",
  description:
    "RAG-powered chatbot for IJAIKE journal. Ask about submission, APC, formatting, reviewer guidelines, and special issues — with citations from official documents.",
};

import { ChatWidget } from "@/components/ChatWidget";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable} h-full`}>
      <body className="flex min-h-full flex-col bg-slate-50 font-sans antialiased">
        <AuthProvider>
          <Header />
          <main className="flex flex-1 flex-col">{children}</main>
          <Footer />
          <ChatWidget />
        </AuthProvider>
      </body>
    </html>
  );
}
