"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api } from "@/lib/api";
import type { Citation, Message } from "@/lib/types";

interface AttachedFile {
  name: string;
  content: string;
  size: number;
  type: string;
}


function getDocUrl(title: string): string {
  const t = title.toLowerCase();
  if (t.includes("requirement")) return "https://ijaike.org/submission-requirements/";
  if (t.includes("procedure")) return "https://ijaike.org/submission-procedure/";
  if (t.includes("formatting")) return "https://ijaike.org/formatting-for-publication/";
  if (t.includes("anonymity")) return "https://ijaike.org/reviewer-anonymity-policy/";
  if (t.includes("reviewing")) return "https://ijaike.org/reviewing-process/";
  if (t.includes("special issue process")) return "https://ijaike.org/special-issue-process/";
  if (t.includes("cfp") || t.includes("call for papers")) return "https://ijaike.org/cfp-special-issues/";
  if (t.includes("apc") || t.includes("charges")) return "https://ijaike.org/article-processing-charges-apc/";
  if (t.includes("focus")) return "https://ijaike.org/journal-focus/";
  if (t.includes("scope")) return "https://ijaike.org/journal-scope/";
  if (t.includes("readership")) return "https://ijaike.org/journal-readership/";
  if (t.includes("subscription")) return "https://ijaike.org/subscription-information/";
  if (t.includes("editor-in-chief")) return "https://ijaike.org/about-the-editor-in-chief-2/";
  if (t.includes("associate editor")) return "https://ijaike.org/about-the-associate-editor/";
  if (t.includes("charter")) return "https://ijaike.org/editorial-charter/";
  if (t.includes("contact")) return "https://ijaike.org/contacts-us/";
  if (t.includes("aaks") || t.includes("association")) return "https://ijaike.org/association-for-the-advancement-of-knowledge-solutions-aaks/";
  if (t.includes("joseph")) return "https://ijaike.org/st-joseph-institute-of-technology/";
  if (t.includes("knowledge engineering")) return "https://ijaike.org/what-is-knowledge-engineering-ke/";
  if (t.includes("about jaike")) return "https://ijaike.org/about-jaike/";
  return "https://ijaike.org/";
}

interface ReferenceLink {
  label: string;
  url: string;
}

function getSuggestedLinks(answerText: string, userQuery: string): ReferenceLink[] {
  const links: ReferenceLink[] = [];
  const text = (answerText + " " + userQuery).toLowerCase();
  
  if (text.includes("format") || text.includes("style") || text.includes("template") || text.includes("publication") || text.includes("font") || text.includes("word") || text.includes("margin") || text.includes("page")) {
    links.push({ label: "Formatting Guidelines", url: "https://ijaike.org/formatting-for-publication/" });
  }
  if (text.includes("submit") || text.includes("manuscript") || text.includes("portal") || text.includes("central") || text.includes("subject line") || text.includes("send")) {
    links.push({ label: "Submission Requirements", url: "https://ijaike.org/submission-requirements/" });
    links.push({ label: "Manuscript Central Portal", url: "https://mc04.manuscriptcentral.com/jaike" });
  }
  if (text.includes("apc") || text.includes("fee") || text.includes("charge") || text.includes("waiver") || text.includes("cost") || text.includes("price") || text.includes("discount")) {
    links.push({ label: "Article Processing Charges (APC)", url: "https://ijaike.org/article-processing-charges-apc/" });
  }
  if (text.includes("review") || text.includes("double-blind") || text.includes("peer") || text.includes("referee") || text.includes("anonymity")) {
    links.push({ label: "Peer Review Process", url: "https://ijaike.org/reviewing-process/" });
  }
  if (text.includes("special issue") || text.includes("proposal") || text.includes("call for papers") || text.includes("cfp")) {
    links.push({ label: "Special Issue Process", url: "https://ijaike.org/special-issue-process/" });
  }
  if (text.includes("contact") || text.includes("email") || text.includes("support") || text.includes("office") || text.includes("help")) {
    links.push({ label: "Contact Us", url: "https://ijaike.org/contacts-us/" });
  }
  
  // If no specific links found, provide the official homepage
  if (links.length === 0) {
    links.push({ label: "IJAIKE Homepage", url: "https://ijaike.org/" });
  }
  
  // Deduplicate links by URL
  const seen = new Set<string>();
  return links.filter(link => {
    if (seen.has(link.url)) return false;
    seen.add(link.url);
    return true;
  }).slice(0, 3);
}


function makeMessage(
  role: Message["role"],
  content: string,
  citations?: Citation[] | null,
  attachedFile?: AttachedFile | null
): Message & { attachedFile?: AttachedFile | null } {
  return {
    id: crypto.randomUUID(),
    conversation_id: "public",
    role,
    content,
    citations: citations ?? null,
    created_at: new Date().toISOString(),
    attachedFile: attachedFile ? { ...attachedFile } : null,
  };
}

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [thinkingStatus, setThinkingStatus] = useState("Analyzing query & retrieving context...");
  const [error, setError] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Suggested questions from API
  const [suggested, setSuggested] = useState<{ id: string; question: string }[]>([]);

  // Active document citation artifact to show (overlay inside widget)
  const [activeArtifact, setActiveArtifact] = useState<Citation | null>(null);

  // File upload state
  const [attachedFile, setAttachedFile] = useState<AttachedFile | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Voice Speech-to-Text state
  const [recognizing, setRecognizing] = useState(false);
  const recognitionRef = useRef<any>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Load chat history from localStorage
  useEffect(() => {
    const saved = localStorage.getItem("ijaike_widget_messages");
    if (saved) {
      try {
        setMessages(JSON.parse(saved));
      } catch {
        // Clear corrupt history
      }
    }

    // Fetch suggested questions
    api
      .getSuggestedQuestions()
      .then(setSuggested)
      .catch(() =>
        setSuggested([
          { id: "1", question: "What are the formatting requirements for IJAIKE submissions?" },
          { id: "2", question: "How are Article Processing Charges calculated?" },
          { id: "3", question: "Are there APC discounts or waivers available?" },
          { id: "4", question: "Where do I submit my manuscript?" },
        ])
      );
  }, []);

  // Scroll to bottom on updates
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending, isOpen]);

  // Handle textarea auto-resize
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  // Cycle thinking reasoning statements dynamically
  useEffect(() => {
    if (!sending) {
      setThinkingStatus("Analyzing query & retrieving context...");
      return;
    }
    const states = [
      "Analyzing query & retrieving context...",
      "Reading retrieved segments...",
      "Reasoning about journal policies & rules...",
      "Structuring a detailed explanation...",
      "Polishing output and translations..."
    ];
    let idx = 0;
    const interval = setInterval(() => {
      idx = (idx + 1) % states.length;
      setThinkingStatus(states[idx]);
    }, 1800);
    return () => clearInterval(interval);
  }, [sending]);

  const saveMessages = (updated: Message[]) => {
    setMessages(updated);
    localStorage.setItem("ijaike_widget_messages", JSON.stringify(updated));
  };

  const clearChat = () => {
    if (confirm("Are you sure you want to clear your conversation history?")) {
      saveMessages([]);
      setActiveArtifact(null);
      setAttachedFile(null);
    }
  };

  const handleFileClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const fileType = file.name.split(".").pop() || "txt";
    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      setAttachedFile({
        name: file.name,
        size: file.size,
        type: fileType,
        content: text,
      });
    };
    reader.readAsText(file);
    e.target.value = "";
  };

  const runVoiceInput = () => {
    if (recognizing) {
      recognitionRef.current?.stop();
      setRecognizing(false);
      return;
    }

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in this browser. Try Google Chrome or Microsoft Edge.");
      return;
    }

    const rec = new SpeechRecognition();
    rec.continuous = false;
    rec.interimResults = false;
    rec.lang = "en-US";

    rec.onstart = () => setRecognizing(true);
    rec.onerror = () => setRecognizing(false);
    rec.onend = () => setRecognizing(false);
    rec.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      if (transcript) {
        setInput((prev) => (prev ? prev + " " + transcript : transcript));
      }
    };

    recognitionRef.current = rec;
    rec.start();
  };

  const send = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if ((!trimmed && !attachedFile) || sending) return;

      setSending(true);
      setError(null);
      setInput("");

      const userMsg = makeMessage("user", trimmed, null, attachedFile);
      const updatedMessages = [...messages, userMsg];
      saveMessages(updatedMessages);

      const promptContext = trimmed + (attachedFile
        ? `\n\n[Local Reference File: ${attachedFile.name}]\n${attachedFile.content}`
        : "");

      setAttachedFile(null);

      try {
        const history = messages.slice(-8).map((m) => ({
          role: m.role,
          content: m.content,
        }));

        const res = await api.askPublic(promptContext, history);
        const assistantMsg = makeMessage("assistant", res.answer, res.citations);
        saveMessages([...updatedMessages, assistantMsg]);
      } catch (e) {
        setError(
          e instanceof Error
            ? e.message
            : "Could not reach the chatbot API. Please check your backend connection."
        );
      } finally {
        setSending(false);
      }
    },
    [sending, messages, attachedFile]
  );

  const getFormattedArtifact = (art: Citation) => {
    const hasVector = art.embedding && Array.isArray(art.embedding);
    const vectorDim = hasVector ? art.embedding!.length : 0;
    const vectorPreview = hasVector
      ? [...art.embedding!.slice(0, 15), `... [truncated, total ${vectorDim} dimensions]`]
      : "No vector values available.";

    return {
      source_document: art.document_title,
      chunk_id: art.chunk_id || "N/A",
      relevance_score: art.relevance_score || 0,
      match_pct: art.relevance_score ? `${Math.round(art.relevance_score * 100)}%` : "N/A",
      page: art.page_number || "N/A",
      section: art.section || "N/A",
      extracted_excerpt: art.excerpt || "",
      chromadb_embeddings: vectorPreview,
    };
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 font-sans">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
        accept=".txt,.md,.js,.py,.json,.csv,.ts,.tsx,.css,.html"
      />

      {/* Chat Window Panel */}
      {isOpen && (
        <div className="mb-4 w-[92vw] sm:w-[400px] h-[80vh] max-h-[600px] border border-slate-200/80 bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-6 duration-200">
          {/* Header */}
          <div className="bg-[#0a1628] text-white px-4 py-3 flex items-center justify-between shadow-sm">
            <div className="flex items-center gap-3">
              <div className="h-9 w-9 rounded-full border border-[#d4a843] bg-[#d4a843]/10 text-[#d4a843] font-bold flex items-center justify-center text-base shrink-0 shadow-inner">
                J
              </div>
              <div className="text-left leading-tight">
                <p className="font-semibold text-sm text-white">IJAIKE Assistant</p>
                <span className="flex items-center gap-1.5 text-[11px] text-emerald-400">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  Replies instantly
                </span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {messages.length > 0 && (
                <button
                  type="button"
                  onClick={clearChat}
                  className="rounded-lg p-1.5 text-white/70 hover:bg-white/10 hover:text-white"
                  title="Clear chat history"
                >
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              )}
              <button
                type="button"
                onClick={() => {
                  setIsOpen(false);
                  setActiveArtifact(null);
                }}
                className="rounded-lg p-1.5 text-white/70 hover:bg-white/10 hover:text-white"
                title="Close chat window"
              >
                ✕
              </button>
            </div>
          </div>



          {/* Messages Feed */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50 relative select-text">
            {messages.length === 0 ? (
              <div className="text-center pt-8 pb-4">
                <div className="mx-auto flex h-11 w-11 items-center justify-center rounded-full border-2 border-[#d4a843] text-lg font-bold text-[#d4a843] mb-3 bg-[#d4a843]/5">
                  J
                </div>
                <h3 className="font-semibold text-slate-800 text-sm mb-1">Ask about IJAIKE</h3>
                <p className="text-xs text-slate-500 max-w-xs mx-auto mb-4.5 px-3">
                  I can help you with submissions, APC fees, formatting guidelines, peer review, and special issues.
                </p>

                {/* Suggested Questions Grid */}
                <div className="space-y-1.5 px-2">
                  {suggested.map((q) => (
                    <button
                      key={q.id}
                      onClick={() => send(q.question)}
                      className="w-full p-2.5 text-left text-xs rounded-xl bg-white border border-slate-200/80 hover:bg-slate-55 hover:border-slate-350 transition text-slate-650 font-medium shadow-sm hover:shadow"
                    >
                      {q.question}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((m, idx) => {
                  const isUser = m.role === "user";
                  const customMsg = m as Message & { attachedFile?: AttachedFile | null };
                  const userQuery = !isUser && idx > 0 ? messages[idx - 1].content : "";
                  const suggestedLinks = !isUser ? getSuggestedLinks(m.content, userQuery) : [];

                  return (
                    <div
                      key={m.id}
                      className={`flex gap-2.5 ${isUser ? "justify-end text-right" : "justify-start text-left"}`}
                    >
                      {!isUser && (
                        <div className="h-6.5 w-6.5 rounded-full border border-[#d4a843]/80 bg-[#d4a843]/10 text-[#d4a843] font-bold text-[10px] flex items-center justify-center shrink-0 shadow-sm select-none">
                          J
                        </div>
                      )}

                      <div className="max-w-[85%]">
                        {isUser ? (
                          <div className="space-y-1 inline-block text-left">
                            {customMsg.attachedFile && (
                              <div className="flex items-center gap-1.5 bg-slate-200 border border-slate-300 rounded-lg px-2 py-1 text-[10px] text-slate-700 max-w-sm mb-1 ml-auto">
                                <span className="font-mono bg-slate-300 px-1 rounded text-[8px] font-bold text-slate-800">
                                  {customMsg.attachedFile.type.toUpperCase()}
                                </span>
                                <span className="truncate max-w-[120px] font-medium">
                                  {customMsg.attachedFile.name}
                                </span>
                              </div>
                            )}
                            {m.content && (
                              <div className="rounded-2xl px-3 py-2 text-xs leading-relaxed bg-[#0a1628] text-white">
                                {m.content}
                              </div>
                            )}
                          </div>
                        ) : (
                          <div className="space-y-2">
                            <div className="rounded-2xl px-3.5 py-2.5 text-xs leading-relaxed bg-white border border-slate-200 text-slate-880 shadow-sm font-sans relative group">
                              <ReactMarkdown
                                remarkPlugins={[remarkGfm]}
                                components={{
                                  p: ({ children }) => <p className="mb-2 leading-relaxed text-slate-700">{children}</p>,
                                  strong: ({ children }) => <strong className="font-semibold text-slate-900">{children}</strong>,
                                  ul: ({ children }) => <ul className="list-disc pl-4 my-1.5 space-y-1 text-slate-650">{children}</ul>,
                                  ol: ({ children }) => <ol className="list-decimal pl-4 my-1.5 space-y-1 text-slate-650">{children}</ol>,
                                  li: ({ children }) => <li className="mb-0.5">{children}</li>,
                                  h1: ({ children }) => <h1 className="text-sm font-bold mt-3 mb-1 text-slate-900">{children}</h1>,
                                  h2: ({ children }) => <h2 className="text-sm font-bold mt-2.5 mb-1 text-slate-900">{children}</h2>,
                                  h3: ({ children }) => <h3 className="text-xs font-bold mt-2 mb-0.5 text-slate-900">{children}</h3>,
                                  code: (props) => {
                                    const { children, className, ...rest } = props;
                                    const isInline = !className;
                                    if (isInline) {
                                      return (
                                        <code className="bg-slate-100 rounded px-1 text-[11px] font-mono text-[#d40043]" {...rest}>
                                          {children}
                                        </code>
                                      );
                                    }
                                    return (
                                      <pre className="bg-slate-900 p-2 rounded text-[10px] font-mono my-2 overflow-x-auto text-[#d4a843]">
                                        <code className={className} {...rest}>
                                          {children}
                                        </code>
                                      </pre>
                                    );
                                  }
                                }}
                              >
                                {m.content}
                              </ReactMarkdown>

                              {/* Copy button */}
                              <button
                                type="button"
                                onClick={() => handleCopy(m.id, m.content)}
                                className="absolute top-2 right-2 p-1.5 rounded-lg border border-slate-100 bg-white hover:bg-slate-50 text-slate-400 hover:text-slate-600 shadow-sm transition opacity-0 group-hover:opacity-100"
                                title="Copy reply"
                              >
                                {copiedId === m.id ? (
                                  <svg className="h-3.5 w-3.5 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                  </svg>
                                ) : (
                                  <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                                  </svg>
                                )}
                              </button>
                            </div>

                            {/* Reference Links inside Widget */}
                            {m.citations && m.citations.length > 0 && (
                              <div className="flex flex-wrap gap-1.5 px-1 select-none mt-2">
                                {m.citations.slice(0, 3).map((c, idx) => {
                                  const liveUrl = getDocUrl(c.document_title);
                                  return (
                                    <a
                                      key={idx}
                                      href={liveUrl}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 hover:text-[#d4a843] transition text-[10px] font-medium shadow-sm"
                                      title="Open official webpage on ijaike.org"
                                    >
                                      <span>📖 {c.document_title.replace("IJAIKE — ", "").replace("IJAIKE - ", "").replace("JAIKE - ", "").replace("JAIKE — ", "")}</span>
                                      {c.page_number && <span className="text-slate-400 font-normal">p.{c.page_number}</span>}
                                    </a>
                                  );
                                })}
                              </div>
                            )}
                            {/* Suggested Reference Links */}
                            {suggestedLinks.length > 0 && (
                              <div className="flex flex-wrap gap-1.5 px-1 select-none mt-2">
                                {suggestedLinks.map((link, idx) => (
                                  <a
                                    key={idx}
                                    href={link.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-[#d4a843]/30 bg-white hover:bg-slate-50 text-slate-700 hover:text-[#d4a843] transition text-[10px] font-medium shadow-sm"
                                    title={`Open ${link.label} on ijaike.org`}
                                  >
                                    <span>🔗 {link.label}</span>
                                  </a>
                                ))}
                              </div>
                            )}
                          </div>

                        )}
                      </div>
                    </div>
                  );
                })}

                {sending && (
                  <div className="flex gap-2.5 justify-start">
                    <div className="h-6.5 w-6.5 rounded-full border border-[#d4a843]/80 bg-[#d4a843]/10 text-[#d4a843] font-bold text-[10px] flex items-center justify-center shrink-0 animate-pulse">
                      J
                    </div>
                    <div className="rounded-2xl bg-white border border-slate-200 px-3 py-2 text-[10px] text-slate-500 shadow-sm flex items-center gap-1.5 animate-pulse">
                      <svg className="animate-spin h-3.5 w-3.5 text-[#d4a843] shrink-0" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <span>{thinkingStatus}</span>
                    </div>
                  </div>
                )}

                {error && (
                  <div className="rounded-xl bg-red-50 border border-red-200 p-2.5 text-[10px] text-red-700 text-left">
                    {error}
                  </div>
                )}
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Footer */}
          <div className="p-3 border-t border-slate-100 bg-white">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                send(input);
              }}
              className="flex flex-col border border-slate-200 rounded-xl bg-slate-50 focus-within:bg-white focus-within:border-slate-350 transition duration-150"
            >
              {attachedFile && (
                <div className="flex items-center justify-between bg-slate-100 border border-slate-200 rounded px-2.5 py-1 text-[10px] text-slate-600 m-2 self-start max-w-[200px]">
                  <span className="truncate max-w-[120px] font-medium">{attachedFile.name}</span>
                  <button
                    type="button"
                    onClick={() => setAttachedFile(null)}
                    className="text-slate-400 hover:text-red-500 ml-1.5 font-bold"
                  >
                    ✕
                  </button>
                </div>
              )}

              <div className="flex items-end px-2 py-1">
                <textarea
                  ref={textareaRef}
                  rows={1}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask IJAIKE Assistant..."
                  disabled={sending}
                  className="flex-1 bg-transparent border-0 outline-none text-xs text-slate-800 resize-none py-1.5 px-1 min-h-[30px] leading-relaxed max-h-[120px]"
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      send(input);
                    }
                  }}
                />

                <div className="flex items-center gap-1 py-1 text-slate-400">
                  {/* File attach button */}
                  <button
                    type="button"
                    onClick={handleFileClick}
                    className="p-1 rounded-md hover:bg-slate-250 hover:text-slate-700 transition"
                    title="Attach text file"
                  >
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                  </button>

                  {/* Mic speech recognition */}
                  <button
                    type="button"
                    onClick={runVoiceInput}
                    className={`p-1 rounded-md transition ${
                      recognizing
                        ? "bg-red-50 text-red-500 animate-pulse border border-red-200"
                        : "hover:bg-slate-250 hover:text-slate-700"
                    }`}
                    title={recognizing ? "Listening..." : "Speech input"}
                  >
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </svg>
                  </button>

                  {/* Send button */}
                  <button
                    type="submit"
                    disabled={(!input.trim() && !attachedFile) || sending}
                    className="p-1.5 rounded-lg bg-[#0a1628] hover:bg-[#d4a843] text-white hover:text-[#0a1628] disabled:bg-slate-200 disabled:text-slate-400 transition"
                  >
                    <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path d="M6 12L20 4L16 20L12 14L6 12Z" fill="currentColor" />
                    </svg>
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Floating launcher toggle button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="h-14 w-14 rounded-full bg-[#0a1628] hover:bg-[#d4a843] text-[#d4a843] hover:text-[#0a1628] flex items-center justify-center shadow-xl hover:scale-105 transition-all duration-200 relative group animate-bounce-slow"
        style={{
          boxShadow: "0 8px 30px rgba(10, 22, 40, 0.35)",
        }}
        title="IJAIKE AI Assistant"
      >
        {isOpen ? (
          <span className="text-xl font-bold font-sans">✕</span>
        ) : (
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        )}
      </button>
    </div>
  );
}
