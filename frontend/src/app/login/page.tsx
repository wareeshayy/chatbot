"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function LoginPage() {
  const { login, register, token, loading } = useAuth();
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (!loading && token) {
    router.replace("/");
    return null;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        await register(email, password, fullName);
      }
      router.push("/");
    } catch (err) {
      if (err instanceof ApiError && err.status === 0) {
        setError(err.message);
      } else {
        setError(
          err instanceof ApiError
            ? err.message
            : "Authentication failed — is the backend running and database seeded?",
        );
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex flex-1 items-center justify-center px-4 py-12">
      <div className="w-full max-w-md rounded-sm border border-slate-200 bg-white p-8 shadow-sm">
        <div className="mb-6 rounded-sm border border-[#d4a843]/40 bg-[#d4a843]/10 p-4">
          <p className="text-sm font-semibold text-[#0a1628]">No login needed for the chatbot</p>
          <p className="mt-1 text-xs text-slate-600">
            The IJAIKE AI chatbot works without signing in. Sign-in is optional for saved conversations.
          </p>
          <Link href="/" className="mt-3 inline-block text-sm font-medium text-[#d4a843] hover:underline">
            Go to Chatbot →
          </Link>
        </div>

        <h1 className="text-xl font-semibold text-[#0a1628]">
          {mode === "login" ? "Optional sign in" : "Create an account"}
        </h1>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          {mode === "register" && (
            <div>
              <label className="block text-xs font-medium text-slate-600">Full name</label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="mt-1 w-full rounded-sm border border-slate-300 px-3 py-2 text-sm outline-none focus:border-[#d4a843]"
              />
            </div>
          )}
          <div>
            <label className="block text-xs font-medium text-slate-600">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-sm border border-slate-300 px-3 py-2 text-sm outline-none focus:border-[#d4a843]"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-600">Password</label>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-sm border border-slate-300 px-3 py-2 text-sm outline-none focus:border-[#d4a843]"
            />
          </div>

          {error && (
            <div className="rounded-sm bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-sm bg-[#0a1628] py-2.5 text-sm font-medium text-white hover:bg-[#152a45] disabled:opacity-50"
          >
            {submitting ? "Please wait…" : mode === "login" ? "Sign in" : "Register"}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-slate-500">
          {mode === "login" ? "No account?" : "Already registered?"}{" "}
          <button
            type="button"
            onClick={() => setMode(mode === "login" ? "register" : "login")}
            className="font-medium text-[#0a1628] hover:underline"
          >
            {mode === "login" ? "Register" : "Sign in"}
          </button>
        </p>

        <div className="mt-6 rounded-sm bg-slate-50 p-3 text-xs text-slate-600">
          <p className="font-medium text-slate-700">Admin login requires backend setup:</p>
          <ol className="mt-2 list-decimal space-y-1 pl-4">
            <li>Start Docker Desktop</li>
            <li><code className="text-[11px]">docker compose -f docker/docker-compose.yml up -d</code></li>
            <li><code className="text-[11px]">cd backend &amp;&amp; .\setup-database.ps1</code></li>
            <li><code className="text-[11px]">uvicorn app.main:app --reload --port 8000</code></li>
          </ol>
          <p className="mt-2">Then: admin@ijaike.org / Admin@12345</p>
        </div>
      </div>
    </div>
  );
}
