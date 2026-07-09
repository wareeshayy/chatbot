"use client";

import { CitationList } from "./CitationList";
import type { Message } from "@/lib/types";

export function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-sm px-4 py-3 text-sm leading-relaxed shadow-sm ${
          isUser
            ? "rounded-br-none bg-[#0a1628] text-white"
            : "rounded-bl-none border border-slate-200 bg-white text-slate-800"
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        {!isUser && message.citations && message.citations.length > 0 && (
          <CitationList citations={message.citations} />
        )}
      </div>
    </div>
  );
}
