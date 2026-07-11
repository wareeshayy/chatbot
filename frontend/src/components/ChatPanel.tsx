"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api } from "@/lib/api";
import type { Citation, Message } from "@/lib/types";

interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  created_at: string;
  model_used?: string;
}

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

export function ChatPanel() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string>("");
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [thinkingStatus, setThinkingStatus] = useState("Analyzing query & retrieving context...");
  const [error, setError] = useState<string | null>(null);
  
  // Suggested questions from API
  const [suggested, setSuggested] = useState<{ id: string; question: string }[]>([]);
  
  // Active document citation artifact to show on the right panel
  const [activeArtifact, setActiveArtifact] = useState<Citation | null>(null);
  
  // Model selector state
  const [modelSelect, setModelSelect] = useState("Gemini 2.5 Flash");
  const [showModelMenu, setShowModelMenu] = useState(false);
  
  // Sidebar state (mobile view toggle)
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [copiedArtifact, setCopiedArtifact] = useState(false);

  // File upload local state
  const [attachedFile, setAttachedFile] = useState<AttachedFile | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Native Speech-to-Text state
  const [recognizing, setRecognizing] = useState(false);
  const recognitionRef = useRef<any>(null);

  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

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

  // Load conversations from local storage
  useEffect(() => {
    const saved = localStorage.getItem("ijaike_conversations");
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (parsed.length > 0) {
          setConversations(parsed);
          setActiveId(parsed[0].id);
        } else {
          startNewChat(false);
        }
      } catch {
        startNewChat(false);
      }
    } else {
      startNewChat(false);
    }

    // Fetch suggested questions
    api
      .getSuggestedQuestions()
      .then(setSuggested)
      .catch(() =>
        setSuggested([
          { id: "1", question: "What are the formatting requirements for IJAIKE submissions?" },
          { id: "2", question: "What documents do I need to submit with my paper?" },
          { id: "3", question: "How are Article Processing Charges calculated?" },
          { id: "4", question: "Are there APC discounts or waivers available?" },
          { id: "5", question: "Where do I submit my manuscript?" },
          { id: "6", question: "How does the double-blind review process work?" },
        ]),
      );
  }, []);

  // Dynamically set body background and overscroll behavior to match the dark theme and prevent drag-down
  useEffect(() => {
    const originalBodyBg = document.body.style.backgroundColor;
    const originalBodyOverscroll = document.body.style.overscrollBehavior;
    const originalHtmlOverscroll = document.documentElement.style.overscrollBehavior;
    const originalBodyOverflow = document.body.style.overflow;
    const originalHtmlOverflow = document.documentElement.style.overflow;
    const originalBodyHeight = document.body.style.height;
    const originalHtmlHeight = document.documentElement.style.height;

    document.body.style.backgroundColor = "#1b1a17";
    document.body.style.overscrollBehavior = "none";
    document.documentElement.style.overscrollBehavior = "none";
    document.body.style.overflow = "hidden";
    document.documentElement.style.overflow = "hidden";
    document.body.style.height = "100%";
    document.documentElement.style.height = "100%";

    return () => {
      document.body.style.backgroundColor = originalBodyBg;
      document.body.style.overscrollBehavior = originalBodyOverscroll;
      document.documentElement.style.overscrollBehavior = originalHtmlOverscroll;
      document.body.style.overflow = originalBodyOverflow;
      document.documentElement.style.overflow = originalHtmlOverflow;
      document.body.style.height = originalBodyHeight;
      document.documentElement.style.height = originalHtmlHeight;
    };
  }, []);

  // Sync conversations to local storage
  const saveConversations = (updated: Conversation[]) => {
    setConversations(updated);
    localStorage.setItem("ijaike_conversations", JSON.stringify(updated));
  };

  // Create a new conversation
  const startNewChat = (shouldSelect = true) => {
    const newChat: Conversation = {
      id: crypto.randomUUID(),
      title: "New Chat",
      messages: [],
      created_at: new Date().toISOString(),
    };
    
    const updated = [newChat, ...conversations];
    saveConversations(updated);
    if (shouldSelect || !activeId) {
      setActiveId(newChat.id);
    }
    setActiveArtifact(null);
    setAttachedFile(null);
  };

  // Delete conversation
  const deleteConversation = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();
    const updated = conversations.filter((c) => c.id !== id);
    saveConversations(updated);
    
    if (activeId === id) {
      if (updated.length > 0) {
        setActiveId(updated[0].id);
      } else {
        const fallback: Conversation = {
          id: crypto.randomUUID(),
          title: "New Chat",
          messages: [],
          created_at: new Date().toISOString(),
        };
        saveConversations([fallback]);
        setActiveId(fallback.id);
      }
      setActiveArtifact(null);
      setAttachedFile(null);
    }
  };

  // Get active messages
  const activeConversation = conversations.find((c) => c.id === activeId);
  const messages = activeConversation ? activeConversation.messages : [];

  // Scroll to bottom on updates
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  // Handle textarea autosize description
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  // Handle local File Selection
  const handleFileClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const fileType = file.name.split('.').pop() || "txt";
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
    e.target.value = ""; // Clear so same file can be loaded again
  };

  // Web Speech-to-Text trigger
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

    rec.onstart = () => {
      setRecognizing(true);
    };

    rec.onerror = (e: any) => {
      console.error(e);
      setRecognizing(false);
    };

    rec.onend = () => {
      setRecognizing(false);
    };

    rec.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      if (transcript) {
        setInput(prev => prev ? prev + " " + transcript : transcript);
      }
    };

    recognitionRef.current = rec;
    rec.start();
  };

  const send = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if ((!trimmed && !attachedFile) || sending || !activeId) return;

      setSending(true);
      setError(null);
      setInput("");

      // User Message with File attached locally if any
      const userMsg = makeMessage("user", trimmed, null, attachedFile);
      const updatedMessages = [...messages, userMsg];
      
      const promptContext = trimmed + (attachedFile 
        ? `\n\n[Local Reference File: ${attachedFile.name}]\n${attachedFile.content}` 
        : "");

      setAttachedFile(null); // Reset attachment

      // Update local conversation state in real-time
      const updatedConversations = conversations.map((c) => {
        if (c.id === activeId) {
          const defaultText = trimmed || `Uploaded file ${userMsg.attachedFile?.name}`;
          const newTitle = c.title === "New Chat" ? (defaultText.slice(0, 32) + (defaultText.length > 32 ? "..." : "")) : c.title;
          return {
            ...c,
            title: newTitle,
            messages: updatedMessages,
          };
        }
        return c;
      });
      saveConversations(updatedConversations);

      try {
        const history = messages.slice(-10).map((m) => ({
          role: m.role,
          content: m.content,
        }));

        const res = await api.askPublic(promptContext, history);
        const assistantMsg = makeMessage("assistant", res.answer, res.citations);
        
        const finalMessages = [...updatedMessages, assistantMsg];
        const finalConversations = updatedConversations.map((c) => {
          if (c.id === activeId) {
            return {
              ...c,
              messages: finalMessages,
              model_used: res.model_used || undefined,
            };
          }
          return c;
        });
        saveConversations(finalConversations);
      } catch (e) {
        setError(
          e instanceof Error
            ? e.message
            : "Could not reach the chatbot API. Start the backend on port 8000.",
        );
      } finally {
        setSending(false);
      }
    },
    [sending, messages, activeId, conversations, attachedFile],
  );

  // Formatting output JSON for artifact sidebar
  const getFormattedArtifact = (art: Citation) => {
    const hasVector = art.embedding && Array.isArray(art.embedding);
    const vectorDim = hasVector ? art.embedding!.length : 0;
    const vectorPreview = hasVector 
      ? [...art.embedding!.slice(0, 35), `... [truncated, total ${vectorDim} dimensions]`].map(v => 
          typeof v === "number" ? parseFloat(v.toFixed(6)) : v
        )
      : "No embedding vector retrieved from fallback data.";

    return {
      source_document: art.document_title,
      chunk_id: art.chunk_id || "N/A",
      relevance_score: art.relevance_score || 0,
      match_percentage: art.relevance_score ? `${Math.round(art.relevance_score * 100)}%` : "N/A",
      page_number: art.page_number || "N/A",
      section_title: art.section || "N/A",
      vector_store_config: {
        provider: "ChromaDB",
        space_type: "cosine distance",
        total_dimensions: vectorDim || 768,
      },
      extracted_excerpt: art.excerpt || "",
      chromadb_embedding_values: vectorPreview
    };
  };

  const handleCopyArtifact = () => {
    if (!activeArtifact) return;
    const jsonStr = JSON.stringify(getFormattedArtifact(activeArtifact), null, 2);
    navigator.clipboard.writeText(jsonStr);
    setCopiedArtifact(true);
    setTimeout(() => setCopiedArtifact(false), 2000);
  };

  return (
    <div className="flex h-screen w-full bg-[#1b1a17] text-neutral-350 font-sans antialiased overflow-hidden select-none">
      {/* Invisible file input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
        accept=".txt,.md,.js,.py,.json,.csv,.ts,.tsx,.css,.html"
      />

      {/* 1. Left Sidebar (Recent Chats) */}
      {sidebarOpen && (
        <aside className="w-64 flex flex-col bg-[#191919] border-r border-white/5 text-white/95 shrink-0 z-40 transition-all duration-300">
          {/* Header */}
          <div className="p-4 border-b border-white/5 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2">
              <div className="flex h-7 w-7 items-center justify-center rounded-full border-2 border-[#d4a843] text-sm font-bold text-[#d4a843]">
                J
              </div>
              <span className="font-semibold tracking-wide text-white">JAIKE Chat</span>
            </Link>
            <button
              onClick={() => setSidebarOpen(false)}
              className="text-neutral-400 hover:text-white lg:hidden"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* New Chat Button */}
          <div className="p-3">
            <button
              onClick={() => startNewChat()}
              className="w-full flex items-center justify-center gap-2 border border-white/10 hover:border-white/20 hover:bg-white/5 rounded-lg py-2 text-sm text-neutral-300 font-medium transition"
            >
              <span className="text-lg font-light leading-none">+</span>
              New Chat
            </button>
          </div>

          {/* Recents list */}
          <div className="flex-1 overflow-y-auto px-2 space-y-1 select-none">
            <p className="px-3 py-2 text-[10px] font-semibold text-neutral-500 uppercase tracking-widest">
              Recent Chats
            </p>
            {conversations.map((c) => (
              <button
                key={c.id}
                onClick={() => {
                  setActiveId(c.id);
                  setActiveArtifact(null);
                }}
                className={`w-full group text-left px-3 py-2 rounded-lg text-sm transition flex items-center justify-between ${
                  activeId === c.id
                    ? "bg-[#2b2a27] text-white font-medium"
                    : "text-neutral-400 hover:bg-white/5 hover:text-neutral-200"
                }`}
              >
                <span className="truncate flex-1 pr-2">{c.title || "New Chat"}</span>
                <span
                  onClick={(e) => deleteConversation(c.id, e)}
                  className="opacity-0 group-hover:opacity-100 hover:text-red-400 text-neutral-400 p-0.5"
                  title="Delete chat"
                >
                  <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </span>
              </button>
            ))}
          </div>

          {/* Footer User Info */}
          <div className="p-4 border-t border-white/5 flex items-center justify-between bg-[#141414]">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-full bg-[#d4a843]/20 flex items-center justify-center text-[#d4a843] font-bold text-sm">
                U
              </div>
              <div className="text-left leading-tight">
                <p className="text-xs font-semibold text-white">Free Guest</p>
                <p className="text-[10px] text-neutral-500">Free Tier Plan</p>
              </div>
            </div>
            <Link
              href="/login"
              className="text-[10px] text-[#d4a843] border border-[#d4a843]/40 hover:bg-[#d4a843]/10 px-2 py-1 rounded"
            >
              Sign In
            </Link>
          </div>
        </aside>
      )}

      {/* 2. Main Chat Panel */}
      <div className="flex-1 flex flex-col h-full bg-[#1b1a17] overflow-hidden relative">
        {/* Main Header */}
        <header className="h-14 border-b border-white/5 px-4 flex items-center justify-between text-white shrink-0 z-30 bg-[#1b1a17] select-none">
          <div className="flex items-center gap-2">
            {!sidebarOpen && (
              <button
                onClick={() => setSidebarOpen(true)}
                className="text-neutral-400 hover:text-white mr-2"
                title="Open sidebar"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            )}
            <h2 className="text-sm font-medium truncate max-w-xs md:max-w-md">
              {activeConversation?.title || "JAIKE Assistant"}
            </h2>
          </div>

          {/* Model Selector Button */}
          <div className="relative">
            <button
              onClick={() => setShowModelMenu(!showModelMenu)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#272623] hover:bg-[#32312d] text-xs text-neutral-300 transition"
            >
              <span>{modelSelect}</span>
              <svg className="h-3 w-3 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {showModelMenu && (
              <div className="absolute right-0 top-full mt-2 w-48 bg-[#1e1d1a] border border-white/10 rounded-lg shadow-xl py-1.5 z-55">
                {[
                  "Gemini 2.5 Flash",
                  "Gemini 2.5 Pro",
                  "Claude 3.5 Sonnet",
                  "Deep Research",
                ].map((model) => (
                  <button
                    key={model}
                    onClick={() => {
                      setModelSelect(model);
                      setShowModelMenu(false);
                    }}
                    className={`w-full text-left px-4 py-2 text-xs transition ${
                      modelSelect === model
                        ? "text-[#d4a843] bg-white/5 font-semibold"
                        : "text-neutral-300 hover:bg-white/5 hover:text-white"
                    }`}
                  >
                    {model}
                  </button>
                ))}
              </div>
            )}
          </div>
        </header>

        {/* Messages Feed Container — pb-40 provides padding for floating bottom input */}
        <div className="flex-1 overflow-y-auto px-4 pt-8 pb-40 relative">
          <div className="mx-auto max-w-2xl space-y-6">
            {messages.length === 0 ? (
              <div className="text-center pt-8 pb-4">
                {/* JAIKE Logo */}
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full border-4 border-[#d4a843]/80 text-2xl font-bold text-[#d4a843] mb-4 bg-[#d4a843]/5">
                  J
                </div>
                <h1 className="text-2xl font-medium text-white mb-2">
                  What can I help you with?
                </h1>
                <p className="text-sm text-neutral-400 max-w-md mx-auto mb-6">
                  Ask anything about the journal, formatting guidelines, submission procedure, publication, or article processing charges.
                </p>

                {/* Suggested Questions */}
                <div className="space-y-2 mt-4 max-w-xl mx-auto">
                  <p className="text-left text-xs font-semibold text-neutral-500 uppercase tracking-widest mb-3 px-1">
                    Suggested questions
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {suggested.map((q) => (
                      <button
                        key={q.id}
                        onClick={() => send(q.question)}
                        className="p-3 text-left text-xs rounded-xl bg-[#272623] hover:bg-[#32312d] transition border border-[#ffffff04] hover:border-white/5 text-neutral-300 hover:text-white"
                      >
                        {q.question}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="mt-8 flex justify-center gap-4 text-xs font-medium text-neutral-400">
                  <Link href="/apc" className="text-[#d4a843] hover:underline">
                    APC Estimator →
                  </Link>
                  <Link href="/resources" className="hover:text-white">
                    Browse All Guidelines →
                  </Link>
                  <a
                    href="https://mc04.manuscriptcentral.com/jaike"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-white"
                  >
                    Submit Manuscript →
                  </a>
                </div>
              </div>
            ) : (
              <div className="space-y-6 select-text">
                {messages.map((m, idx) => {
                  const isUser = m.role === "user";
                  const customMsg = m as Message & { attachedFile?: AttachedFile | null };
                  const userQuery = !isUser && idx > 0 ? messages[idx - 1].content : "";
                  const suggestedLinks = !isUser ? getSuggestedLinks(m.content, userQuery) : [];


                  return (
                    <div
                      key={m.id}
                      className={`flex gap-4 ${isUser ? "justify-end" : "justify-start"}`}
                    >
                      {/* Avatar for assistant */}
                      {!isUser && (
                        <div className="h-7 w-7 rounded-full border border-[#d4a843]/60 bg-[#d4a843]/10 text-[#d4a843] font-bold text-xs flex items-center justify-center shrink-0 select-none">
                          J
                        </div>
                      )}

                      <div className={`max-w-[85%] text-left ${isUser ? "text-right" : ""}`}>
                        {isUser ? (
                          // User Bubble
                          <div className="space-y-1.5 inline-block text-left">
                            {/* Render local attached file preview in users bubble if uploaded */}
                            {customMsg.attachedFile && (
                              <div className="flex items-center gap-2 bg-[#2b2a27]/90 border border-white/5 rounded-xl px-3 py-1.5 text-xs text-neutral-300 max-w-sm mb-1 ml-auto">
                                <span className="p-1 rounded bg-[#d4a843]/20 text-[#d4a843] font-mono text-[9px] font-bold">
                                  {customMsg.attachedFile.type.toUpperCase()}
                                </span>
                                <span className="truncate text-white font-medium text-[10px] max-w-[150px]">
                                  {customMsg.attachedFile.name}
                                </span>
                                <span className="text-[9px] text-neutral-400">
                                  ({(customMsg.attachedFile.size / 1024).toFixed(1)} KB)
                                </span>
                              </div>
                            )}

                            {m.content && (
                              <div className="rounded-2xl px-4 py-2.5 text-sm leading-relaxed bg-[#2b2a27] text-white/95">
                                {m.content}
                              </div>
                            )}
                          </div>
                        ) : (
                          // Assistant content (rendered via ReactMarkdown viewer)
                          <div className="space-y-3">
                            <div className="text-[#e2e2e2] leading-relaxed text-sm pr-2">
                              <ReactMarkdown
                                remarkPlugins={[remarkGfm]}
                                components={{
                                  p: ({ children }) => <p className="mb-3 leading-relaxed text-neutral-200 text-sm">{children}</p>,
                                  strong: ({ children }) => <strong className="font-bold text-white">{children}</strong>,
                                  em: ({ children }) => <em className="italic text-white/90">{children}</em>,
                                  ul: ({ children }) => <ul className="list-disc pl-5 my-2.5 space-y-1.5 text-neutral-300 text-sm">{children}</ul>,
                                  ol: ({ children }) => <ol className="list-decimal pl-5 my-2.5 space-y-1.5 text-neutral-300 text-sm">{children}</ol>,
                                  li: ({ children }) => <li className="mb-0.5">{children}</li>,
                                  h1: ({ children }) => <h1 className="text-xl font-bold mt-5 mb-2.5 text-white">{children}</h1>,
                                  h2: ({ children }) => <h2 className="text-lg font-bold mt-4.5 mb-2 text-white">{children}</h2>,
                                  h3: ({ children }) => <h3 className="text-base font-bold mt-4 mb-2 text-white">{children}</h3>,
                                  code: (props) => {
                                    const { children, className, ...rest } = props;
                                    const isInline = !className;
                                    if (isInline) {
                                      return (
                                        <code className="bg-white/10 rounded px-1.5 py-0.5 text-xs font-mono text-[#d4a843]" {...rest}>
                                          {children}
                                        </code>
                                      );
                                    }
                                    return (
                                      <pre className="bg-black/35 border border-white/5 p-3 rounded-lg text-xs font-mono my-3 overflow-x-auto text-[#d4a843]">
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
                            </div>

                            {/* References section */}
                            {m.citations && m.citations.length > 0 && (
                              <div className="mt-4 pt-3 border-t border-white/5 select-none">
                                <p className="text-[10px] font-semibold text-neutral-500 uppercase tracking-widest mb-2">
                                  References &amp; Resources
                                </p>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                  {m.citations.slice(0, 4).map((c, i) => {
                                    const liveUrl = getDocUrl(c.document_title);
                                    return (
                                      <a
                                        key={i}
                                        href={liveUrl}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="flex items-center justify-between p-3 rounded-lg bg-[#272623] hover:bg-[#32312d] border border-white/5 hover:border-[#d4a843]/20 transition group"
                                      >
                                        <div className="flex items-center gap-3">
                                          <div className="p-2 rounded bg-[#d4a843]/15 text-[#d4a843] text-xs font-serif font-bold">
                                            📖
                                          </div>
                                          <div className="text-left">
                                            <p className="text-xs font-medium text-white group-hover:text-[#d4a843] transition">
                                              {c.document_title.replace("IJAIKE — ", "")}
                                            </p>
                                            <p className="text-[10px] text-neutral-400">
                                              Official IJAIKE Journal Page
                                            </p>
                                          </div>
                                        </div>
                                        <span className="text-[10.5px] font-semibold text-[#d4a843] group-hover:underline pl-3 whitespace-nowrap">
                                          Open Page ↗
                                        </span>
                                      </a>
                                    );
                                  })}
                                </div>
                              </div>
                            )}
                            {/* Suggested Reference Links */}
                            {suggestedLinks.length > 0 && (
                              <div className="mt-3 pt-2 border-t border-white/5 select-none">
                                <p className="text-[9px] font-semibold text-neutral-500 uppercase tracking-widest mb-1.5">
                                  Suggested Links
                                </p>
                                <div className="flex flex-wrap gap-2">
                                  {suggestedLinks.map((link, i) => (
                                    <a
                                      key={i}
                                      href={link.url}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#272623] hover:bg-[#32312d] border border-white/5 hover:border-[#d4a843]/30 transition text-xs text-neutral-300 hover:text-white"
                                    >
                                      <span>🔗 {link.label}</span>
                                    </a>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>

                        )}
                      </div>
                    </div>
                  );
                })}

                {/* Loading Bubble */}
                {sending && (
                  <div className="flex gap-4 justify-start">
                    <div className="h-7 w-7 rounded-full border border-[#d4a843]/60 bg-[#d4a843]/10 text-[#d4a843] font-bold text-xs flex items-center justify-center shrink-0 animate-pulse">
                      J
                    </div>
                    <div className="rounded-lg bg-white/5 border border-white/5 px-4 py-2 text-xs text-neutral-400 flex items-center gap-2">
                      <svg className="animate-spin h-3.5 w-3.5 text-[#d4a843]" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <span>{thinkingStatus}</span>
                    </div>
                  </div>
                )}
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        </div>

        {/* 3. Fully Active Floating User Input Field (Bottom Offset) */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 w-full max-w-2xl px-4 z-40 select-none">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              send(input);
            }}
            className="flex flex-col p-2.5 rounded-2xl bg-[#272623] border border-white/10 focus-within:border-white/20 transition-all shadow-2xl shadow-black/80"
          >
            {/* Render file attachment card IF uploaded */}
            {attachedFile && (
              <div className="flex items-center gap-2 bg-[#1b1a17] border border-white/5 rounded-lg px-3 py-1.5 self-start text-xs max-w-sm mb-2">
                <div className="p-1 px-1.5 rounded bg-[#d4a843]/15 text-[#d4a843] font-bold font-mono text-[9px]">
                  {attachedFile.type.toUpperCase()}
                </div>
                <div className="flex-1 min-w-0 text-left">
                  <p className="text-white font-medium truncate text-[10px] max-w-[180px]">{attachedFile.name}</p>
                  <p className="text-[9px] text-neutral-400">{(attachedFile.size / 1024).toFixed(1)} KB</p>
                </div>
                <button
                  type="button"
                  onClick={() => setAttachedFile(null)}
                  className="text-neutral-400 hover:text-red-400 p-0.5 ml-2"
                >
                  <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            )}

            {/* Input textarea */}
            <textarea
              ref={textareaRef}
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask JAIKE Assistant..."
              disabled={sending}
              className="w-full bg-transparent text-sm text-white outline-none resize-none px-2 pt-2 min-h-[36px] max-h-[160px] leading-relaxed"
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  send(input);
                }
              }}
            />

            {/* Bottom Row Tool Buttons (Dynamic Actions!) */}
            <div className="flex items-center justify-between pt-2 px-1">
              <div className="flex items-center gap-1.5 text-neutral-400">
                {/* 1. Add Attachment Plus — Fully Functional! */}
                <button
                  type="button"
                  onClick={handleFileClick}
                  className="p-1.5 rounded-lg hover:bg-white/5 hover:text-white transition"
                  title="Attach text/code file context"
                >
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                </button>

                {/* 2. Mic Speech Input — Fully Functional Voice Transcription! */}
                <button
                  type="button"
                  onClick={runVoiceInput}
                  className={`p-1.5 rounded-lg transition ${
                    recognizing 
                      ? "bg-red-500/20 text-red-500 animate-pulse border border-red-500/30" 
                      : "hover:bg-white/5 hover:text-white"
                  }`}
                  title={recognizing ? "Listening... click to stop" : "Speech voice input"}
                >
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                  </svg>
                </button>
              </div>

              {/* Submit button */}
              <button
                type="submit"
                disabled={sending || (!input.trim() && !attachedFile)}
                className="p-1.5 rounded-full bg-[#d4a843] hover:bg-[#c49738] disabled:opacity-35 text-[#0a1628] transition duration-200"
              >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </button>
            </div>
          </form>
          {error && (
            <p className="mt-2 text-center text-xs text-red-400 leading-tight bg-[#272623]/80 p-1.5 rounded-md border border-red-500/10">
              {error}
            </p>
          )}
          <p className="mt-1.5 text-center text-[9px] text-neutral-500 select-none">
            JAIKE Chatbot can make mistakes. Verify documents, metadata, and embeddings before using.
          </p>
        </div>
      </div>


    </div>
  );
}
